# Part B: cloud plan

## Where I would run it

| Option | Trade-off |
|---|---|
| Office computer | No new GPU rental, but computer, power, router, and ISP are single failure points. Part A showed the router risk. |
| Rented GPU server | GPU and app can run in a data centre, but continuous GPU cost depends on type and region. Get a quote before choosing. |
| Hybrid (my choice) | Cloud VPS runs website, API, database, and worker; existing office GPU serves the model through an outbound VPN (encrypted private connection). Affordable start, but AI stops if office power, ISP, or GPU fails. |

I choose hybrid to reuse the owned GPU and pay for a small cloud server. One VPS is not high availability. Case notes cross the VPN to the office model, so I would restrict that connection. If the actual bill exceeds budget, I would revise the design or ask for more budget before launch.

## GPU estimate

- **16-bit:** 8 billion parameters × 16 bits ÷ 8 = 16 billion bytes ≈ **16 GB** (14.9 GiB).
- **4-bit:** 8 billion × 4 ÷ 8 = 4 billion bytes ≈ **4 GB** (3.7 GiB).
- Both weights fit on 24 GB in theory. KV cache (attention data kept during generation), runtime, and temporary buffers need extra memory. Long context and concurrent requests increase cache use. I would start with 4-bit weights and measure peak memory.

**Load:** 200 users × 5 = 1,000 answers/workday. 80% in 8 hours = 800 answers. 800 × 10 GPU-seconds = 8,000 seconds = **2.22 GPU-hours in 8 hours**, about **28% average use**. One GPU has enough total work time if the 10-second estimate holds and requests are spread out; this does not prove prompt latency.

Ten simultaneous requests cannot all finish in ten seconds on one GPU. Without batching, ten 10-second waves mean the last may wait about 100 seconds, plus overhead. A bounded queue controls overload. Batching can improve throughput but uses more memory; I would measure it.

## Monthly cost estimate

Prices checked **18 Oct 2026**. Conversion: **₹95.0194/USD**, FBIL USD/INR rate for **16 Oct 2026**, reported on [CBonds' FBIL index page](https://cbonds.com/indexes/179695/) and published by [FBIL](https://www.fbil.org.in/). INR estimates exclude tax, FX fees, and excess usage.

| Item | Price | INR/month | Provider link; checked |
|---|---:|---:|---|
| Lightsail Linux 8 GB, public IPv4, Mumbai | $44 | ₹4,181 | [AWS plan table](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bundles.html); 18 Oct 2026. Mumbai has half the listed transfer allowance. |
| S3 Standard, assumed 20 GB in Mumbai | $0.025/GB = $0.50 | ₹48 | [S3 pricing](https://aws.amazon.com/s3/pricing/); 18 Oct 2026. Storage only; requests/transfer can add cost. |
| Basic CloudWatch metrics/logs | $0 assumed within free allowance | ₹0 assumed | [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/); 18 Oct 2026. |
| GPU server alternative (not selected) |  |  | [EC2 pricing](https://aws.amazon.com/ec2/pricing/on-demand/); 18 Oct 2026. **TODO: student to check** actual GPU and region quote. |
| **Known cloud subtotal** | **$44.50** | **₹4,229** | Before tax, fees, and excess usage. |

Known new cloud spend is below ₹25,000. Office electricity/internet bills were not supplied, so I cannot honestly give a complete all-in total. Add those bills and actual tax/usage before approval. If that total is above ₹25,000, do not launch on this plan; reduce costs only if load tests allow, or ask for more budget. A GPU rental is not in the subtotal.

## Safety, monitoring, move

- **Backups:** Daily `pg_dump`, gzip, seven local copies, plus encrypted offsite copy in a separate account/bucket. Monthly, restore into an isolated database; check tables, row counts, and a sample case. A backup is not proven until restored.
- **Access:** Keep secrets out of Git; protect `.env` and use a managed secret store when available. SSH only for named staff keys via VPN/allowlist; disable password SSH/root login. Individual app accounts; least privilege. Do not expose database, queue, or model ports publicly.
- **Alerts:** Watch external HTTPS and certificate expiry, API health, queue age, worker errors, database disk/connections, VPS CPU/RAM/disk, GPU memory/temperature/use, VPN, and backup age. Alert on downtime, failed backups, growing queue, or low disk. Test alerts monthly.
- **Move:** Briefly stop writes; take and verify final dump; copy securely; restore in cloud; compare counts and sample case; start services and smoke-check; change DNS. Keep old system read-only for rollback. I estimate **30–90 minutes write downtime** for a small database, but would rehearse using its real size. DNS caching can extend the visible cutover.
