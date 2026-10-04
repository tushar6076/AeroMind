from aero_autonomy_ai.cli import _parser


def test_autonomy_parser():
    parser = _parser()
    args = parser.parse_args(["train"])
    assert args.command == "train"