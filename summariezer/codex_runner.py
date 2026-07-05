from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .models import CodexSettings


@dataclass(frozen=True)
class CodexRunResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    output_path: Path


class CodexRunner:
    def __init__(self, settings: CodexSettings) -> None:
        self.settings = settings

    def build_command(self, output_path: Path) -> list[str]:
        command = [self.settings.executable]
        if self.settings.ask_for_approval:
            command.extend(["--ask-for-approval", self.settings.ask_for_approval])
        command.append("exec")
        if self.settings.model:
            command.extend(["--model", self.settings.model])
        command.extend(["--cd", str(self.settings.work_dir)])
        command.extend(["--sandbox", self.settings.sandbox])
        if self.settings.ephemeral:
            command.append("--ephemeral")
        command.extend(["--output-last-message", str(output_path)])
        command.extend(self.settings.extra_args)
        command.append("-")
        return command

    def run(self, prompt_path: Path, output_path: Path) -> CodexRunResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = self.build_command(output_path)
        with prompt_path.open("rb") as prompt_file:
            completed = subprocess.run(
                command,
                stdin=prompt_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        return CodexRunResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout.decode("utf-8", errors="replace"),
            stderr=completed.stderr.decode("utf-8", errors="replace"),
            output_path=output_path,
        )
