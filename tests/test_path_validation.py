import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from vsslint import lint, main


class PathValidationTests(unittest.TestCase):
    @staticmethod
    def catalog(path):
        return {"signals": [{
            "path": path,
            "description": "Current vehicle speed",
            "datatype": "float",
            "unit": "km/h",
            "access": "read",
        }]}

    def test_path_must_match_in_full_including_trailing_newline(self):
        self.assertEqual(lint(self.catalog("Vehicle.Speed")), [])
        for suffix in ("\n", "\r\n", " ", "\t", "\nOther"):
            with self.subTest(suffix=repr(suffix)):
                self.assertIn(
                    "signals[0]: invalid logical path",
                    lint(self.catalog("Vehicle.Speed" + suffix)),
                )

    def test_cli_rejects_json_escaped_newline_in_path(self):
        # JSON escapes preserve the newline in the logical signal identity.
        # Accepting it creates a different key from Vehicle.Speed downstream.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "signals.json"
            path.write_text(
                json.dumps(self.catalog("Vehicle.Speed\n")), encoding="utf-8"
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = main([str(path)])
        self.assertEqual(status, 1)
        self.assertIn("invalid logical path", output.getvalue())


if __name__ == "__main__":
    unittest.main()
