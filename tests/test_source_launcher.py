"""Source launcher profile writes are an explicit user action."""

import os
import subprocess
import sys
from pathlib import Path


def test_profile_shortcuts_are_opt_in_and_repeatable(tmp_path):
    launcher = Path(__file__).resolve().parents[1] / "omnisuite"
    env = {**os.environ, "HOME": str(tmp_path)}
    zsh = tmp_path / ".zshrc"
    bash = tmp_path / ".bashrc"
    original = "alias omnidebate='my-debate'\n"
    zsh.write_text(original)
    command = [sys.executable, str(launcher)]
    subprocess.run([*command, "--help"], env=env, check=True)
    assert zsh.read_text() == original
    assert not bash.exists()
    subprocess.run([*command, "--install-aliases"], env=env, check=True)
    assert zsh.read_text().startswith(original)
    for profile in (bash, zsh):
        assert profile.read_text().count("alias omnidebate=") == 1
        assert profile.read_text().count("alias omniformat=") == 1
    contents = [profile.read_text() for profile in (bash, zsh)]
    subprocess.run([*command, "--install-aliases"], env=env, check=True)
    assert [profile.read_text() for profile in (bash, zsh)] == contents
