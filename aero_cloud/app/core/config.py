from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "AeroMind Edge"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8100
    DEBUG: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TELEMETRY_TTL_SECONDS: int = Field(default=10, ge=1)
    REDIS_FLIGHT_STATE_TTL_SECONDS: int = Field(default=86_400, ge=1)
    REDIS_RECONNECT_INTERVAL_SECONDS: int = Field(default=5, ge=1)
    TELEMETRY_MAX_AGE_SECONDS: int = Field(default=3, ge=1)
    API_PREFIX: str = "/api/v1"
    API_ACCESS_TOKEN: str | None = None
    ELRS_SERIAL_PORT: str | None = None
    ELRS_BAUD_RATE: int = 420_000
    ELRS_ARM_CHANNEL: int | None = Field(default=None, ge=5, le=16)
    ELRS_ARMED_CHANNEL_VALUE: int = Field(default=1811, ge=172, le=1811)
    VIDEO_INPUT_DEVICE: str | None = None
    VIDEO_WIDTH: int = 1280
    VIDEO_HEIGHT: int = 720
    VIDEO_FRAME_RATE: int = 30
    HOST_THERMAL_PATH: str = "/sys/class/thermal/thermal_zone0/temp"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()