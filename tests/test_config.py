# Puts the services root on sys.path under the module names the containers
# use. Must precede the service imports below. See src/__init__.py.
import src  # noqa: F401
import unittest
from shared.config import get_settings

class TestSettings(unittest.TestCase):
    def test_settings_load(self):
        settings = get_settings()
        self.assertIsNotNone(settings.gemini_api_key)
        self.assertIsNotNone(settings.obsidian_vault_location)
        self.assertTrue(len(settings.gemini_api_key) > 0)

if __name__ == "__main__":
    unittest.main()
