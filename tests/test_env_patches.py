"""Checks that the dependency pins apply to upstream's Dockerfiles. Loading
upstream connects to Docker, so these run with RUN_DOCKER_TESTS=1 only."""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_DOCKER_TESTS") != "1",
    reason="needs Docker; set RUN_DOCKER_TESTS=1",
)


@pytest.fixture(scope="module")
def envs():
    from inspect_baxbench.upstream import load_upstream

    return load_upstream()[1]


def test_go_pins_goimports(envs):
    from inspect_baxbench.env_patches import patch_env

    for env_id in ("Go-Fiber", "Go-Gin", "Go-net/http"):
        dockerfile = patch_env(envs[env_id]).dockerfile
        assert "goimports@v0.36.0" in dockerfile
        assert "@latest" not in dockerfile


def test_rust_ships_lockfile(envs):
    from inspect_baxbench.env_patches import patch_env

    env = patch_env(envs["Rust-Actix"])
    assert "COPY Cargo.toml Cargo.lock ./" in env.dockerfile
    assert env.manifest_files["Cargo.lock"].startswith("# This file is automatically @generated")


def test_rails_pins_version(envs):
    from inspect_baxbench.env_patches import patch_env

    env = patch_env(envs["Ruby-Rails"])
    assert 'gem install rails -v "~> 8.0.1"' in env.dockerfile
    assert env.manifest_files["Gemfile"].rstrip().endswith('gem "json", "< 3"')


def test_debian_archive_comes_before_any_apt_get(envs):
    from inspect_baxbench.env_patches import use_debian_archive_patch

    for env_id, env in envs.items():
        dockerfile = use_debian_archive_patch(env).dockerfile
        archive = dockerfile.index("archive.debian.org")
        assert dockerfile.index("FROM ") < archive, env_id
        if "apt-get" in dockerfile[:archive]:
            raise AssertionError(f"{env_id}: apt-get runs before the archive switch")


def test_other_envs_are_unchanged(envs):
    from inspect_baxbench.env_patches import patch_env

    for env in envs.values():
        if env.language not in ("Go", "Rust", "Ruby"):
            assert patch_env(env) is env
