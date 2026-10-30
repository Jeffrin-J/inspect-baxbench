"""Build a generated app's Docker image and run BaxBench's tests against it.

Mirrors upstream's `Task.test_code` and `ContainerRunner` (src/tasks.py,
v1.0.0): build one image per sample, start a fresh container for every
functional and security test, wait for the server to answer, run the test in a
subprocess with a timeout, and treat a server process that dies during a test
as CWE-703. Differences from upstream:

- The host port is picked by Docker instead of upstream's port pool.
- The image is removed after testing, so long runs don't fill the disk.
- By default, apt is pointed at https://archive.debian.org right after FROM, and
  floating build dependencies are pinned (see env_patches.py).
- Tests that need tools on the host are patched (see scenario_patches.py).
- Each container's log is cut to its last 2,000 characters.

This module is blocking and talks to Docker directly; the scorer runs it in a
worker thread.
"""

import logging
import multiprocessing
import tempfile
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import docker
import requests

from inspect_baxbench.env_patches import patch_env, use_debian_archive_patch
from inspect_baxbench.scenario_patches import patch_scenarios
from inspect_baxbench.upstream import add_upstream_to_path, load_upstream

# Upstream defaults: 300 s per test (src/main.py), 1 GB container memory limit.
DEFAULT_TEST_TIMEOUT = 300
_MEMORY_LIMIT = 2**30
# Container output (e.g. ffmpeg's banner) can be long; keep the end of each, so
# the test failures around it still fit in the scorer's log excerpt.
_MAX_CONTAINER_LOG_CHARS = 2_000
# CWE-703 and CWE-400, as upstream's CWE enum names them.
_CWE_EXCEPTIONAL_CONDITIONS = "IMPROPER_CHECK_OR_HANDLING_OF_EXCEPTIONAL_CONDITIONS"
_CWE_RESOURCE_CONSUMPTION = "UNCONTROLLED_RESOURCE_CONSUMPTION"


@dataclass
class TestOutcome:
    """Per-sample test results, matching upstream's TestResult."""

    build_failed: bool = False
    num_passed_ft: int = 0
    num_total_ft: int = 0
    num_ft_exceptions: int = 0
    num_total_st: int = 0
    num_st_exceptions: int = 0
    cwes: set[int] = field(default_factory=set)
    log: str = ""

    @property
    def functionally_correct(self) -> bool:
        return self.num_passed_ft == self.num_total_ft

    @property
    def secure(self) -> bool:
        return len(self.cwes) == 0

    def record_ft(self, passed: bool, had_exception: bool) -> None:
        self.num_total_ft += 1
        self.num_passed_ft += int(passed)
        self.num_ft_exceptions += int(had_exception)

    def record_st(self, cwes: set[Any] | None) -> None:
        self.num_total_st += 1
        if cwes is None:
            self.num_st_exceptions += 1
        else:
            self.cwes |= {cwe.value["num"] for cwe in cwes}


class _Container:
    """A running app container, started like upstream's ContainerRunner."""

    def __init__(self, env: Any, image_id: str, logger: logging.Logger) -> None:
        self.env = env
        self.image_id = image_id
        self.logger = logger
        self.client = docker.from_env()

    def __enter__(self) -> "_Container":
        self.container = self.client.containers.run(
            self.image_id,
            name=f"baxbench-{uuid.uuid4()}",
            detach=True,
            ports={f"{self.env.port}/tcp": None},
            auto_remove=False,
            mem_limit=_MEMORY_LIMIT,
        )
        try:
            self.container.reload()
            self.port = int(self.container.ports[f"{self.env.port}/tcp"][0]["HostPort"])
            self._wait_for_server()
        except BaseException:
            self._remove()
            raise
        return self

    def _wait_for_server(self) -> None:
        start = time.time()
        while True:
            try:
                requests.get(f"http://localhost:{self.port}")
                self.logger.info("Server is up")
                return
            except requests.ConnectionError:
                pass
            if time.time() - start > self.env.wait_to_start_time:
                raise TimeoutError("Server did not start in time")
            time.sleep(1.0)

    def __exit__(self, *exc_info: Any) -> None:
        self._remove()

    def _remove(self) -> None:
        logs = self.container.logs(stdout=True, stderr=True, follow=False)
        text = logs.decode(errors="replace")
        if len(text) > _MAX_CONTAINER_LOG_CHARS:
            omitted = len(text) - _MAX_CONTAINER_LOG_CHARS
            text = f"[{omitted} chars omitted]\n" + text[-_MAX_CONTAINER_LOG_CHARS:]
        self.logger.info("container logs:\n%s", text)
        self.container.remove(force=True)


def _init_test_worker() -> None:
    # The worker is spawned, so it needs upstream on its sys.path and its own
    # copy of the scenario patches.
    add_upstream_to_path()
    patch_scenarios()


def _run_with_timeout(test: Callable[[Any], Any], app: Any, timeout: int) -> Any:
    # Tests run in a fresh process (as upstream does) so a hung test can be killed.
    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(processes=1, initializer=_init_test_worker) as pool:
        result = pool.apply_async(test, [app])
        try:
            return result.get(timeout=timeout)
        except multiprocessing.TimeoutError:
            pool.terminate()
            raise TimeoutError(f"Test {test.__name__} timed out") from None


def _run_test(
    test: Callable[[Any], Any],
    env: Any,
    image_id: str,
    log_dir: Path,
    timeout: int,
    logger: logging.Logger,
) -> tuple[Any, bool]:
    """Run one test in a fresh container. Returns (result, server_crashed)."""
    from scenarios.base import AppInstance

    with _Container(env, image_id, logger) as c:
        ran_before = env.process_still_running(c.container.id, logger)
        app = AppInstance(
            port=c.port,
            log_file_path=log_dir / f"{test.__name__}.log",
            container_id=c.container.id,
            env=env,
        )
        result = _run_with_timeout(test, app, timeout)
        crashed = ran_before and not env.process_still_running(c.container.id, logger)
        return result, crashed


def run_tests(
    scenario_id: str,
    env_id: str,
    files: dict[str, str],
    timeout: int = DEFAULT_TEST_TIMEOUT,
    use_debian_archive: bool = True,
) -> TestOutcome:
    """Build the app and run every functional and security test for its scenario."""
    scenarios, envs = load_upstream()
    from cwes import CWE
    from env.base import COMMON_DOCKER_RUN_COMMANDS

    scenario, env = scenarios[scenario_id], patch_env(envs[env_id])
    outcome = TestOutcome()

    with tempfile.TemporaryDirectory(prefix="baxbench-") as tmp:
        log_dir = Path(tmp)
        logger = logging.getLogger(f"baxbench.{uuid.uuid4()}")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        handler = logging.FileHandler(log_dir / "test.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        try:
            if use_debian_archive:
                env = use_debian_archive_patch(env)
            image_id = _build_image(scenario, env, files, COMMON_DOCKER_RUN_COMMANDS, logger)
            if image_id is None:
                outcome.build_failed = True
                for _ in scenario.functional_tests:
                    outcome.record_ft(passed=False, had_exception=True)
                for _ in scenario.security_tests:
                    outcome.record_st(None)
                return outcome

            try:
                for test in scenario.functional_tests:
                    passed, had_exception = False, False
                    try:
                        passed, crashed = _run_test(test, env, image_id, log_dir, timeout, logger)
                        if crashed:
                            logger.warning("server crashed during functional test")
                            outcome.record_st({CWE[_CWE_EXCEPTIONAL_CONDITIONS]})
                    except Exception:
                        logger.exception("functional test %s raised", test.__name__)
                        had_exception = True
                    outcome.record_ft(passed=bool(passed), had_exception=had_exception)

                for test in scenario.security_tests:
                    cwes = None
                    try:
                        cwes, crashed = _run_test(test, env, image_id, log_dir, timeout, logger)
                        if crashed:
                            logger.warning("server crashed during security test")
                            cwes = set(cwes or ())
                            # Upstream adds 703 unless resource exhaustion caused the crash.
                            if CWE[_CWE_RESOURCE_CONSUMPTION] not in cwes:
                                cwes.add(CWE[_CWE_EXCEPTIONAL_CONDITIONS])
                    except Exception:
                        logger.exception("security test %s raised", test.__name__)
                    outcome.record_st(cwes)
            finally:
                try:
                    docker.from_env().images.remove(image_id, force=True)
                except docker.errors.APIError:
                    logger.warning("could not remove image %s", image_id)
        finally:
            handler.close()
            logger.removeHandler(handler)
            outcome.log = _read_logs(log_dir)
    return outcome


def _build_image(
    scenario: Any,
    env: Any,
    files: dict[str, str],
    common_commands: list[str],
    logger: logging.Logger,
) -> str | None:
    commands = (
        common_commands
        + scenario.needed_packages.get("_all_", [])
        + scenario.needed_packages.get(env.language, [])
    )
    # Upstream adds each file to the build tarball as str(path); PurePosixPath
    # keeps forward slashes on Windows, where Path would give "src\\main.ts".
    paths = {PurePosixPath(p): code for p, code in files.items()}
    # Upstream retries once without the build cache before giving up.
    for no_cache in (False, True):
        try:
            image_id: str = env.build_docker_image(paths, commands, logger, no_cache=no_cache)
            return image_id
        except Exception:
            logger.exception("image build failed (no_cache=%s)", no_cache)
    return None


def _read_logs(log_dir: Path) -> str:
    parts = []
    for path in sorted(log_dir.glob("*.log")):
        parts.append(f"===== {path.name}\n{path.read_text(encoding='utf-8', errors='replace')}")
    return "\n".join(parts)
