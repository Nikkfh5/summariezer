from pathlib import Path
import unittest

from summariezer.config import load_config


class ConfigTests(unittest.TestCase):
    def test_example_config_defines_ai_profile(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        config = load_config(repo_root / "configs" / "example.toml")

        self.assertIn("ai", config.profiles)
        profile = config.profiles["ai"]
        self.assertEqual(profile.language, "ru")
        self.assertTrue(any("model releases" in item for item in profile.priorities))
        self.assertNotIn("What to try or verify next", profile.output_sections)
