"""Make upstream's tests independent of the host they run on.

- FrameExtract: upstream's functional test computes the frame it expects by
  running ffmpeg on the host, then compares PNG bytes exactly. That fails
  without ffmpeg on the host, and a host ffmpeg other than the containers'
  Debian bullseye 4.3 can encode the PNG differently. We ship the frame
  computed with the containers' ffmpeg (scripts/generate_expected_frame.sh).
- Database downloads: tests that check how passwords are stored copy the app's
  SQLite file to a temporary directory on the host. On Windows, deleting that
  directory fails while the file is still open (upstream's `with
  sqlite3.connect(...)` doesn't close the connection, and virus scanners open
  new files briefly), and the test then raises, so no CWE is recorded. We
  retry the deletion instead. What the tests check is unchanged.
"""

import gc
import shutil
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from importlib import resources
from typing import Any


def _expected_frame(logger: object) -> bytes:
    return (
        resources.files("inspect_baxbench").joinpath("data/frame_extract_expected.png").read_bytes()
    )


def _remove_dir(path: str, attempts: int = 10) -> None:
    for _ in range(attempts):
        # Closes sqlite3 connections the tests left unreferenced but open.
        gc.collect()
        try:
            shutil.rmtree(path)
            return
        except OSError:
            time.sleep(0.5)
    # Leave the copy behind rather than fail the test.
    shutil.rmtree(path, ignore_errors=True)


@contextmanager
def _download_db_from_docker(container_id: str, env: Any) -> Iterator[str]:
    """Upstream's exploits.download_db_from_docker, with a robust cleanup."""
    import exploits

    db = exploits.load_file_from_docker(container_id, env.workdir + "/" + env.sqlite_database)
    tempdir = tempfile.mkdtemp()
    try:
        filename = tempdir + "/" + env.sqlite_database
        with open(filename, "wb") as f:
            f.write(db)
        yield filename
    finally:
        _remove_dir(tempdir)


def patch_scenarios() -> None:
    """Patch upstream's test modules. Needs upstream on sys.path."""
    import exploits
    import scenarios.frame_extract

    # The tests look these up as module globals when they run.
    scenarios.frame_extract._ENCODED_FRAME = _expected_frame
    exploits.download_db_from_docker = _download_db_from_docker
