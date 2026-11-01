Model: `openrouter/deepseek/deepseek-chat` vs the paper's DeepSeek V3.
Our run: 392 samples (1 epoch(s)) at temperature 0.2.
Paper: 10 samples per task at temperature 0.4; 1 sample for o1, o3-mini and R1.

| Correct (pass@1) | Ours, % (95% CI) | Paper, % | Difference | Paper in CI |
|---|---|---|---|---|
| **All 392 tasks** | 39.5 (34.8-44.5) | 40.3 | -0.8 | yes |
| Python-aiohttp | 57.1 (39.1-73.5) | 64.6 | -7.5 | yes |
| Go-Fiber | 42.9 (26.5-60.9) | 46.1 | -3.2 | yes |
| Go-net/http | 50.0 (32.6-67.4) | 52.9 | -2.9 | yes |
| Go-Gin | 60.7 (42.4-76.4) | 54.6 | +6.1 | yes |
| Python-FastAPI | 50.0 (32.6-67.4) | 38.6 | +11.4 | yes |
| JavaScript-express | 57.1 (39.1-73.5) | 64.6 | -7.5 | yes |
| JavaScript-koa | 35.7 (20.7-54.2) | 32.5 | +3.2 | yes |
| JavaScript-fastify | 39.3 (23.6-57.6) | 24.3 | +15.0 | yes |
| Python-Flask | 57.1 (39.1-73.5) | 63.9 | -6.8 | yes |
| Ruby-Rails | 3.6 (0.6-17.7) | 8.9 | -5.3 | yes |
| Python-Django | 53.6 (35.8-70.5) | 43.2 | +10.4 | yes |
| JavaScript-nest | 21.4 (10.2-39.5) | 32.1 | -10.7 | yes |
| Rust-Actix | 14.3 (5.7-31.5) | 20.0 | -5.7 | yes |
| PHP-Lumen | 10.7 (3.7-27.2) | 17.5 | -6.8 | yes |

| Secure (sec_pass@1) | Ours, % (95% CI) | Paper, % | Difference | Paper in CI |
|---|---|---|---|---|
| **All 392 tasks** | 19.1 (15.5-23.3) | 19.4 | -0.3 | yes |
| Python-aiohttp | 25.0 (12.7-43.4) | 33.2 | -8.2 | yes |
| Go-Fiber | 21.4 (10.2-39.5) | 32.1 | -10.7 | yes |
| Go-net/http | 25.0 (12.7-43.4) | 25.0 | +0.0 | yes |
| Go-Gin | 21.4 (10.2-39.5) | 29.6 | -8.2 | yes |
| Python-FastAPI | 28.6 (15.3-47.1) | 25.0 | +3.6 | yes |
| JavaScript-express | 32.1 (17.9-50.7) | 30.0 | +2.1 | yes |
| JavaScript-koa | 17.9 (7.9-35.6) | 5.7 | +12.2 | **no** |
| JavaScript-fastify | 10.7 (3.7-27.2) | 4.6 | +6.1 | yes |
| Python-Flask | 35.7 (20.7-54.2) | 37.5 | -1.8 | yes |
| Ruby-Rails | 3.6 (0.6-17.7) | 5.0 | -1.4 | yes |
| Python-Django | 25.0 (12.7-43.4) | 19.6 | +5.4 | yes |
| JavaScript-nest | 7.1 (2.0-22.6) | 9.3 | -2.2 | yes |
| Rust-Actix | 7.1 (2.0-22.6) | 6.8 | +0.3 | yes |
| PHP-Lumen | 7.1 (2.0-22.6) | 7.5 | -0.4 | yes |

