import argparse, csv, json, os, socket, ssl, time, statistics, concurrent.futures
from datetime import datetime
from urllib.parse import urlparse

VERSION = "1.1.0"
SCAN_DIR = "sni_scans"
DEFAULT_MAX_IPS = 3

PROFILES = {
    "1": {"name": "Normal", "retries": 5, "timeout": 4, "workers": 6, "sleep": 0.3},
    "2": {"name": "Deep", "retries": 10, "timeout": 5, "workers": 4, "sleep": 1.0},
}

DOMAINS = """
www.microsoft.com www.apple.com www.samsung.com www.hp.com www.dell.com
www.lenovo.com www.oracle.com www.jetbrains.com www.ibm.com www.adobe.com
www.cisco.com www.intel.com www.amd.com www.nvidia.com www.cloudflare.com
www.cloudflare.net www.speedtest.net www.yahoo.com www.bing.com www.office.com
www.live.com www.github.com www.mozilla.org www.python.org www.ubuntu.com
www.debian.org www.kernel.org www.asus.com www.acer.com www.sony.com
www.fastly.com www.akamai.com www.paypal.com www.booking.com www.airbnb.com
www.wikipedia.org www.wikimedia.org www.wordpress.com www.shopify.com
www.salesforce.com www.zoom.us www.slack.com www.atlassian.com www.docker.com
www.elastic.co www.mongodb.com www.digitalocean.com www.linode.com
www.ovhcloud.com www.hetzner.com www.britannica.com www.stackoverflow.com
www.stackexchange.com www.medium.com www.quora.com www.imdb.com www.archive.org
www.wired.com www.theverge.com www.techcrunch.com www.engadget.com www.cnet.com
www.google.com www.gstatic.com www.youtube.com www.android.com aws.amazon.com
www.amazonaws.com www.amazon.com www.twitch.tv www.meta.com www.facebook.com
www.instagram.com www.whatsapp.com www.netflix.com www.disneyplus.com www.hulu.com
www.steamcommunity.com store.steampowered.com www.epicgames.com www.ea.com
www.ubisoft.com www.riotgames.com www.blizzard.com www.xbox.com www.playstation.com
www.cloudflare-dns.com one.one.one.one www.quad9.net dns.google www.opendns.com
www.nextdns.io www.verisign.com www.digicert.com www.letsencrypt.org
www.godaddy.com www.namecheap.com www.heroku.com www.netlify.com www.vercel.com
www.render.com www.fly.io www.vultr.com www.scaleway.com www.redhat.com
www.vmware.com www.mysql.com www.postgresql.org www.redis.io www.sqlite.org
www.nginx.com www.apache.org www.nodejs.org www.npmjs.com www.typescriptlang.org
www.rust-lang.org go.dev www.php.net www.figma.com www.canva.com www.notion.so
www.trello.com www.asana.com www.monday.com www.clickup.com www.linear.app
www.gitlab.com bitbucket.org www.sentry.io www.datadoghq.com www.grafana.com
www.udemy.com www.coursera.org www.edx.org www.khanacademy.org www.duolingo.com
www.bbc.com www.cnn.com www.reuters.com www.bloomberg.com www.forbes.com
www.nytimes.com www.theguardian.com www.mastercard.com www.visa.com www.stripe.com
www.airbus.com www.boeing.com www.toyota.com www.ford.com www.bmw.com
www.mercedes-benz.com www.tesla.com www.volvo.com www.ikea.com www.nike.com
www.adidas.com www.puma.com www.unilever.com www.pg.com www.pepsi.com
www.coca-cola.com www.mcdonalds.com www.starbucks.com
""".split()

RISK = {
    "github.com": 180, "cloudflare.com": 140, "cloudflare.net": 120,
    "wikipedia.org": 120, "google.com": 160, "youtube.com": 220,
    "facebook.com": 220, "instagram.com": 220, "reddit.com": 160,
    "whatsapp.com": 180, "netflix.com": 160,
}

SAFE = {
    "samsung.com": 90, "hp.com": 80, "dell.com": 80, "lenovo.com": 70,
    "oracle.com": 70, "jetbrains.com": 65, "microsoft.com": 60,
    "apple.com": 60, "ibm.com": 55, "adobe.com": 45, "cisco.com": 45,
    "intel.com": 45, "amd.com": 45,
}


def clear():
    os.system("clear")


def pause():
    input("\nPress Enter to continue...")


def title():
    print("=" * 62)
    print("          REALITY SNI Smart Scanner - Stable Edition")
    print("=" * 62)


def clean_domain(value):
    value = value.strip().lower()
    if not value or value.startswith("#"):
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        value = urlparse(value).hostname or value
    return value.strip().strip("/")


def root(domain):
    parts = domain.lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else domain.lower()


def reputation(domain):
    r = root(domain)
    score = 0
    for k, v in RISK.items():
        if r == k or domain.endswith("." + k):
            score += v
    for k, v in SAFE.items():
        if r == k or domain.endswith("." + k):
            score -= v
    return score


def reality_grade(row):
    if row.get("status") != "OK":
        return "F"

    success = safe_float(row.get("success_rate")) or 0
    p95 = safe_float(row.get("p95_total_ms"))
    jitter = safe_float(row.get("jitter_ms")) or 999999
    risk = safe_float(row.get("reputation_adjustment")) or 0

    if success >= 100 and p95 is not None and p95 <= 450 and jitter <= 80 and risk <= 80:
        return "A"
    if success >= 95 and p95 is not None and p95 <= 750 and jitter <= 150 and risk <= 140:
        return "B"
    if success >= 80 and p95 is not None and p95 <= 1200 and jitter <= 300:
        return "C"
    return "D"


def parse_int(value, default, min_value=1):
    if value == "" or value is None:
        return default
    try:
        parsed = int(value)
        return parsed if parsed >= min_value else default
    except ValueError:
        print(f"Invalid integer '{value}', using {default}.")
        return default


def parse_float(value, default, min_value=0):
    if value == "" or value is None:
        return default
    try:
        parsed = float(value)
        return parsed if parsed >= min_value else default
    except ValueError:
        print(f"Invalid number '{value}', using {default}.")
        return default


def load_domains():
    domains = []
    for d in DOMAINS:
        d = clean_domain(d)
        if d and d not in domains:
            domains.append(d)

    if os.path.exists("domains.txt"):
        with open("domains.txt") as f:
            for line in f:
                d = clean_domain(line)
                if d and d not in domains:
                    domains.append(d)

    return domains


def avg(values):
    return round(statistics.mean(values), 2) if values else ""


def stdev(values):
    return round(statistics.pstdev(values), 2) if len(values) > 1 else 0


def percentile(values, p):
    if not values:
        return ""
    values = sorted(values)
    return round(values[int(round((len(values) - 1) * p))], 2)


def safe_float(v):
    try:
        if v == "" or v is None:
            return None
        return float(v)
    except Exception:
        return None


def resolve_ipv4(domain, timeout):
    old = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        start = time.time()
        infos = socket.getaddrinfo(domain, 443, socket.AF_INET, socket.SOCK_STREAM)
        dns_ms = (time.time() - start) * 1000
        ips = list(dict.fromkeys(i[4][0] for i in infos))
        return ips, dns_ms, ""
    except Exception as e:
        return [], None, str(e)[:160]
    finally:
        socket.setdefaulttimeout(old)


def probe(domain, ip, timeout):
    out = {
        "ok": False, "tcp_ms": None, "tls_ms": None, "http_ms": None,
        "total_ms": None, "tls_version": "", "cipher": "",
        "http_status": "", "error": "",
    }

    raw = None
    tls = None
    total_start = time.time()

    try:
        s = time.time()
        raw = socket.create_connection((ip, 443), timeout=timeout)
        out["tcp_ms"] = (time.time() - s) * 1000

        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2

        s = time.time()
        tls = ctx.wrap_socket(raw, server_hostname=domain)
        out["tls_ms"] = (time.time() - s) * 1000
        out["tls_version"] = tls.version() or ""
        out["cipher"] = tls.cipher()[0] if tls.cipher() else ""

        s = time.time()
        req = (
            f"HEAD / HTTP/1.1\r\n"
            f"Host: {domain}\r\n"
            f"User-Agent: Mozilla/5.0\r\n"
            f"Accept: */*\r\n"
            f"Connection: close\r\n\r\n"
        )
        tls.sendall(req.encode())
        res = tls.recv(512)
        out["http_ms"] = (time.time() - s) * 1000

        first = res.split(b"\r\n", 1)[0].decode(errors="ignore")
        out["http_status"] = first
        out["ok"] = first.startswith("HTTP/")
        if not out["ok"]:
            out["error"] = "bad_http_response"

    except Exception as e:
        out["error"] = str(e)[:160]

    finally:
        try:
            if tls:
                tls.close()
            elif raw:
                raw.close()
        except Exception:
            pass

    out["total_ms"] = (time.time() - total_start) * 1000
    return out


def summarize(domain, ip, dns_ms, probes, retries):
    ok = [p for p in probes if p.get("ok")]
    success = len(ok) / retries * 100

    tcp = [p["tcp_ms"] for p in ok if p["tcp_ms"] is not None]
    tls = [p["tls_ms"] for p in ok if p["tls_ms"] is not None]
    http = [p["http_ms"] for p in ok if p["http_ms"] is not None]
    total = [p["total_ms"] for p in ok if p["total_ms"] is not None]

    p95 = percentile(total, 0.95)
    jitter = stdev(total)
    tls13 = sum(1 for p in ok if p.get("tls_version") == "TLSv1.3")
    tls13_rate = tls13 / len(ok) * 100 if ok else 0

    rep = reputation(domain)

    if not ok:
        final_score = 999999
    else:
        final_score = float(avg(total)) + jitter * 1.8 + max(0, 100 - success) * 12 + float(p95) * 0.25 + rep
        if tls13_rate >= 80:
            final_score *= 0.88
        elif tls13_rate >= 50:
            final_score *= 0.94

    last_ok = ok[-1] if ok else {}
    errors = [p.get("error", "") for p in probes if not p.get("ok")]

    row = {
        "domain": domain,
        "ip": ip,
        "status": "OK" if ok else "FAILED",
        "success_rate": round(success, 1),
        "dns_ms": round(dns_ms, 2) if dns_ms else "",
        "avg_tcp_ms": avg(tcp),
        "avg_tls_ms": avg(tls),
        "avg_http_ms": avg(http),
        "avg_total_ms": avg(total),
        "p95_total_ms": p95,
        "jitter_ms": jitter,
        "tls13_rate": round(tls13_rate, 1),
        "tls_version": last_ok.get("tls_version", ""),
        "cipher": last_ok.get("cipher", ""),
        "http_status": last_ok.get("http_status", ""),
        "reputation_adjustment": rep,
        "final_score": round(final_score, 2),
        "error": errors[-1] if errors else "",
    }
    row["reality_grade"] = reality_grade(row)
    return row


def scan_domain(domain, retries, timeout, sleep_time, max_ips=DEFAULT_MAX_IPS, raw_probe_rows=None):
    ips, dns_ms, err = resolve_ipv4(domain, timeout)
    if not ips:
        probes = [{"ok": False, "error": "dns_error: " + err}]
        if raw_probe_rows is not None:
            raw_probe_rows.append({"domain": domain, "ip": "", "attempt": 1, **probes[0]})
        return summarize(domain, "", dns_ms, probes, retries)

    selected_ips = ips[:max(1, max_ips)]
    candidates = []

    for ip in selected_ips:
        results = []
        for i in range(retries):
            probe_result = probe(domain, ip, timeout)
            results.append(probe_result)
            if raw_probe_rows is not None:
                raw_probe_rows.append({"domain": domain, "ip": ip, "attempt": i + 1, **probe_result})
            if sleep_time > 0 and i < retries - 1:
                time.sleep(sleep_time)
        candidates.append(summarize(domain, ip, dns_ms, results, retries))

    best = min(candidates, key=lambda x: x["final_score"])
    best["tested_ips"] = ",".join(selected_ips)
    best["tested_ip_count"] = len(selected_ips)
    return best


def print_best(results, limit=15):
    ok = [r for r in results if r["status"] == "OK"]
    ok.sort(key=lambda x: x["final_score"])

    print("\nBest raw results for this network:")
    print("-" * 118)
    print(f"{'Rank':<5} {'SNI':<28} {'OK%':<7} {'Total':<9} {'P95':<9} {'Jitter':<9} {'TLS1.3%':<9} {'Score':<9}")
    print("-" * 118)

    for i, r in enumerate(ok[:limit], 1):
        print(f"{i:<5} {r['domain']:<28} {r['success_rate']:<7} {r['avg_total_ms']:<9} {r['p95_total_ms']:<9} {r['jitter_ms']:<9} {r['tls13_rate']:<9} {r['final_score']:<9} grade={r.get('reality_grade', '')}")

    print("\nTop REALITY configs:")
    for r in ok[:5]:
        print(f'"serverNames": ["{r["domain"]}"], "target": "{r["domain"]}:443"')


def choose_profile():
    print("Select scan mode:")
    print("1. Normal - faster, good for first-pass scanning")
    print("2. Deep   - slower, better for final decisions")
    choice = input("\nSelect [1/2]: ").strip()
    return PROFILES.get(choice, PROFILES["1"]).copy()


def customize(profile):
    custom = input("\nDo you want manual settings? [y/N]: ").strip().lower()
    if custom != "y":
        return profile

    retries = input(f"Retries per SNI? Default {profile['retries']}: ").strip()
    timeout = input(f"Timeout per test? Default {profile['timeout']}s: ").strip()
    workers = input(f"Concurrent workers? Default {profile['workers']}: ").strip()
    sleep = input(f"Delay between retries? Default {profile['sleep']}s: ").strip()

    profile["retries"] = parse_int(retries, profile["retries"], 1)
    profile["timeout"] = parse_float(timeout, profile["timeout"], 0.1)
    profile["workers"] = parse_int(workers, profile["workers"], 1)
    profile["sleep"] = parse_float(sleep, profile["sleep"], 0)

    return profile


def save_outputs(output, results, raw_probe_rows=None):
    if not results:
        return
    csv_fields = list(results[0].keys())
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(results)

    json_output = output.rsplit(".", 1)[0] + ".json"
    with open(json_output, "w") as f:
        json.dump(results, f, indent=2)

    raw_output = ""
    if raw_probe_rows:
        raw_output = output.rsplit(".", 1)[0] + "_raw.csv"
        raw_fields = list(raw_probe_rows[0].keys())
        with open(raw_output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=raw_fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(raw_probe_rows)

    return json_output, raw_output


def print_summary(results):
    total = len(results)
    ok = sum(1 for r in results if r["status"] == "OK")
    failed = total - ok
    grades = {}
    for r in results:
        grades[r.get("reality_grade", "?")] = grades.get(r.get("reality_grade", "?"), 0) + 1
    print(f"\nSummary: total={total} ok={ok} failed={failed} grades={grades}")


def run_scan(network, profile=None, max_ips=DEFAULT_MAX_IPS, domains=None, raw=False, interactive=True):
    clear()
    title()
    os.makedirs(SCAN_DIR, exist_ok=True)

    domains = domains or load_domains()
    print(f"Selected network: {network}")
    print(f"SNI domains loaded: {len(domains)}\n")

    if profile is None:
        profile = customize(choose_profile())
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = f"{SCAN_DIR}/{network}_{profile['name'].lower()}_{ts}.csv"

    print(f"\nStarting {profile['name']} scan on {network}...")
    print(f"retries={profile['retries']} timeout={profile['timeout']}s workers={profile['workers']} sleep={profile['sleep']}s max_ips={max_ips}")
    print(f"Output file: {output}\n")

    results = []
    raw_probe_rows = [] if raw else None
    with concurrent.futures.ThreadPoolExecutor(max_workers=profile["workers"]) as ex:
        futures = {
            ex.submit(scan_domain, d, profile["retries"], profile["timeout"], profile["sleep"], max_ips, raw_probe_rows): d
            for d in domains
        }

        done = 0
        for f in concurrent.futures.as_completed(futures):
            done += 1
            r = f.result()
            r["network"] = network
            r["profile"] = profile["name"]
            results.append(r)

            if r["status"] == "OK":
                print(f"[{done}/{len(domains)}] OK     {r['domain']:<28} ok={r['success_rate']:<5} total={r['avg_total_ms']:<8} p95={r['p95_total_ms']:<8} jitter={r['jitter_ms']:<7} score={r['final_score']} grade={r.get('reality_grade', '')} ip={r.get('ip', '')}")
            else:
                print(f"[{done}/{len(domains)}] FAILED {r['domain']:<28} {r['error']}")

    results.sort(key=lambda x: x["final_score"])

    json_output, raw_output = save_outputs(output, results, raw_probe_rows)

    print_best(results)
    print_summary(results)
    print(f"\nSaved CSV: {output}")
    print(f"Saved JSON: {json_output}")
    if raw_output:
        print(f"Saved raw probes: {raw_output}")
    if interactive:
        pause()
    return output


def scan_files():
    os.makedirs(SCAN_DIR, exist_ok=True)
    return sorted(
        os.path.join(SCAN_DIR, f)
        for f in os.listdir(SCAN_DIR)
        if f.endswith(".csv") and not f.startswith("analysis_")
    )


def show_files():
    clear()
    title()
    files = scan_files()

    if not files:
        print("No scan files found yet.")
        pause()
        return

    print("Saved scan files:\n")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")
    pause()


def row_avg(rows, key):
    values = []
    for r in rows:
        v = safe_float(r.get(key))
        if v is not None:
            values.append(v)
    return statistics.mean(values) if values else None


def analyze():
    clear()
    title()
    files = scan_files()

    if len(files) < 2:
        print("At least two scan files are required for shared SNI analysis.")
        pause()
        return

    print("Available scan files:\n")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")

    choice = input("\nAnalyze all files? [Y/n]: ").strip().lower()
    selected = files

    if choice == "n":
        raw = input("Enter file numbers separated by spaces, e.g. 1 2 4: ").strip()
        idxs = []
        for x in raw.split():
            try:
                idx = int(x) - 1
                if 0 <= idx < len(files):
                    idxs.append(idx)
            except Exception:
                pass
        selected = [files[i] for i in idxs]

    if len(selected) < 2:
        print("At least two files must be selected.")
        pause()
        return

    min_raw = input("Minimum shared networks? Default 2: ").strip()
    min_networks = int(min_raw) if min_raw else 2

    rows = []
    for file in selected:
        with open(file, newline="") as f:
            for row in csv.DictReader(f):
                if row.get("status") == "OK":
                    row["_file"] = file
                    rows.append(row)

    grouped = {}
    for row in rows:
        network = row.get("network") or os.path.basename(row["_file"]).split("_")[0]
        grouped.setdefault(row["domain"], {}).setdefault(network, []).append(row)

    all_networks = set()
    for row in rows:
        all_networks.add(row.get("network") or os.path.basename(row["_file"]).split("_")[0])

    output_rows = []

    for domain, nets in grouped.items():
        coverage = len(nets)
        if coverage < min_networks:
            continue

        per_net = []
        for network, rs in nets.items():
            per_net.append({
                "success": row_avg(rs, "success_rate") or 0,
                "total": row_avg(rs, "avg_total_ms"),
                "p95": row_avg(rs, "p95_total_ms"),
                "jitter": row_avg(rs, "jitter_ms") or 0,
                "tls13": row_avg(rs, "tls13_rate") or 0,
                "score": row_avg(rs, "final_score"),
            })

        totals = [x["total"] for x in per_net if x["total"] is not None]
        p95s = [x["p95"] for x in per_net if x["p95"] is not None]
        scores = [x["score"] for x in per_net if x["score"] is not None]
        if not totals or not scores:
            continue

        avg_success = statistics.mean(x["success"] for x in per_net)
        avg_total = statistics.mean(totals)
        avg_p95 = statistics.mean(p95s) if p95s else avg_total
        avg_jitter = statistics.mean(x["jitter"] for x in per_net)
        avg_tls13 = statistics.mean(x["tls13"] for x in per_net)
        avg_score = statistics.mean(scores)
        worst_score = max(scores)

        combined = (
            avg_score
            + avg_jitter * 2.5
            + avg_p95 * 0.38
            + worst_score * 0.30
            + max(0, len(all_networks) - coverage) * 250
            + max(0, 100 - avg_success) * 18
            + reputation(domain)
            - coverage * 150
            - avg_tls13 * 0.8
        )

        row = {
            "domain": domain,
            "coverage": coverage,
            "networks": ",".join(sorted(nets.keys())),
            "avg_success": round(avg_success, 1),
            "avg_total": round(avg_total, 2),
            "avg_p95": round(avg_p95, 2),
            "avg_jitter": round(avg_jitter, 2),
            "avg_tls13": round(avg_tls13, 1),
            "reputation_adjustment": reputation(domain),
            "combined_score": round(combined, 2),
        }
        row["reality_grade"] = reality_grade({
            "status": "OK",
            "success_rate": row["avg_success"],
            "p95_total_ms": row["avg_p95"],
            "jitter_ms": row["avg_jitter"],
            "reputation_adjustment": row["reputation_adjustment"],
        })
        output_rows.append(row)

    output_rows.sort(key=lambda x: (-x["coverage"], x["combined_score"]))

    clear()
    title()

    if not output_rows:
        print("No shared SNI candidates found with the current condition.")
        pause()
        return

    print("Best shared and stable SNI candidates:")
    print("-" * 142)
    print(f"{'Rank':<5} {'SNI':<28} {'Nets':<6} {'OK%':<7} {'Total':<9} {'P95':<9} {'Jitter':<9} {'TLS1.3%':<9} {'RiskAdj':<8} {'Score':<10} {'Seen In'}")
    print("-" * 142)

    for i, r in enumerate(output_rows[:25], 1):
        print(f"{i:<5} {r['domain']:<28} {r['coverage']:<6} {r['avg_success']:<7} {r['avg_total']:<9} {r['avg_p95']:<9} {r['avg_jitter']:<9} {r['avg_tls13']:<9} {r['reputation_adjustment']:<8} {r['combined_score']:<10} {r['networks']}")

    print("\nTop universal REALITY configs:")
    for r in output_rows[:5]:
        print(f'"serverNames": ["{r["domain"]}"], "target": "{r["domain"]}:443"')

    out = f"{SCAN_DIR}/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    json_out = out.rsplit(".", 1)[0] + ".json"
    with open(json_out, "w") as f:
        json.dump(output_rows, f, indent=2)

    print(f"\nAnalysis saved CSV: {out}")
    print(f"Analysis saved JSON: {json_out}")
    pause()


def self_test(interactive=True):
    clear()
    title()
    print("Running scanner self-test...\n")

    checks = []
    checks.append(("Python runtime", True, "OK"))
    checks.append(("CSV module", hasattr(csv, "DictWriter"), "OK"))
    checks.append(("SSL module", hasattr(ssl, "create_default_context"), "OK"))
    checks.append(("Domains loaded", len(load_domains()) > 0, f"{len(load_domains())} domains"))
    checks.append(("Reputation scoring", isinstance(reputation("www.samsung.com"), int), "OK"))

    try:
        socket.getaddrinfo("www.microsoft.com", 443, socket.AF_INET, socket.SOCK_STREAM)
        checks.append(("DNS IPv4 lookup", True, "OK"))
    except Exception as e:
        checks.append(("DNS IPv4 lookup", False, str(e)[:80]))

    for name, ok, detail in checks:
        print(f"{'OK' if ok else 'FAIL':<5} {name:<22} {detail}")

    print("\nRecommendations:")
    print("- Use Deep mode for final decisions.")
    print("- Run each network 2-3 times at different hours if possible.")
    print("- Prefer OK%=100, low Jitter, low P95, and full network coverage.")
    print("- Keep port 443 as the main REALITY inbound when possible.")
    print("- This is SNI quality testing; final validation should still be done with your real REALITY config.")
    if interactive:
        pause()


def custom_scan():
    name = input("Enter network name, e.g. rightel or homewifi: ").strip().lower()
    if not name:
        print("Invalid network name.")
        pause()
        return
    name = "".join(c for c in name if c.isalnum() or c in ["-", "_"])
    run_scan(name)


def build_profile(name, retries=None, timeout=None, workers=None, sleep=None):
    profile = PROFILES.get(name, PROFILES["1"]).copy()
    if retries is not None:
        profile["retries"] = parse_int(str(retries), profile["retries"], 1)
    if timeout is not None:
        profile["timeout"] = parse_float(str(timeout), profile["timeout"], 0.1)
    if workers is not None:
        profile["workers"] = parse_int(str(workers), profile["workers"], 1)
    if sleep is not None:
        profile["sleep"] = parse_float(str(sleep), profile["sleep"], 0)
    return profile


def parse_args():
    parser = argparse.ArgumentParser(description="REALITY SNI Smart Scanner")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command")

    scan = sub.add_parser("scan", help="Run a non-interactive scan")
    scan.add_argument("--network", required=True, help="Network name, e.g. mci, irancell, wifi")
    scan.add_argument("--profile", choices=["1", "2", "normal", "deep"], default="1")
    scan.add_argument("--retries", type=int)
    scan.add_argument("--timeout", type=float)
    scan.add_argument("--workers", type=int)
    scan.add_argument("--sleep", type=float)
    scan.add_argument("--max-ips", type=int, default=DEFAULT_MAX_IPS)
    scan.add_argument("--domains", nargs="*", help="Optional domain list instead of built-in domains")
    scan.add_argument("--limit", type=int, help="Limit loaded domains for quick tests")
    scan.add_argument("--raw", action="store_true", help="Save per-attempt raw probe CSV")

    sub.add_parser("self-test", help="Run self-test")
    sub.add_parser("menu", help="Open interactive menu")
    return parser.parse_args()


def cli():
    args = parse_args()
    if args.command == "scan":
        profile_key = "2" if args.profile == "deep" else "1" if args.profile == "normal" else args.profile
        profile = build_profile(profile_key, args.retries, args.timeout, args.workers, args.sleep)
        domains = [clean_domain(d) for d in args.domains] if args.domains else load_domains()
        domains = [d for d in domains if d]
        if args.limit:
            domains = domains[:args.limit]
        run_scan(args.network, profile, max(1, args.max_ips), domains, args.raw, interactive=False)
    elif args.command == "self-test":
        self_test(interactive=False)
    else:
        menu()


def menu():
    while True:
        clear()
        title()
        print("1. Scan MCI / Hamrah Aval")
        print("2. Scan Irancell")
        print("3. Scan Wi-Fi / Mokhaberat")
        print("4. Scan custom network")
        print("5. Show shared SNI candidates")
        print("6. Show saved scan files")
        print("7. Run self-test and recommendations")
        print("0. Exit\n")

        choice = input("Select an option: ").strip()

        if choice == "1":
            run_scan("mci")
        elif choice == "2":
            run_scan("irancell")
        elif choice == "3":
            run_scan("wifi")
        elif choice == "4":
            custom_scan()
        elif choice == "5":
            analyze()
        elif choice == "6":
            show_files()
        elif choice == "7":
            self_test()
        elif choice == "0":
            print("Exit.")
            break
        else:
            print("Invalid option.")
            time.sleep(1)


if __name__ == "__main__":
    cli()
