# Puts the services root on sys.path under the module names the containers
# use. Must precede the service imports below. See src/__init__.py.
import src  # noqa: F401
import unittest
from ingestion.app.sanitizer import LaTeXSanitizer

class TestLaTeXSanitizer(unittest.TestCase):
    def test_strip_det_tokens(self):
        raw = "Here is an equation <|det|> \\det(A) = 0."
        cleaned = LaTeXSanitizer.sanitize(raw)
        self.assertNotIn("<|det|>", cleaned)
        self.assertIn("\\det(A) = 0", cleaned)

    def test_display_math_normalization(self):
        raw = "The formula is:\n\\[ A x = \\lambda x \\]"
        cleaned = LaTeXSanitizer.sanitize(raw)
        self.assertIn("$$", cleaned)
        self.assertNotIn("\\[", cleaned)

    def test_inline_math_normalization(self):
        raw = "Given vector \\(v \\in V\\), we calculate its norm."
        cleaned = LaTeXSanitizer.sanitize(raw)
        self.assertIn("$v \\in V$", cleaned)

if __name__ == "__main__":
    unittest.main()
