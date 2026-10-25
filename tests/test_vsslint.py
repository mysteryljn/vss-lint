import unittest
from vsslint import lint
class VssTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(lint({"signals":[{"path":"Vehicle.Body.IsLocked","description":"Whether it is locked","datatype":"boolean","access":"read"}]}),[])
    def test_errors(self):
        errors=lint({"signals":[{"path":"vehicle.bad","description":"x","datatype":"float","access":"read"},{"path":"vehicle.bad","description":"long enough description","datatype":"float","unit":"A","access":"bad"}]})
        self.assertTrue(any("duplicate" in e for e in errors)); self.assertTrue(any("unit" in e for e in errors))
    def test_unhashable_path_is_reported_without_crashing(self):
        errors = lint({"signals":[{"path":[],"description":"long enough description","datatype":"string","access":"read"}]})
        self.assertTrue(any("invalid logical path" in e for e in errors))
    def test_vss_64_bit_and_double_types_are_supported(self):
        signals = [
            {"path":"Vehicle.Power.EnergyCounter", "description":"Total energy counter", "datatype":"uint64", "unit":"Wh", "access":"read"},
            {"path":"Vehicle.Power.TorqueOffset", "description":"Signed torque offset", "datatype":"int64", "unit":"Nm", "access":"read"},
            {"path":"Vehicle.Power.Efficiency", "description":"Power conversion efficiency", "datatype":"double", "unit":"percent", "access":"read"},
        ]
        self.assertEqual(lint({"signals": signals}), [])
if __name__=="__main__": unittest.main()
