from pathlib import Path

from aero_ai.cli import DEFAULT_CONFIG, _parser


def test_default_config_is_bundled_with_package() -> None:
    assert DEFAULT_CONFIG.is_file()


def test_config_option_works_before_or_after_command() -> None:
    custom_config = Path("custom.yaml")

    before_command = _parser().parse_args(["--config", str(custom_config), "train"])
    after_command = _parser().parse_args(["train", "--config", str(custom_config)])

    assert before_command.config == str(custom_config)
    assert after_command.config == str(custom_config)


def test_subcommand_uses_bundled_config_by_default() -> None:
    args = _parser().parse_args(["train"])

    assert args.config == str(DEFAULT_CONFIG)
