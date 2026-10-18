import io
import logging
import re
from pathlib import Path
import threading
from typing import Any, Literal
import warnings

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.core.config import settings
from app.schemas.ai import (
    AIInferenceResult,
    AIInventory,
    AIModelSummary,
    AIStagePrediction,
)

logger = logging.getLogger(__name__)


class AIImageError(ValueError):
    """The uploaded image is invalid or outside the supported input contract."""


class AIInferenceUnavailable(RuntimeError):
    """The model runtime or a required model artifact is unavailable."""


class ModelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tensor_shape: list[int] = Field(min_length=4, max_length=4)
    color_order: str = "RGB"
    value_range: list[float] = Field(min_length=2, max_length=2)

    @model_validator(mode="after")
    def validate_image_tensor(self) -> "ModelInput":
        if self.tensor_shape[0] != 1 or self.tensor_shape[1] != 3:
            raise ValueError("Image tensors must use shape [1, 3, height, width]")
        if any(dimension < 1 for dimension in self.tensor_shape):
            raise ValueError("Image tensor dimensions must be positive")
        if self.color_order != "RGB":
            raise ValueError("Only RGB image tensors are supported")
        if self.value_range[0] >= self.value_range[1]:
            raise ValueError("value_range must be increasing")
        return self


class ModelStage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    name: str = Field(min_length=1)
    artifact: str = Field(min_length=1)
    task: str = Field(min_length=1)
    labels: list[str] = Field(min_length=1)
    when: dict[str, list[str]] | None = None

    @model_validator(mode="after")
    def validate_condition(self) -> "ModelStage":
        if self.when is not None and len(self.when) != 1:
            raise ValueError("when must name exactly one preceding stage")
        return self


class MissionMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(ge=1, le=1)
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    description: str = Field(min_length=1)
    task: str = Field(min_length=1)
    router_label: str = Field(min_length=1)
    input: ModelInput
    stages: list[ModelStage] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_stage_references(self) -> "MissionMetadata":
        stage_ids = [stage.id for stage in self.stages]
        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError("Stage ids must be unique")
        prior_stages: dict[str, set[str]] = {}
        for stage in self.stages:
            if stage.when is not None:
                previous_id, labels = next(iter(stage.when.items()))
                if previous_id not in prior_stages:
                    raise ValueError("Stage conditions must reference a preceding stage")
                if not set(labels).issubset(prior_stages[previous_id]):
                    raise ValueError("Stage condition contains an unknown label")
            prior_stages[stage.id] = set(stage.labels)
        return self


class RouterMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(ge=1, le=1)
    artifact: str = Field(min_length=1)
    runtime: Literal["torchscript"] = "torchscript"
    input: ModelInput
    labels: list[str] = Field(min_length=1)
    missions: dict[str, str]

    @model_validator(mode="after")
    def validate_mission_labels(self) -> "RouterMetadata":
        if set(self.labels) != set(self.missions):
            raise ValueError("Every router label must map to exactly one mission")
        return self


class AIService:
    def __init__(self, models_dir: Path | None = None) -> None:
        self._models_dir = (
            models_dir if models_dir is not None else settings.AI_MODELS_DIR
        )
        self._model_cache: dict[Path, tuple[int, int, object]] = {}
        self._model_cache_lock = threading.Lock()

    def inventory(self) -> AIInventory:
        router, router_status = self._load_router()
        models = self._discover_missions(router)
        return AIInventory(
            mode="missions",
            note=(
                "Missions are discovered from model metadata and support "
                "image inference when their weights are available."
            ),
            router_status=router_status,
            models=models,
        )

    def infer(self, image_bytes: bytes, media_type: str) -> AIInferenceResult:
        try:
            import torch
        except ImportError as error:
            raise AIInferenceUnavailable(
                "PyTorch is not installed in the Aero Cloud runtime."
            ) from error

        router, router_status = self._load_router()
        if router is None:
            raise AIInferenceUnavailable(
                f"Mission router is unavailable: {router_status}."
            )

        router_path = self._resolve_artifact(self._models_dir, router.artifact)
        if not router_path.is_file():
            raise AIInferenceUnavailable("Mission router weights are missing.")

        router_tensor = self._prepare_image_tensor(
            image_bytes,
            media_type,
            router.input,
            torch,
        )
        router_scores = self._run_classifier(
            router_path,
            router_tensor,
            router.labels,
            torch,
        )
        router_index = int(router_scores.argmax(dim=1).item())
        router_label = router.labels[router_index]
        router_confidence = float(router_scores[0, router_index].item())
        mission_id = router.missions.get(router_label)
        if mission_id is None:
            raise AIInferenceUnavailable(
                f"Router output label {router_label!r} has no mission mapping."
            )

        mission_dir = self._models_dir / mission_id
        if mission_dir.is_symlink() or not mission_dir.is_dir():
            raise AIInferenceUnavailable(
                f"Mission directory for {mission_id!r} is unavailable."
            )
        metadata_path = mission_dir / "metadata.json"
        try:
            mission = MissionMetadata.model_validate_json(metadata_path.read_text())
        except (OSError, ValidationError) as error:
            raise AIInferenceUnavailable(
                f"Mission metadata for {mission_id!r} is invalid or missing."
            ) from error
        if mission.id != mission_id or mission.router_label != router_label:
            raise AIInferenceUnavailable(
                f"Mission metadata for {mission_id!r} does not match the router."
            )

        previous_predictions: dict[str, str] = {}
        stage_predictions = []
        for stage in mission.stages:
            if stage.when is not None:
                previous_id, allowed_labels = next(iter(stage.when.items()))
                if previous_predictions.get(previous_id) not in allowed_labels:
                    stage_predictions.append(
                        AIStagePrediction(
                            stage_id=stage.id,
                            stage_name=stage.name,
                            task=stage.task,
                            status="skipped",
                        )
                    )
                    continue

            stage_path = self._resolve_artifact(mission_dir, stage.artifact)
            if not stage_path.is_file():
                raise AIInferenceUnavailable(
                    f"Model weights are missing for stage {stage.id!r}."
                )
            stage_tensor = self._prepare_image_tensor(
                image_bytes,
                media_type,
                mission.input,
                torch,
            )
            scores = self._run_classifier(
                stage_path,
                stage_tensor,
                stage.labels,
                torch,
            )
            predicted_index = int(scores.argmax(dim=1).item())
            label = stage.labels[predicted_index]
            previous_predictions[stage.id] = label
            stage_predictions.append(
                AIStagePrediction(
                    stage_id=stage.id,
                    stage_name=stage.name,
                    task=stage.task,
                    status="predicted",
                    label=label,
                    confidence=float(scores[0, predicted_index].item()),
                )
            )

        return AIInferenceResult(
            mission_id=mission.id,
            mission_name=mission.name,
            router_label=router_label,
            router_confidence=router_confidence,
            stages=stage_predictions,
        )

    @staticmethod
    def _prepare_image_tensor(
        image_bytes: bytes,
        media_type: str,
        model_input: ModelInput,
        torch: Any,
    ) -> Any:
        from PIL import Image, ImageOps, UnidentifiedImageError

        expected_formats = {
            "image/jpeg": {"JPEG"},
            "image/png": {"PNG"},
            "image/webp": {"WEBP"},
        }
        if media_type not in expected_formats:
            raise AIImageError("Only JPEG, PNG, and WebP images are supported.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(image_bytes)) as source:
                    if source.format not in expected_formats[media_type]:
                        raise AIImageError(
                            "Image bytes do not match the declared content type."
                        )
                    width, height = source.size
                    if width < 1 or height < 1:
                        raise AIImageError("Image dimensions must be positive.")
                    if width * height > settings.AI_MAX_IMAGE_PIXELS:
                        raise AIImageError(
                            "Image exceeds the configured pixel limit."
                        )
                    source.load()
                    image = ImageOps.exif_transpose(source).convert("RGB")
            target_height, target_width = model_input.tensor_shape[2:]
            image = image.resize(
                (target_width, target_height),
                resample=Image.Resampling.BILINEAR,
            )
        except AIImageError:
            raise
        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
        ) as error:
            raise AIImageError("Unable to decode a safe image from the request.") from error

        tensor = torch.frombuffer(
            bytearray(image.tobytes()),
            dtype=torch.uint8,
        )
        tensor = tensor.reshape(target_height, target_width, 3)
        tensor = tensor.permute(2, 0, 1).unsqueeze(0).to(dtype=torch.float32)
        minimum, maximum = model_input.value_range
        return tensor.div(255.0).mul(maximum - minimum).add(minimum)

    def _run_classifier(
        self,
        artifact: Path,
        image_tensor: Any,
        labels: list[str],
        torch: Any,
    ) -> Any:
        model = self._load_model(artifact, torch)
        try:
            with torch.inference_mode():
                logits = model(image_tensor)
                if not isinstance(logits, torch.Tensor):
                    raise AIInferenceUnavailable(
                        f"Model {artifact.name!r} must return a score tensor."
                    )
                if tuple(logits.shape) != (1, len(labels)):
                    raise AIInferenceUnavailable(
                        f"Model {artifact.name!r} returned {tuple(logits.shape)} "
                        f"scores; expected (1, {len(labels)})."
                    )
                if not bool(torch.isfinite(logits).all().item()):
                    raise AIInferenceUnavailable(
                        f"Model {artifact.name!r} returned non-finite scores."
                    )
                return torch.softmax(logits.to(dtype=torch.float32), dim=1)
        except AIInferenceUnavailable:
            raise
        except (RuntimeError, ValueError) as error:
            logger.exception("TorchScript model execution failed: %s", artifact.name)
            raise AIInferenceUnavailable(
                f"Model {artifact.name!r} failed during inference."
            ) from error

    def _load_model(self, artifact: Path, torch: Any) -> Any:
        try:
            stat = artifact.stat()
        except OSError as error:
            raise AIInferenceUnavailable(
                f"Model artifact {artifact.name!r} is unavailable."
            ) from error
        signature = (stat.st_mtime_ns, stat.st_size)
        with self._model_cache_lock:
            cached = self._model_cache.get(artifact)
            if cached is not None and cached[:2] == signature:
                return cached[2]
            try:
                model = torch.jit.load(str(artifact), map_location="cpu")
                model.eval()
            except (OSError, RuntimeError, ValueError) as error:
                logger.exception("Unable to load TorchScript model: %s", artifact.name)
                raise AIInferenceUnavailable(
                    f"Model artifact {artifact.name!r} is not a valid TorchScript model."
                ) from error
            self._model_cache[artifact] = (*signature, model)
            return model

    def _load_router(self) -> tuple[RouterMetadata | None, str]:
        router_path = self._models_dir / "router.json"
        try:
            router = RouterMetadata.model_validate_json(router_path.read_text())
            self._resolve_artifact(self._models_dir, router.artifact)
        except FileNotFoundError:
            if not self._models_dir.is_dir():
                return None, "Models directory is missing"
            return None, "Router metadata or weights are missing"
        except (OSError, ValidationError, ValueError) as error:
            return None, f"Router configuration is invalid: {error}"

        for label, mission_id in router.missions.items():
            if not self._valid_identifier(mission_id):
                return None, f"Router mission id for {label!r} is invalid"
        router_artifact = self._resolve_artifact(self._models_dir, router.artifact)
        if not router_artifact.is_file():
            return router, "Router weights are missing"
        return router, self._artifact_status(router_artifact)

    def _discover_missions(
        self,
        router: RouterMetadata | None,
    ) -> list[AIModelSummary]:
        if not self._models_dir.is_dir():
            return []

        summaries = []
        for directory in sorted(self._models_dir.iterdir()):
            if directory.is_dir() and directory.is_symlink():
                summaries.append(
                    AIModelSummary(
                        id=directory.name,
                        name=directory.name,
                        version="unknown",
                        task="Mission metadata",
                        status="Symbolic-link mission directories are not supported",
                        stage_count=0,
                    )
                )
                continue
            if not directory.is_dir():
                continue
            metadata_path = directory / "metadata.json"
            if not metadata_path.is_file():
                continue
            summaries.append(self._mission_summary(directory, metadata_path, router))
        return summaries

    def _mission_summary(
        self,
        directory: Path,
        metadata_path: Path,
        router: RouterMetadata | None,
    ) -> AIModelSummary:
        fallback_id = directory.name
        try:
            mission = MissionMetadata.model_validate_json(metadata_path.read_text())
            if mission.id != directory.name:
                raise ValueError("Mission id must match its directory name")
            if router is None:
                status = "Router configuration is unavailable"
            elif router.missions.get(mission.router_label) != mission.id:
                status = "Router label is not mapped to this mission"
            else:
                missing = self._missing_artifacts(
                    directory, [stage.artifact for stage in mission.stages]
                )
                status = (
                    f"Missing stage weights: {', '.join(missing)}"
                    if missing
                    else self._mission_artifact_status(directory, mission)
                )
            return AIModelSummary(
                id=mission.id,
                name=mission.name,
                version=mission.version,
                task=mission.task,
                status=status,
                stage_count=len(mission.stages),
            )
        except (OSError, ValidationError, ValueError) as error:
            return AIModelSummary(
                id=fallback_id,
                name=fallback_id.replace("_", " ").replace("-", " ").title(),
                version="unknown",
                task="Mission metadata",
                status=f"Invalid metadata: {error}",
                stage_count=0,
            )

    def _missing_artifacts(self, directory: Path, artifacts: list[str]) -> list[str]:
        missing = []
        for artifact in artifacts:
            path = self._resolve_artifact(directory, artifact)
            if not path.is_file():
                missing.append(artifact)
        return missing

    def _mission_artifact_status(
        self,
        directory: Path,
        mission: MissionMetadata,
    ) -> str:
        paths = [
            self._resolve_artifact(directory, stage.artifact)
            for stage in mission.stages
        ]
        if paths and all(
            self._artifact_status(path) == "Loaded and ready" for path in paths
        ):
            return "Loaded and ready"
        return "Weights present; not yet loaded"

    def _artifact_status(self, artifact: Path) -> str:
        try:
            stat = artifact.stat()
        except OSError:
            return "Weights are unavailable"
        cached = self._model_cache.get(artifact)
        if cached is not None and cached[:2] == (stat.st_mtime_ns, stat.st_size):
            return "Loaded and ready"
        return "Weights present; not yet loaded"

    @staticmethod
    def _resolve_artifact(directory: Path, artifact: str) -> Path:
        if not artifact.strip():
            raise ValueError("Artifact path cannot be empty")
        path = (directory / artifact).resolve()
        try:
            path.relative_to(directory.resolve())
        except ValueError as error:
            raise ValueError("Artifact path must stay inside its model directory") from error
        return path

    @staticmethod
    def _valid_identifier(value: str) -> bool:
        return re.fullmatch(r"[a-z0-9][a-z0-9_-]*", value) is not None