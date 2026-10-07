"""
GEIS (Galvano Electrochemical Impedance Spectroscopy, technique ID 107): EC-Lab's own single-sine impedance
technique with a controlled current.

Same shape as PEIS (see peis.py); parameters from the "EC-Lab Development Package" manual, section 7.13. GEIS
takes I_Range (but not E_Range / Bandwidth).
"""
from dataclasses import dataclass, field

import pyeclab.api.kbio_types as KBIO
from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms
from pyeclab.device import BiologicDevice


@dataclass
class GEISTechnique:
    device: BiologicDevice
    vs_initial: bool
    initial_current_step: float
    duration_step: float
    record_every_dT: float
    record_every_dE: float
    initial_frequency: float
    final_frequency: float
    sweep_linear: bool
    amplitude_current: float
    frequency_number: int
    average_n_times: int
    correction: bool
    wait_for_steady: float
    i_range: "KBIO.I_RANGE"
    xctr: int | None = None
    ecc_file: str | None = field(init=False, default=None)
    ecc_params: KBIO.EccParams | None = field(init=False, default=None)

    def make_params(self):
        names = {
            "vs_initial": ECC_parm("vs_initial", bool),
            "initial_current_step": ECC_parm("Initial_Current_step", float),
            "duration_step": ECC_parm("Duration_step", float),
            "record_every_dT": ECC_parm("Record_every_dT", float),
            "record_every_dE": ECC_parm("Record_every_dE", float),
            "final_frequency": ECC_parm("Final_frequency", float),
            "initial_frequency": ECC_parm("Initial_frequency", float),
            "sweep": ECC_parm("sweep", bool),
            "amplitude_current": ECC_parm("Amplitude_Current", float),
            "frequency_number": ECC_parm("Frequency_number", int),
            "average_n_times": ECC_parm("Average_N_times", int),
            "correction": ECC_parm("Correction", bool),
            "wait_for_steady": ECC_parm("Wait_for_steady", float),
            "i_range": ECC_parm("I_Range", int),
            "xctr": ECC_parm("xctr", int),
        }
        params_list = [
            make_ecc_parm(self.device, names["vs_initial"], self.vs_initial),
            make_ecc_parm(self.device, names["initial_current_step"], self.initial_current_step),
            make_ecc_parm(self.device, names["duration_step"], self.duration_step),
            make_ecc_parm(self.device, names["record_every_dT"], self.record_every_dT),
            make_ecc_parm(self.device, names["record_every_dE"], self.record_every_dE),
            make_ecc_parm(self.device, names["final_frequency"], self.final_frequency),
            make_ecc_parm(self.device, names["initial_frequency"], self.initial_frequency),
            make_ecc_parm(self.device, names["sweep"], self.sweep_linear),
            make_ecc_parm(self.device, names["amplitude_current"], self.amplitude_current),
            make_ecc_parm(self.device, names["frequency_number"], self.frequency_number),
            make_ecc_parm(self.device, names["average_n_times"], self.average_n_times),
            make_ecc_parm(self.device, names["correction"], self.correction),
            make_ecc_parm(self.device, names["wait_for_steady"], self.wait_for_steady),
            make_ecc_parm(self.device, names["i_range"], self.i_range.value),
        ]
        if self.xctr:
            params_list.append(make_ecc_parm(self.device, names["xctr"], self.xctr))
        return make_ecc_parms(self.device, *params_list)

    def choose_ecc_file(self):
        return "geis.ecc" if self.device.is_VMP3 else "geis4.ecc"

    def make_technique(self):
        self.ecc_file = self.choose_ecc_file()
        self.ecc_params = self.make_params()
