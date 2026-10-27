import pytest

from inspect_baxbench.dataset import baxbench_dataset
from inspect_baxbench.prompts import build_prompt


@pytest.fixture(scope="module")
def dataset():
    return baxbench_dataset()


def test_full_dataset_has_392_unique_tasks(dataset):
    assert len(dataset) == 392
    assert len({s.id for s in dataset}) == 392
    assert len({s.metadata["env_id"] for s in dataset}) == 14
    assert len({s.metadata["scenario_id"] for s in dataset}) == 28


def test_filter_by_env_and_scenario():
    dataset = baxbench_dataset(envs=["Python-Flask"], scenarios=["Calculator", "Login"])
    assert sorted(s.id for s in dataset) == ["Calculator-Python-Flask", "Login-Python-Flask"]


def test_filter_accepts_single_string():
    dataset = baxbench_dataset(envs="Python-Flask", scenarios="Calculator")
    assert [s.id for s in dataset] == ["Calculator-Python-Flask"]


def test_unknown_env_raises():
    with pytest.raises(ValueError, match="Unknown envs"):
        baxbench_dataset(envs=["Python-Flsk"])


def test_unknown_scenario_raises():
    with pytest.raises(ValueError, match="Unknown scenarios"):
        baxbench_dataset(scenarios=["Calculater"])


def test_openapi_prompt_contains_spec_and_format(dataset):
    sample = next(s for s in dataset if s.id == "Calculator-Python-Flask")
    assert "OpenAPI schema" in sample.input
    assert "/calculator" in sample.input
    assert "using the Flask framework" in sample.input
    assert "<CODE>" in sample.input
    assert "0.0.0.0:5000" in sample.input


def test_multifile_env_uses_filepath_format_only(dataset):
    sample = next(s for s in dataset if s.metadata["env_multifile"])
    assert "<FILEPATH>" in sample.input
    assert "Do not return anything besides code" not in sample.input


def test_install_commands_come_from_upstream_v1(dataset):
    # The HF dataset still has Alpine `apk add` commands; v1.0.0 uses Debian.
    sample = next(s for s in dataset if s.id == "FrameExtract-Python-Flask")
    assert "apt-get install ffmpeg -y" in sample.input
    assert not any("apk add" in s.input for s in dataset)


def test_specs_come_from_upstream_v1(dataset):
    # v1.0.0 reworded FrameExtract to extract frames by index, not by second.
    sample = next(s for s in dataset if s.id == "FrameExtract-Python-Flask")
    assert "frame at the specified index" in sample.input
    assert "frame at the specified second" not in sample.input


def test_song_downloader_instructions_resolve_storage_dir(dataset):
    sample = next(s for s in dataset if s.id == "SongDownloader-Python-Flask")
    assert "The songs are stored in the /var/songs directory." in sample.input


def test_db_instructions_only_when_needed(dataset):
    for sample in dataset:
        has_db_text = "sqlite3 database named db.sqlite3" in sample.input
        assert has_db_text == sample.metadata["needs_db"]


def _record(**overrides):
    record = dict(
        short_app_description="calculator web app",
        env_framework="Flask",
        env_language="Python",
        scenario_instructions="",
        env_multifile=False,
        needs_db=False,
        needs_secret=False,
        allowed_packages="\nFlask==3.1.0\n",
        needed_packages={"_all_": None, "Python": None},
        env_instructions="Put all code in one file! Do not create any additional files!",
        port=5000,
        potential_cwes=[703, 94, 400],
        api_specification="openapi: 3.0.3",
        text_specification="A calculator.",
    )
    record.update(overrides)
    return record


def test_specific_safety_prompt_lists_cwes_sorted():
    prompt = build_prompt(_record(), "openapi", "specific")
    cwe_lines = [line for line in prompt.split("\n") if line.startswith("CWE-")]
    assert [line.split(":")[0] for line in cwe_lines] == ["CWE-94", "CWE-400", "CWE-703"]


def test_safety_prompt_none_has_no_security_text():
    prompt = build_prompt(_record(), "openapi", "none")
    assert "best practices for security" not in prompt


def test_text_spec_uses_text_specification():
    prompt = build_prompt(_record(), "text", "none")
    assert "A calculator." in prompt
    assert "OpenAPI" not in prompt


def test_needed_packages_are_appended():
    record = _record(needed_packages={"_all_": ["ffmpeg"], "Python": ["pillow"]})
    prompt = build_prompt(record, "openapi", "none")
    assert "the following packages have been installed for this task\nffmpeg\npillow" in prompt


def test_invalid_options_raise():
    with pytest.raises(ValueError):
        build_prompt(_record(), "yaml", "none")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        build_prompt(_record(), "openapi", "paranoid")  # type: ignore[arg-type]
