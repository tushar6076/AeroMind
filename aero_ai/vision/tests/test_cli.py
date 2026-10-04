import pytest
from aero_vision_ai.cli import _parser


def test_cli_parser():
    parser = _parser()
    args = parser.parse_args(["validate"])
    assert args.command == "validate"