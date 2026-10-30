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
import re
from importlib import resources
from typing import Any

# Every upstream image is Debian 11 (bullseye), which reached end of life in
# August 2026. Its packages are leaving deb.debian.org (some already return
# 404), and some networks block plain HTTP to Debian's mirrors. This points apt
# at https://archive.debian.org, which serves the same packages and versions.
_DEBIAN_ARCHIVE_COMMAND = (
    "RUN sed -i -e 's|http://deb.debian.org|https://archive.debian.org|g' "
    "-e 's|http://security.debian.org|https://archive.debian.org|g' "
    "/etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null; "
    # Archived release files are past their Valid-Until date.
    "echo 'Acquire::Check-Valid-Until \"false\";' > /etc/apt/apt.conf.d/99baxbench-archive"
)
_FROM_LINE = re.compile(r"^FROM [^\n]+\n", re.MULTILINE)

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


def use_debian_archive_patch(env: Any) -> Any:
    """Return the Env with apt switched to the Debian archive right after FROM.

    It goes before every other instruction because some Dockerfiles (e.g.
    JavaScript-nest) run apt-get before the slot for extra build commands.
    """
    match = _FROM_LINE.search(env.dockerfile)
    if match is None or len(_FROM_LINE.findall(env.dockerfile)) != 1:
        raise RuntimeError(f"Expected one FROM line in the Dockerfile for {env.id}")
    end = match.end()
    dockerfile = env.dockerfile[:end] + _DEBIAN_ARCHIVE_COMMAND + "\n" + env.dockerfile[end:]
    return dataclasses.replace(env, dockerfile=dockerfile)


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
