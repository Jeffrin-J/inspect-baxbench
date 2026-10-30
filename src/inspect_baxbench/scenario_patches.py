"""Remove upstream tests' dependencies on tools installed on the host.

Upstream's FrameExtract functional test computes the frame it expects by
running ffmpeg on the host, then compares PNG bytes exactly. That fails
without ffmpeg on the host, and a host ffmpeg other than the containers'
Debian bullseye 4.3 can encode the PNG differently. We ship the frame computed
with the containers' ffmpeg (scripts/generate_expected_frame.sh) instead.
"""

from importlib import resources


def _expected_frame(logger: object) -> bytes:
    return (
        resources.files("inspect_baxbench")
        .joinpath("data/frame_extract_expected.png")
        .read_bytes()
    )


def patch_scenarios() -> None:
    """Patch upstream's scenario modules. Needs upstream on sys.path."""
    import scenarios.frame_extract

    # The test looks this up as a module global when it runs.
    scenarios.frame_extract._ENCODED_FRAME = _expected_frame
