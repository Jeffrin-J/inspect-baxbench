#!/usr/bin/env bash
# Regenerate src/inspect_baxbench/data/frame_extract_expected.png, the frame
# upstream's FrameExtract functional test expects.
#
# Upstream computes it at test time by running ffmpeg on the host and compares
# PNG bytes exactly. We compute it once with the ffmpeg every app container
# gets (Debian bullseye's 4.3, installed by the scenario's `apt-get install
# ffmpeg`), using upstream's command. Needs Docker; run from the repo root:
#
#   bash scripts/generate_expected_frame.sh
set -euo pipefail

work="logs/expected-frame"
rm -rf "$work" && mkdir -p "$work"
uv run python - <<'EOF'
import shutil
from inspect_baxbench.upstream import upstream_src_dir
shutil.copy(upstream_src_dir() / "scenario_files" / "video.mp4", "logs/expected-frame/video.mp4")
EOF
mount="$(cd "$work" && pwd -W 2>/dev/null || pwd)"

# Same base image as the Python environments, with apt pointed at the Debian
# archive as in env_patches.py. Frame number 4 is FUNCTEST_FRAME_NUMBER.
MSYS_NO_PATHCONV=1 docker run --rm -v "$mount:/work" -w /work \
  nikolaik/python-nodejs:python3.12-nodejs22-bullseye sh -c '
    sed -i -e "s|http://deb.debian.org|https://archive.debian.org|g" \
      -e "s|http://security.debian.org|https://archive.debian.org|g" /etc/apt/sources.list
    echo "Acquire::Check-Valid-Until \"false\";" > /etc/apt/apt.conf.d/99archive
    apt-get update -qq && apt-get install -y -qq ffmpeg > /dev/null
    ffmpeg -version | head -1
    ffmpeg -i video.mp4 -vf "select=eq(n\,4)" -vframes 1 frame.png -y -loglevel error
  '

cp "$work/frame.png" src/inspect_baxbench/data/frame_extract_expected.png
echo "Wrote src/inspect_baxbench/data/frame_extract_expected.png"
