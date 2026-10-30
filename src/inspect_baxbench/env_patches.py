"""Pin build-time dependencies that upstream BaxBench leaves floating.

Upstream's Dockerfiles install some tools and libraries at their latest
version. Since v1.0.0 (Sep 2025) those have moved past the toolchains pinned in
the images, so the builds now fail. Each patch pins the newest version that
still works with the image's own toolchain, which is what upstream resolved
when it was published:

- Go: `goimports@latest` needs Go >= 1.26 (x/tools v0.52). v0.36.0 is the last
  release supporting the image's Go 1.23.
- Rust: there is no Cargo.lock, so crates resolve to versions needing a newer
  Rust than the image's 1.83 (e.g. clap_lex 1.1 needs edition 2024). We ship a
  lockfile with the newest Rust-1.83-compatible versions; see
  scripts/generate_cargo_lock.sh.
- Ruby: `gem install rails` installs 8.1, whose `rails new` config fails on the
  Rails ~> 8.0.1 the Gemfile pins. And the json gem, which the Gemfile leaves
  free, resolves to 3.x (Sep 2026), which rejects the `quirks_mode` option
  Rails 8.0 passes when parsing JSON request bodies; we add `json < 3` to the
  Gemfile used for the build (the prompt's package list is unchanged).

Patches raise if the text they replace is missing, so an upstream change is
noticed instead of silently skipped.
"""

import dataclasses
from importlib import resources
from typing import Any

_GO_PIN = (
    "RUN go install golang.org/x/tools/cmd/goimports@latest",
    "RUN go install golang.org/x/tools/cmd/goimports@v0.36.0",
)
_RUST_LOCK = ("COPY Cargo.toml Cargo.toml", "COPY Cargo.toml Cargo.lock ./")
_RAILS_PIN = ("RUN gem install rails\n", 'RUN gem install rails -v "~> 8.0.1"\n')


def _replace(dockerfile: str, old: str, new: str, env_id: str) -> str:
    if old not in dockerfile:
        raise RuntimeError(f"Upstream Dockerfile for {env_id} changed: {old!r} not found")
    return dockerfile.replace(old, new)


def patch_env(env: Any) -> Any:
    """Return the upstream Env with its floating dependencies pinned."""
    if env.language == "Go":
        return dataclasses.replace(env, dockerfile=_replace(env.dockerfile, *_GO_PIN, env.id))
    if env.language == "Rust":
        lock = resources.files("inspect_baxbench").joinpath("data/Cargo.lock").read_text()
        return dataclasses.replace(
            env,
            dockerfile=_replace(env.dockerfile, *_RUST_LOCK, env.id),
            manifest_files={**env.manifest_files, "Cargo.lock": lock},
        )
    if env.language == "Ruby":
        gemfile = env.manifest_files["Gemfile"] + '\ngem "json", "< 3"\n'
        return dataclasses.replace(
            env,
            dockerfile=_replace(env.dockerfile, *_RAILS_PIN, env.id),
            manifest_files={**env.manifest_files, "Gemfile": gemfile},
        )
    return env
