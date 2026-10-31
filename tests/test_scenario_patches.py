"""Checks the patches to upstream's tests. Importing upstream's scenarios
connects to Docker, so these run with RUN_DOCKER_TESTS=1 only."""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_DOCKER_TESTS") != "1",
    reason="needs Docker; set RUN_DOCKER_TESTS=1",
)


def test_frame_extract_uses_shipped_frame():
    from inspect_baxbench.scenario_patches import patch_scenarios
    from inspect_baxbench.upstream import add_upstream_to_path

    add_upstream_to_path()
    patch_scenarios()
    import scenarios.frame_extract

    # Runs without ffmpeg on the host.
    frame = scenarios.frame_extract._ENCODED_FRAME(None)
    assert frame.startswith(b"\x89PNG\r\n\x1a\n")


def test_db_download_survives_open_file(monkeypatch):
    from inspect_baxbench.scenario_patches import patch_scenarios
    from inspect_baxbench.upstream import add_upstream_to_path

    add_upstream_to_path()
    patch_scenarios()
    import exploits

    monkeypatch.setattr(exploits, "load_file_from_docker", lambda *_: b"SQLite format 3\0")

    class Env:
        workdir = "/app"
        sqlite_database = "db.sqlite3"

    # Hold the copied file open across cleanup, as an unclosed connection or a
    # virus scanner does on Windows; the download must not raise.
    with exploits.download_db_from_docker("container", Env()) as path:
        handle = open(path, "rb")  # noqa: SIM115
    handle.close()
