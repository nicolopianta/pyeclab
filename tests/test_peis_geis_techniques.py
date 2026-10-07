"""PEIS / GEIS techniques and the channel that decodes their frequency-sweep results (no instrument needed)."""
import unittest

import pyeclab
from pyeclab.api.kbio_types import I_RANGE
from pyeclab.techniques import GEISTechnique, PEISTechnique


class FakeDevice:
    """Records the parameters a technique defines instead of talking to the instrument."""

    def __init__(self, is_VMP3=True):
        self.is_VMP3 = is_VMP3
        self.defined = []

    def DefineParameter(self, label, value, index, parm):
        self.defined.append((label, value, index))


def peis(device, **kw):
    args = dict(
        device=device, vs_initial=False, initial_voltage_step=0.1, duration_step=60.0, record_every_dT=0.0,
        record_every_dI=0.0, initial_frequency=1e5, final_frequency=1.0, sweep_linear=False, amplitude_voltage=0.01,
        frequency_number=10, average_n_times=3, correction=True, wait_for_steady=1.0,
    )
    return PEISTechnique(**{**args, **kw})


def geis(device, **kw):
    args = dict(
        device=device, vs_initial=True, initial_current_step=1e-4, duration_step=30.0, record_every_dT=0.0,
        record_every_dE=0.0, initial_frequency=1e4, final_frequency=10.0, sweep_linear=True, amplitude_current=1e-5,
        frequency_number=5, average_n_times=2, correction=False, wait_for_steady=0.5, i_range=I_RANGE.I_RANGE_100uA,
    )
    return GEISTechnique(**{**args, **kw})


class Techniques(unittest.TestCase):
    def test_peis_parameters_follow_the_manual(self):
        device = FakeDevice()
        technique = peis(device)
        technique.make_technique()
        self.assertEqual([label for label, _, _ in device.defined], [
            "vs_initial", "Initial_Voltage_step", "Duration_step", "Record_every_dT", "Record_every_dI",
            "Final_frequency", "Initial_frequency", "sweep", "Amplitude_Voltage", "Frequency_number",
            "Average_N_times", "Correction", "Wait_for_steady",
        ])                                                   # no I_Range / E_Range / Bandwidth, no xctr
        values = {label: value for label, value, _ in device.defined}
        self.assertEqual((values["Initial_frequency"], values["Final_frequency"], values["Frequency_number"]), (1e5, 1.0, 10))
        self.assertEqual(technique.ecc_file, "peis.ecc")
        self.assertEqual(technique.ecc_params.len, 13)

    def test_geis_parameters_follow_the_manual(self):
        device = FakeDevice(is_VMP3=False)
        technique = geis(device)
        technique.make_technique()
        labels = [label for label, _, _ in device.defined]
        self.assertEqual(labels[:2], ["vs_initial", "Initial_Current_step"])
        self.assertEqual(labels[-1], "I_Range")                # GEIS takes I_Range, not E_Range / Bandwidth
        self.assertNotIn("E_Range", labels)
        self.assertEqual(dict((label, value) for label, value, _ in device.defined)["I_Range"], I_RANGE.I_RANGE_100uA.value)
        self.assertEqual(technique.ecc_file, "geis4.ecc")
        self.assertEqual(technique.ecc_params.len, 14)

    def test_external_control_adds_xctr_only_when_set(self):
        for build in (peis, geis):
            device = FakeDevice()
            build(device, xctr=8).make_technique()
            self.assertEqual(device.defined[-1][:2], ("xctr", 8))
            device = FakeDevice()
            build(device).make_technique()
            self.assertNotIn("xctr", [label for label, _, _ in device.defined])

    def test_are_exported(self):
        import pyeclab.techniques as techniques
        self.assertIn("PEISTechnique", techniques.__all__)
        self.assertIn("GEISTechnique", techniques.__all__)


if __name__ == "__main__":
    unittest.main()
