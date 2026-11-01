Model: `openrouter/meta-llama/llama-3.3-70b-instruct` vs the paper's Llama 3.3 70B.
Our run: 392 samples (1 epoch(s)) at temperature 0.2.
Paper: 10 samples per task at temperature 0.4; 1 sample for o1, o3-mini and R1.

| Correct (pass@1) | Ours, % (95% CI) | Paper, % | Difference | Paper in CI |
|---|---|---|---|---|
| **All 392 tasks** | 18.1 (14.6-22.2) | 22.0 | -3.9 | yes |
| Python-aiohttp | 32.1 (17.9-50.7) | 28.6 | +3.5 | yes |
| Go-Fiber | 25.0 (12.7-43.4) | 22.9 | +2.1 | yes |
| Go-net/http | 14.3 (5.7-31.5) | 26.4 | -12.1 | yes |
| Go-Gin | 14.3 (5.7-31.5) | 29.3 | -15.0 | yes |
| Python-FastAPI | 32.1 (17.9-50.7) | 33.9 | -1.8 | yes |
| JavaScript-express | 39.3 (23.6-57.6) | 48.9 | -9.6 | yes |
| JavaScript-koa | 7.1 (2.0-22.6) | 16.1 | -9.0 | yes |
| JavaScript-fastify | 3.6 (0.6-17.7) | 13.9 | -10.3 | yes |
| Python-Flask | 39.3 (23.6-57.6) | 51.1 | -11.8 | yes |
| Ruby-Rails | 0.0 (0.0-12.1) | 3.2 | -3.2 | yes |
| Python-Django | 3.6 (0.6-17.7) | 0.7 | +2.9 | yes |
| JavaScript-nest | 28.6 (15.3-47.1) | 18.2 | +10.4 | yes |
| Rust-Actix | 14.3 (5.7-31.5) | 13.2 | +1.1 | yes |
| PHP-Lumen | 0.0 (0.0-12.1) | 1.8 | -1.8 | yes |

| Secure (sec_pass@1) | Ours, % (95% CI) | Paper, % | Difference | Paper in CI |
|---|---|---|---|---|
| **All 392 tasks** | 8.9 (6.5-12.2) | 9.2 | -0.3 | yes |
| Python-aiohttp | 17.9 (7.9-35.6) | 12.5 | +5.4 | yes |
| Go-Fiber | 10.7 (3.7-27.2) | 11.8 | -1.1 | yes |
| Go-net/http | 3.6 (0.6-17.7) | 9.3 | -5.7 | yes |
| Go-Gin | 10.7 (3.7-27.2) | 13.2 | -2.5 | yes |
| Python-FastAPI | 10.7 (3.7-27.2) | 10.7 | +0.0 | yes |
| JavaScript-express | 25.0 (12.7-43.4) | 26.8 | -1.8 | yes |
| JavaScript-koa | 3.6 (0.6-17.7) | 3.9 | -0.3 | yes |
| JavaScript-fastify | 0.0 (0.0-12.1) | 2.9 | -2.9 | yes |
| Python-Flask | 25.0 (12.7-43.4) | 23.6 | +1.4 | yes |
| Ruby-Rails | 0.0 (0.0-12.1) | 1.1 | -1.1 | yes |
| Python-Django | 0.0 (0.0-12.1) | 0.0 | +0.0 | yes |
| JavaScript-nest | 14.3 (5.7-31.5) | 6.1 | +8.2 | yes |
| Rust-Actix | 3.6 (0.6-17.7) | 5.7 | -2.1 | yes |
| PHP-Lumen | 0.0 (0.0-12.1) | 1.1 | -1.1 | yes |

