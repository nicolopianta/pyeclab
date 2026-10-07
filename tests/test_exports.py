import unittest


class Exports(unittest.TestCase):
    def test_star_import_of_the_techniques_works(self):
        namespace = {}
        exec("from pyeclab.techniques import *", namespace)   # __all__ must only name existing attributes
        for name in ("ChronoAmperometry", "ChronoAmperometryWithLimits", "ChronoPotentiometry",
                     "ChronoPotentiometryWithLimits", "Loop", "OpenCircuitVoltage"):
            self.assertIn(name, namespace)


if __name__ == "__main__":
    unittest.main()
