import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from vsslint import lint, main


def catalog(*paths):
    return {"signals": [
        {"path": path, "description": "Current vehicle state", "datatype": "string", "access": "read"}
        for path in paths
    ]}


class HierarchyTests(unittest.TestCase):
    def test_leaf_cannot_also_be_an_ancestor_in_either_input_order(self):
        for paths in (
            ("Vehicle.Body", "Vehicle.Body.Mode"),
            ("Vehicle.Body.Mode", "Vehicle.Body"),
            ("Vehicle.Body", "Vehicle.Body.Door.FrontLeft.Mode"),
        ):
            with self.subTest(paths=paths):
                errors = lint(catalog(*paths))
                self.assertTrue(any("signal path is also an ancestor" in error for error in errors), errors)
                self.assertTrue(any("Vehicle.Body" in error for error in errors), errors)

    def test_shared_branches_and_text_prefixes_remain_valid(self):
        self.assertEqual(lint(catalog(
            "Vehicle.Body.Mode", "Vehicle.Body.State", "Vehicle.Bodywork.Mode",
            "Vehicle.Power", "Vehicle.Powertrain.Mode",
        )), [])

    def test_cli_rejects_real_json_with_leaf_branch_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "signals.json"
            path.write_text(json.dumps(catalog("Vehicle.Body.Mode", "Vehicle.Body")), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main([str(path)])
            self.assertEqual(result, 1)
            self.assertIn("signal path is also an ancestor", output.getvalue())


if __name__ == "__main__":
    unittest.main()
