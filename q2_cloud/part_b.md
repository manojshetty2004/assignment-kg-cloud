# Part B: Cloud plan (200 users, Rs. 25,000/month)

## 1. Where I would run it

| Option | Good | Bad |
|---|---|---|
| (a) Office computer, made more reliable | No new cost | Power, ISP and router are single points of failure. Part A showed the router already broke it silently for weeks. |
| (b) Cloud server for website, API, database and worker + rented GPU for the model, GPU switched on only during working hours (**my choice**) | Nothing depends on the office. GPU cost fits the budget because it runs about 12 hours a day, not 24. | Model is unavailable at night. A GPU pod takes a few minutes to start. Needs a start/stop schedule. |
| (c) Cheap cloud server + model on the office GPU through an outbound tunnel | Cheapest (about Rs. 4,200). Outbound tunnel needs no port forwarding, so Part A's problem cannot repeat. | The core feature (AI answers) still stops if office power, internet or the GPU fails. |

**Why (b):** the brief asks for "running reliably", and the office was the weak part in Part A. A 24/7 GPU does not fit the budget (see section 3), but a GPU that runs 8 am to 8 pm on working days does. The office GPU stays as a manual emergency fallback at no extra cost. I assume users work in office hours; I would confirm this, because requests outside 8 am to 8 pm would get a clear "AI is offline" message.

**Privacy:** case notes are sent to the GPU as prompts. I would pick a region and plan type suitable for private data (not shared community hosts), keep nothing on the GPU server's disk, and check the provider's data terms before launch.

## 2. GPU calculation

**Memory**
- 16-bit: 8 billion x 2 bytes = 16 GB (about 14.9 GiB). Fits in 24 GB, but only about 8 GB is left for the KV cache (attention data kept while generating) and runtime.
- 4-bit: 8 billion x 0.5 byte = 4 GB (about 3.7 GiB). Fits easily and leaves about 20 GB for the KV cache, so more users can be served at once. I would start with 4-bit and measure answer quality and peak memory. If quality is poor, move to 8-bit or 16-bit.

**Load**
- 200 users x 5 questions = 1,000 answers per day. 80% in 8 hours = 800 answers.
- 800 x 10 s = 8,000 s = 2.22 GPU-hours in 8 hours = about 28% busy. One GPU is enough on average.

**10 people at the same moment:** one GPU cannot finish ten 10-second jobs in 10 seconds. One by one, the 10th person waits about 100 s. I would use a request queue with a limit and a "you are in the queue" message, and a model server that batches requests (for example vLLM) so several answers are generated together. Batching uses more memory, so I would test with 10 parallel requests before launch.

## 3. Monthly cost

Exchange rate: Rs. 95.0194 per USD (FBIL reference rate, 16 Oct 2026). Prices exclude tax, FX fees and extra usage.

| Item | Price | Rs./month | Link; date checked |
|---|---|---:|---|
| Cloud server: Lightsail Linux 8 GB, Mumbai | $44/month | 4,181 | [AWS Lightsail plans](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bundles.html); 18 Oct 2026 |
| GPU: RunPod RTX 4090 24 GB, Secure Cloud, $0.69/hr x 264 h (12 h x 22 days) | $182.16 | 17,309 | [RunPod pricing](https://www.runpod.io/gpu-cloud/pricing), [RTX 4090 page](https://www.runpod.io/gpu/4090); 18 Oct 2026 |
| Backup storage: S3 Standard, 20 GB, Mumbai, $0.025/GB | $0.50 | 48 | [S3 pricing](https://aws.amazon.com/s3/pricing/); 18 Oct 2026 |
| External uptime monitor, free plan (assumed) | $0 | 0 | check plan limits before launch |
| **Total** | **$226.66** | **about 21,538** | |

- **Left for tax and extras:** about Rs. 3,460. I would use it for GST, a storage volume for the model files, and data transfer.
- **Price risk:** one price tracker lists the same GPU at $0.74/hr. At that rate the GPU costs about Rs. 18,560 and the total is still under Rs. 25,000.
- **Why not 24/7:** $0.69 x 730 h = $503.70 = about Rs. 47,860, which is over budget. The cheaper Community Cloud rate ($0.34/hr, about Rs. 23,580 for 730 h) still goes over once the server is added (about Rs. 27,800), and it runs on shared hosts, which I do not want for private notes.
- If the real bill is above Rs. 25,000, I would shorten GPU hours or ask for more budget before launch.

## 4. Keeping data safe

- **Backups:** the database lives on the cloud server, not on the GPU. Every night: `pg_dump`, compress, encrypt, copy to a bucket in a separate account. Keep 7 daily copies locally and 30 offsite. Backups protect against failures, so a worst case is losing up to 24 hours of notes. I would ask the team if that is acceptable, and add WAL archiving if not.
- **Restore test:** every month, restore the latest backup into a scratch database, compare table counts and open one sample case. A backup is not proven until it has been restored.
- **Secrets:** no passwords or keys in Git. Keep them in a `.env` file with strict permissions, or the cloud's secret manager. Different keys for each service. Rotate them when a staff member leaves.
- **Server access:** SSH with keys only, no passwords, no root login. Only named staff keys. SSH reachable only from the VPN or office IP. Firewall opens 80 and 443 only. The database, queue and model ports are never public. The model endpoint accepts requests only from the cloud server and needs a token. MFA on the cloud and GPU accounts.

## 5. Knowing when it breaks

- **Watch:** website and certificate expiry (from outside, alert at 21 and 14 days), API health, GPU pod running during hours, queue wait time, worker errors, disk space, CPU and memory, backup age, and the GPU start/stop schedule.
- **Alerts:** the external monitor sends email and a message to a team chat group (Slack, Telegram or WhatsApp). One named person is on call each week. I would send a test alert once a month so a broken alert path is found.

## 6. Moving day

1. A few days before: build the new setup, copy a test dump, and rehearse the whole move. Lower the DNS TTL to 5 minutes at least a day before.
2. Move day: tell users, then stop writes on the office system.
3. Take the final database dump and check it. Copy it over an encrypted connection and restore it in the cloud.
4. Compare table and row counts and open a sample case. Start all services and run a smoke test, including one AI answer.
5. Switch DNS to the new server. Keep the office system read-only for a week as a rollback.

**Downtime:** about 30 to 90 minutes of write downtime for a small database. I would time a rehearsal with the real data size, because the dump and copy time depends on it. DNS caching can extend the visible switch a little.