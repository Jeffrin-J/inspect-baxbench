Model: `openrouter/deepseek/deepseek-chat` vs the paper's DeepSeek V3.
Our run: 392 samples (1 epoch(s)) at temperature 0.2.
Paper: 10 samples per task at temperature 0.4; 1 sample for o1, o3-mini and R1.

| Correct (pass@1) | Ours, % | Paper, % | Difference |
|---|---|---|---|
| **All 392 tasks** | 39.5 ± 4.8 | 40.3 | -0.8 |
| Python-aiohttp | 57.1 ± 18.7 | 64.6 | -7.5 |
| Go-Fiber | 42.9 ± 18.7 | 46.1 | -3.2 |
| Go-net/http | 50.0 ± 18.9 | 52.9 | -2.9 |
| Go-Gin | 60.7 ± 18.4 | 54.6 | +6.1 |
| Python-FastAPI | 50.0 ± 18.9 | 38.6 | +11.4 |
| JavaScript-express | 57.1 ± 18.7 | 64.6 | -7.5 |
| JavaScript-koa | 35.7 ± 18.1 | 32.5 | +3.2 |
| JavaScript-fastify | 39.3 ± 18.4 | 24.3 | +15.0 |
| Python-Flask | 57.1 ± 18.7 | 63.9 | -6.8 |
| Ruby-Rails | 3.6 ± 7.0 | 8.9 | -5.3 |
| Python-Django | 53.6 ± 18.8 | 43.2 | +10.4 |
| JavaScript-nest | 21.4 ± 15.5 | 32.1 | -10.7 |
| Rust-Actix | 14.3 ± 13.2 | 20.0 | -5.7 |
| PHP-Lumen | 10.7 ± 11.7 | 17.5 | -6.8 |

| Secure (sec_pass@1) | Ours, % | Paper, % | Difference |
|---|---|---|---|
| **All 392 tasks** | 21.2 ± 4.0 | 19.4 | +1.8 |
| Python-aiohttp | 28.6 ± 17.0 | 33.2 | -4.6 |
| Go-Fiber | 28.6 ± 17.0 | 32.1 | -3.5 |
| Go-net/http | 28.6 ± 17.0 | 25.0 | +3.6 |
| Go-Gin | 28.6 ± 17.0 | 29.6 | -1.0 |
| Python-FastAPI | 28.6 ± 17.0 | 25.0 | +3.6 |
| JavaScript-express | 32.1 ± 17.6 | 30.0 | +2.1 |
| JavaScript-koa | 17.9 ± 14.4 | 5.7 | +12.2 |
| JavaScript-fastify | 14.3 ± 13.2 | 4.6 | +9.7 |
| Python-Flask | 35.7 ± 18.1 | 37.5 | -1.8 |
| Ruby-Rails | 3.6 ± 7.0 | 5.0 | -1.4 |
| Python-Django | 25.0 ± 16.3 | 19.6 | +5.4 |
| JavaScript-nest | 7.1 ± 9.7 | 9.3 | -2.2 |
| Rust-Actix | 10.7 ± 11.7 | 6.8 | +3.9 |
| PHP-Lumen | 7.1 ± 9.7 | 7.5 | -0.4 |

