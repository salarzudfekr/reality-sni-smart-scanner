# Reality SNI Smart Scanner

[English](README.md) | فارسی

اسکنر هوشمند SNI برای Xray REALITY، مناسب Termux و سیستم‌های دسکتاپ. این ابزار دامنه‌های پیشنهادی را روی IPv4 و پورت 443 تست می‌کند، زمان DNS/TCP/TLS/HTTP را اندازه می‌گیرد، پایداری را امتیازدهی می‌کند و خروجی CSV/JSON می‌سازد.

## قابلیت‌ها

- منوی عددی تعاملی برای استفاده ساده
- حالت CLI غیرتعاملی برای اسکریپت و اتوماسیون
- پروفایل‌های Normal و Deep
- تست چند IP برای هر دامنه با `--max-ips`
- خروجی CSV و JSON
- ذخیره لاگ خام هر تلاش با `--raw`
- تحلیل SNIهای مشترک بین چند شبکه
- امتیازدهی مناسب REALITY بر اساس success rate، p95، jitter، TLS 1.3 و reputation
- خروجی `reality_grade` از A تا F
- لیست داخلی گسترده‌تر از subdomainهای مناسب تست REALITY
- دسته‌بندی دامنه، برچسب ریسک، کد وضعیت HTTP و ستون توضیحی `reason`
- گزینه‌های `--category`، `--min-grade` و دستور `export-domains`

## پیش‌نیازها

- Python 3.8 یا جدیدتر
- بدون نیاز به پکیج Python جانبی
- قابل استفاده روی Android Termux، Linux، macOS و Windows

## نصب سریع

### Termux / Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/salarzudfekr/reality-sni-smart-scanner/main/install.sh | sh
```

بعد اجرا کن:

```bash
reality-sni-smart
```
نکته نصب: در Termux اگر ممکن باشد دستور داخل `$PREFIX/bin` نصب می‌شود تا `reality-sni-smart` بلافاصله بعد از نصب کار کند.


اگر دستور پیدا نشد، مستقیم اجرا کن:

```bash
python ~/reality-sni-smart-scanner/reality_sni_smart.py
```

### Windows PowerShell

```powershell
iwr -useb https://raw.githubusercontent.com/salarzudfekr/reality-sni-smart-scanner/main/install.ps1 | iex
```

بعد اجرا کن:

```powershell
python "$HOME\reality-sni-smart-scanner\reality_sni_smart.py"
```

## شروع سریع

```bash
python reality_sni_smart.py
```

بعد از منوی عددی انتخاب کن:

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

## استفاده مستقیم با CLI

اسکن Deep برای همراه اول:

```bash
python reality_sni_smart.py scan --network mci --profile deep --max-ips 3 --raw
```

تست سریع فقط با 5 دامنه داخلی:

```bash
python reality_sni_smart.py scan --network test --profile normal --retries 1 --limit 5 --max-ips 2 --raw
```

اسکن چند دامنه مشخص:

```bash
python reality_sni_smart.py scan --network wifi --domains www.microsoft.com www.samsung.com www.apple.com --retries 3 --max-ips 2 --raw
```

اجرای self-test:

```bash
python reality_sni_smart.py self-test
```

باز کردن منوی قدیمی:

```bash
python reality_sni_smart.py menu
```
خروجی گرفتن از لیست داخلی دامنه‌ها:

```bash
python reality_sni_smart.py export-domains --output domains.example.txt
```

اسکن فقط candidateهای امن‌تر و نگه داشتن نتایج B یا بهتر:

```bash
python reality_sni_smart.py scan --network mci --profile deep --category safe --min-grade B --max-ips 3 --raw
```


## گزینه‌های CLI

```text
python reality_sni_smart.py scan --network NAME [options]

Options:
  --profile normal|deep|1|2   پروفایل اسکن. پیش‌فرض: normal
  --retries N                 تعداد تلاش برای هر SNI
  --timeout SECONDS           timeout سوکت
  --workers N                 تعداد worker همزمان
  --sleep SECONDS             فاصله بین retryها
  --max-ips N                 تعداد IPv4هایی که برای هر دامنه تست می‌شوند
  --domains DOMAIN ...        فقط همین دامنه‌ها را اسکن کن
  --limit N                   محدود کردن تعداد دامنه‌های داخلی برای تست سریع
  --raw                       ذخیره CSV خام از هر تلاش
  --category CATEGORY          اسکن فقط یک دسته: safe, cdn, dev, dns, education, productivity, streaming, social, other, all
  --min-grade A|B|C|D|F        نگه داشتن فقط نتیجه‌هایی با این grade یا بهتر
```

## دسته‌بندی‌های داخلی

دامنه‌های داخلی در دسته‌هایی مثل `safe`، `cdn`، `dev`، `dns`، `education`، `productivity`، `streaming`، `social` و `other` قرار می‌گیرند. هر نتیجه این ستون‌ها را هم دارد:

- `category`
- `risk_label`
- `http_status_code`
- `reason` برای توضیح دلیل grade

با دستور `export-domains` می‌توانی کل لیست داخلی را خروجی بگیری و ویرایش کنی.

## فایل‌های خروجی

خروجی‌ها در این پوشه ذخیره می‌شوند:

```text
sni_scans/
```

هر اسکن این فایل‌ها را می‌سازد:

```text
<network>_<profile>_<timestamp>.csv
<network>_<profile>_<timestamp>.json
<network>_<profile>_<timestamp>_raw.csv   # فقط وقتی --raw فعال باشد
```

تحلیل مشترک چند شبکه این فایل‌ها را می‌سازد:

```text
analysis_<timestamp>.csv
analysis_<timestamp>.json
```

## روش پیشنهادی استفاده

1. اول روی هر شبکه Normal mode بگیر.
2. برای گزینه‌های امیدوارکننده Deep mode بگیر.
3. هر شبکه را 2 تا 3 بار در ساعت‌های مختلف تست کن.
4. از shared analysis برای پیدا کردن دامنه‌های پایدار بین چند شبکه استفاده کن.
5. دامنه‌هایی بهترند که این ویژگی‌ها را داشته باشند:
   - `success_rate` نزدیک 100
   - `p95_total_ms` پایین
   - `jitter_ms` پایین
   - `reputation_adjustment` پایین یا منفی
   - grade برابر `A` یا `B`

## خروجی پیشنهادی برای REALITY

اسکنر snippetهایی مثل این چاپ می‌کند:

```json
"serverNames": ["www.example.com"], "target": "www.example.com:443"
```

این‌ها فقط candidate هستند. انتخاب نهایی را حتماً با کانفیگ واقعی Xray REALITY و شبکه‌های واقعی کلاینت تست کن.

## نکات مهم

- این ابزار کیفیت اتصال SNI را می‌سنجد، نه تضمین عبور از فیلترینگ.
- latency پایین همیشه به معنی انتخاب امن‌تر نیست.
- دامنه‌های خیلی معروف یا پرریسک ممکن است با reputation adjustment جریمه شوند.
- دامنه‌های CDN ممکن است چند IP داشته باشند؛ برای نتیجه بهتر از `--max-ips 3` یا بیشتر استفاده کن.
- روی اینترنت موبایل مقدار worker و retry را بیش از حد بالا نبر.

## نسخه

نسخه فعلی: `v1.3.1`

## لایسنس

MIT
