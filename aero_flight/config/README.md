# Flight configuration

Configuration here is descriptive and board-specific. It is not automatically
flashed to the FC and must not be treated as a verified pin map.

- `boards/dys_fc722/board.yaml` records supplied DYS FC722 metadata.
- Keep target identifiers, UART assignments, channel mapping, and peripheral
  wiring marked unverified until checked against the physical board revision
  and authoritative documentation.
- Never put credentials, private keys, or local device paths in committed
  board profiles.
