"""
PEIS (Potentio Electrochemical Impedance Spectroscopy, technique ID 104): EC-Lab's own single-sine impedance
technique, measured through the potentiostat's internal sine generator and ADC.

Parameter names and the set of parameters the technique takes are from the "EC-Lab Development Package" manual,
section 7.11 -- notably PEIS takes no I_Range / E_Range / Bandwidth (unlike CA). Duration_step is the length of
the INITIAL HOLD at the step potential (process 0) before the frequency sweep starts, not a timeout: no impedance
point can appear before it has elapsed. The sweep results (process 1) are decoded by
pyeclab.channel.peis_channel.PEISAwareChannel.
"""
from dataclasses import dataclass, field

import pyeclab.api.kbio_types as KBIO
from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms
from pyeclab.device import BiologicDevice


@dataclass
class PEISTechnique:
    device: BiologicDevice
    vs_initial: bool
    initial_voltage_step: float
    duration_step: float
    record_every_dT: float
    record_every_dI: float
    initial_frequency: float
    final_frequency: float
    sweep_linear: bool
    amplitude_voltage: float
    frequency_number: int
    average_n_times: int
    correction: bool
    wait_for_steady: float
    xctr: int | None = None
    ecc_file: str | None = field(init=False, default=None)
    ecc_params: KBIO.EccParams | None = field(init=False, default=None)

    def make_params(self):
        names = {
            "vs_initial": ECC_parm("vs_initial", bool),
            "initial_voltage_step": ECC_parm("Initial_Voltage_step", float),
            "duration_step": ECC_parm("Duration_step", float),
            "record_every_dT": ECC_parm("Record_every_dT", float),
            "record_every_dI": ECC_parm("Record_every_dI", float),
            "final_frequency": ECC_parm("Final_frequency", float),
            "initial_frequency": ECC_parm("Initial_frequency", float),
            "sweep": ECC_parm("sweep", bool),
            "amplitude_voltage": ECC_parm("Amplitude_Voltage", float),
            "frequency_number": ECC_parm("Frequency_number", int),
            "average_n_times": ECC_parm("Average_N_times", int),
            "correction": ECC_parm("Correction", bool),
            "wait_for_steady": ECC_parm("Wait_for_steady", float),
            "xctr": ECC_parm("xctr", int),
        }
        params_list = [
            make_ecc_parm(self.device, names["vs_initial"], self.vs_initial),
            make_ecc_parm(self.device, names["initial_voltage_step"], self.initial_voltage_step),
            make_ecc_parm(self.device, names["duration_step"], self.duration_step),
            make_ecc_parm(self.device, names["record_every_dT"], self.record_every_dT),
            make_ecc_parm(self.device, names["record_every_dI"], self.record_every_dI),
            make_ecc_parm(self.device, names["final_frequency"], self.final_frequency),
            make_ecc_parm(self.device, names["initial_frequency"], self.initial_frequency),
            make_ecc_parm(self.device, names["sweep"], self.sweep_linear),
            make_ecc_parm(self.device, names["amplitude_voltage"], self.amplitude_voltage),
            make_ecc_parm(self.device, names["frequency_number"], self.frequency_number),
            make_ecc_parm(self.device, names["average_n_times"], self.average_n_times),
            make_ecc_parm(self.device, names["correction"], self.correction),
            make_ecc_parm(self.device, names["wait_for_steady"], self.wait_for_steady),
        ]
        if self.xctr:
            params_list.append(make_ecc_parm(self.device, names["xctr"], self.xctr))
        return make_ecc_parms(self.device, *params_list)

    def choose_ecc_file(self):
        return "peis.ecc" if self.device.is_VMP3 else "peis4.ecc"

    def make_technique(self):
        self.ecc_file = self.choose_ecc_file()
        self.ecc_params = self.make_params()
