Model: `openrouter/meta-llama/llama-3.3-70b-instruct` vs the paper's Llama 3.3 70B.
Our run: 392 samples (1 epoch(s)) at temperature 0.2.
Paper: 10 samples per task at temperature 0.4; 1 sample for o1, o3-mini and R1.

| Correct (pass@1) | Ours, % | Paper, % | Difference |
|---|---|---|---|
| **All 392 tasks** | 17.6 ± 3.8 | 22.0 | -4.4 |
| Python-aiohttp | 32.1 ± 17.6 | 28.6 | +3.5 |
| Go-Fiber | 25.0 ± 16.3 | 22.9 | +2.1 |
| Go-net/http | 14.3 ± 13.2 | 26.4 | -12.1 |
| Go-Gin | 10.7 ± 11.7 | 29.3 | -18.6 |
| Python-FastAPI | 32.1 ± 17.6 | 33.9 | -1.8 |
| JavaScript-express | 39.3 ± 18.4 | 48.9 | -9.6 |
| JavaScript-koa | 7.1 ± 9.7 | 16.1 | -9.0 |
| JavaScript-fastify | 3.6 ± 7.0 | 13.9 | -10.3 |
| Python-Flask | 35.7 ± 18.1 | 51.1 | -15.4 |
| Ruby-Rails | 0.0 ± 0.0 | 3.2 | -3.2 |
| Python-Django | 3.6 ± 7.0 | 0.7 | +2.9 |
| JavaScript-nest | 28.6 ± 17.0 | 18.2 | +10.4 |
| Rust-Actix | 14.3 ± 13.2 | 13.2 | +1.1 |
| PHP-Lumen | 0.0 ± 0.0 | 1.8 | -1.8 |

| Secure (sec_pass@1) | Ours, % | Paper, % | Difference |
|---|---|---|---|
| **All 392 tasks** | 9.7 ± 2.9 | 9.2 | +0.5 |
| Python-aiohttp | 17.9 ± 14.4 | 12.5 | +5.4 |
| Go-Fiber | 14.3 ± 13.2 | 11.8 | +2.5 |
| Go-net/http | 3.6 ± 7.0 | 9.3 | -5.7 |
| Go-Gin | 10.7 ± 11.7 | 13.2 | -2.5 |
| Python-FastAPI | 10.7 ± 11.7 | 10.7 | +0.0 |
| JavaScript-express | 25.0 ± 16.3 | 26.8 | -1.8 |
| JavaScript-koa | 3.6 ± 7.0 | 3.9 | -0.3 |
| JavaScript-fastify | 0.0 ± 0.0 | 2.9 | -2.9 |
| Python-Flask | 25.0 ± 16.3 | 23.6 | +1.4 |
| Ruby-Rails | 0.0 ± 0.0 | 1.1 | -1.1 |
| Python-Django | 0.0 ± 0.0 | 0.0 | +0.0 |
| JavaScript-nest | 14.3 ± 13.2 | 6.1 | +8.2 |
| Rust-Actix | 10.7 ± 11.7 | 5.7 | +5.0 |
| PHP-Lumen | 0.0 ± 0.0 | 1.1 | -1.1 |

