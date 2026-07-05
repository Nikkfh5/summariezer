import unittest
from pathlib import Path

from summariezer.codex_runner import CodexRunner
from summariezer.models import CodexSettings


class CodexRunnerTests(unittest.TestCase):
    def test_places_global_approval_flag_before_exec_subcommand(self) -> None:
        runner = CodexRunner(
            CodexSettings(
                executable="codex",
                work_dir=Path("/tmp/project"),
                ask_for_approval="never",
            )
        )

        command = runner.build_command(Path("/tmp/out.md"))

        self.assertEqual(command[:4], ["codex", "--ask-for-approval", "never", "exec"])
        self.assertEqual(command[-1], "-")
