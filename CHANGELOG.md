# Changelog

## v1.1.0 - 2026-06-26

Initial public release of the improved Reality SNI Smart Scanner.

### Added

- Non-interactive CLI mode with `scan`, `self-test`, and `menu` commands.
- Multi-IP probing per domain via `--max-ips`.
- JSON output next to CSV output.
- Optional raw per-attempt probe CSV via `--raw`.
- `reality_grade` field for quick A-F candidate quality classification.
- `tested_ips` and `tested_ip_count` fields.
- Summary output with OK/failed counts and grade distribution.
- Safer manual input parsing for interactive mode.

### Changed

- Single-network scoring now includes reputation adjustment.
- Printed scan rows include selected IP and REALITY grade.
- Shared analysis exports JSON as well as CSV.

### Notes

- The scanner is a candidate discovery tool. Always validate final SNI choices with your actual Xray REALITY configuration and target networks.
