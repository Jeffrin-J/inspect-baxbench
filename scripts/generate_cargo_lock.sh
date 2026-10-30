#!/usr/bin/env bash
# Regenerate src/inspect_baxbench/data/Cargo.lock for the Rust-Actix environment.
#
# Uses Cargo's MSRV-aware resolver (Cargo >= 1.84) to pick the newest crate
# versions that support Rust 1.83, the toolchain in upstream's rust:1.83.0
# image, then checks the app builds with that image. Needs Docker; run from the
# repo root:
#
#   bash scripts/generate_cargo_lock.sh
set -euo pipefail

work="logs/cargo-lock"
rm -rf "$work" && mkdir -p "$work/src"
uv run python - <<'EOF'
from inspect_baxbench.upstream import load_upstream
_, envs = load_upstream()
toml = envs["Rust-Actix"].manifest_files["Cargo.toml"]
open("logs/cargo-lock/Cargo.toml", "w", newline="\n").write(
    toml.replace('edition = "2021"', 'edition = "2021"\nrust-version = "1.83"')
)
EOF
cp tests/apps/logger_rust/main.rs "$work/src/main.rs"
mount="$(cd "$work" && pwd -W 2>/dev/null || pwd)"

# Resolve with a rust-version hint, then build with upstream's own image and
# upstream's unmodified Cargo.toml.
MSYS_NO_PATHCONV=1 docker run --rm -e CARGO_RESOLVER_INCOMPATIBLE_RUST_VERSIONS=fallback \
  -v "$mount:/work" -w /work rust:1.88 cargo generate-lockfile
sed -i '/^rust-version = "1.83"$/d' "$work/Cargo.toml"
MSYS_NO_PATHCONV=1 docker run --rm -v "$mount:/work" -w /work rust:1.83.0-bullseye cargo build --locked

cp "$work/Cargo.lock" src/inspect_baxbench/data/Cargo.lock
echo "Wrote src/inspect_baxbench/data/Cargo.lock"
