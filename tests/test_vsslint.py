import unittest
from vsslint import lint
class VssTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(lint({"signals":[{"path":"Vehicle.Body.IsLocked","description":"Whether it is locked","datatype":"boolean","access":"read"}]}),[])
    def test_errors(self):
        errors=lint({"signals":[{"path":"vehicle.bad","description":"x","datatype":"float","access":"read"},{"path":"vehicle.bad","description":"long enough description","datatype":"float","unit":"A","access":"bad"}]})
        self.assertTrue(any("duplicate" in e for e in errors)); self.assertTrue(any("unit" in e for e in errors))
if __name__=="__main__": unittest.main()
