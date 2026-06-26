# Reality SNI Smart Scanner

English | [فارسی](README.fa.md)

A Termux-friendly smart SNI scanner for Xray REALITY. It probes candidate domains over IPv4/443, measures DNS/TCP/TLS/HTTP timing, scores stability, and exports CSV/JSON reports.

## Features

- Interactive numeric menu for normal use
- Non-interactive CLI mode for automation and Termux scripts
- Normal and Deep scan profiles
- Multi-IP probing per domain with `--max-ips`
- CSV and JSON result files
- Optional raw per-attempt probe log with `--raw`
- Shared SNI analysis across multiple network scans
- REALITY-oriented scoring with success rate, p95, jitter, TLS 1.3 rate, and reputation adjustment
- `reality_grade` output from A to F
- Expanded built-in REALITY candidate subdomain list
- Domain categories, risk labels, HTTP status codes, and explainable `reason` output
- `--category`, `--min-grade`, and `export-domains` helpers

## Requirements

- Python 3.8+
- No third-party Python packages required
- Android Termux, Linux, macOS, or Windows with Python

## Quick Install

### Termux / Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/salarzudfekr/reality-sni-smart-scanner/main/install.sh | sh
```

Then run:

```bash
reality-sni-smart
```
Installer note: on Termux, the command is installed into `$PREFIX/bin` when possible so `reality-sni-smart` works immediately after installation.


If the command is not found, run it directly:

```bash
python ~/reality-sni-smart-scanner/reality_sni_smart.py
```

### Windows PowerShell

```powershell
iwr -useb https://raw.githubusercontent.com/salarzudfekr/reality-sni-smart-scanner/main/install.ps1 | iex
```

Then run:

```powershell
python "$HOME\reality-sni-smart-scanner\reality_sni_smart.py"
```

## Quick Start

```bash
python reality_sni_smart.py
```

Then choose from the numeric menu:

```text
1. Scan MCI / Hamrah Aval
2. Scan Irancell
3. Scan Wi-Fi / Mokhaberat
4. Scan custom network
5. Show shared SNI candidates
6. Show saved scan files
7. Run self-test and recommendations
0. Exit
```

## Direct CLI Usage

Run a Deep scan for MCI/Hamrah Aval:

```bash
python reality_sni_smart.py scan --network mci --profile deep --max-ips 3 --raw
```

Run a quick test with only 5 built-in domains:

```bash
python reality_sni_smart.py scan --network test --profile normal --retries 1 --limit 5 --max-ips 2 --raw
```

Scan specific domains only:

```bash
python reality_sni_smart.py scan --network wifi --domains www.microsoft.com www.samsung.com www.apple.com --retries 3 --max-ips 2 --raw
```

Run self-test:

```bash
python reality_sni_smart.py self-test
```

Open the old numeric menu explicitly:

```bash
python reality_sni_smart.py menu
```
Export the built-in domain list:

```bash
python reality_sni_smart.py export-domains --output domains.example.txt
```

Scan only safer enterprise-style candidates and keep B-or-better results:

```bash
python reality_sni_smart.py scan --network mci --profile deep --category safe --min-grade B --max-ips 3 --raw
```


## CLI Options

```text
python reality_sni_smart.py scan --network NAME [options]

Options:
  --profile normal|deep|1|2   Scan profile. Default: normal
  --retries N                 Retries per SNI
  --timeout SECONDS           Socket timeout
  --workers N                 Concurrent workers
  --sleep SECONDS             Delay between retries
  --max-ips N                 Number of IPv4 addresses to test per domain
  --domains DOMAIN ...        Scan only these domains
  --limit N                   Limit loaded built-in domains for quick tests
  --raw                       Save per-attempt raw probe CSV
  --category CATEGORY          Scan only one category: safe, cdn, dev, dns, education, productivity, streaming, social, other, all
  --min-grade A|B|C|D|F        Keep only results with this grade or better
```

## Built-in Categories

The built-in domains are classified into categories such as `safe`, `cdn`, `dev`, `dns`, `education`, `productivity`, `streaming`, `social`, and `other`. Each result also includes:

- `category`
- `risk_label`
- `http_status_code`
- `reason` explaining the grade

A full editable domain list can be exported with `export-domains`.

## Output Files

Results are saved under:

```text
sni_scans/
```

Each scan creates:

```text
<network>_<profile>_<timestamp>.csv
<network>_<profile>_<timestamp>.json
<network>_<profile>_<timestamp>_raw.csv   # only when --raw is used
```

Shared analysis creates:

```text
analysis_<timestamp>.csv
analysis_<timestamp>.json
```

## Recommended Workflow

1. Run Normal mode first on each network.
2. Run Deep mode for promising networks/domains.
3. Repeat scans 2-3 times at different hours.
4. Use shared analysis to find domains stable across networks.
5. Prefer candidates with:
   - `success_rate` near 100
   - low `p95_total_ms`
   - low `jitter_ms`
   - low or negative `reputation_adjustment`
   - grade `A` or `B`

## REALITY Config Output

The scanner prints suggested snippets like:

```json
"serverNames": ["www.example.com"], "target": "www.example.com:443"
```

Use these as candidates only. Final validation should still be done with your real Xray REALITY config and the actual client networks.

## Important Notes

- This tool measures SNI connection quality, not censorship bypass guarantees.
- A low latency SNI is not always the safest SNI.
- Popular high-risk domains can be penalized by reputation adjustment.
- CDN-backed domains can resolve to multiple IPs; use `--max-ips 3` or more for better coverage.
- Do not overuse aggressive worker/retry values on mobile networks.

## Version

Current release: `v1.3.1`

## License

MIT
