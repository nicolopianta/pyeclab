"""
Channel for sequences that contain PEIS / GEIS steps.
"""
import time

import numpy as np

from pyeclab.channel import Channel

# PEIS/GEIS technique IDs (EC-Lab Development Package manual, sections 7.11 / 7.13)
PEIS_GEIS_TECH_IDS = (104, 107)


class PEISAwareChannel(Channel):
    """
    pyeclab's Channel._get_converted_buffer() always calls buffer_converters.base(), which
    hardcodes the process-0 column layout (t_high, t_low, Ewe, I) -- right for CA/CP/OCV, which
    only ever emit process-0 data. PEIS/GEIS also emit process-1 buffers (the frequency-sweep
    result rows: freq, |Ewe|, |I|, phase, ...), and base() would misread THOSE columns as if
    they were (t, Ewe, I) too, writing garbage rows into measurement_data.txt and the live plots.

    Process-1 rows are decoded here instead (phase comes back in RADIANS) and appended to
    self.peis_freqs / self.peis_z, with the sequence step they belong to in
    self.peis_step_index, for a GUI to plot live and save; they contribute zero rows to the
    (t, Ewe, I) stream. Process-0 of a PEIS/GEIS step (the initial hold, sampled by EC-Lab at its
    ~24 us timebase -- ~680k rows per 100 s when Record_every_dT is 0, tens of MB of text) is
    dropped rather than written. Every other technique goes through the normal inherited path.

    Polling: process-1 buffers are transient -- in direct testing 0.3 s polling missed every
    result row while 0.02 s caught them all -- so the channel polls every 0.02 s while a PEIS/GEIS
    technique is active and at the normal interval otherwise (see Channel._poll_interval).
    """

    PEIS_GEIS_TECH_IDS = PEIS_GEIS_TECH_IDS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.peis_freqs = []
        self.peis_z = []
        self.peis_step_index = []

    def _get_measurement_values(self):
        self._get_data()
        if self.data_info.TechniqueID in self.PEIS_GEIS_TECH_IDS:
            if self.data_info.ProcessIndex == 1 and self.data_info.NbRows > 0:
                cols = self.data_info.NbCols
                buf = self.data_buffer
                for r in range(self.data_info.NbRows):
                    row = [buf[r * cols + c] for c in range(cols)]
                    freq = self.bio_device.ConvertNumericIntoSingle(row[0])
                    abs_ewe = self.bio_device.ConvertNumericIntoSingle(row[1])
                    abs_i = self.bio_device.ConvertNumericIntoSingle(row[2])
                    phase_rad = self.bio_device.ConvertNumericIntoSingle(row[3])
                    z = (abs_ewe / abs_i) * np.exp(1j * phase_rad) if abs_i else complex("nan")
                    # step index last: readers on another thread treat len(peis_freqs) as the
                    # number of complete rows, so freq is appended after the other two.
                    self.peis_z.append(z)
                    self.peis_step_index.append(self.data_info.TechniqueIndex)
                    self.peis_freqs.append(freq)
            return (np.array([]), np.array([]), np.array([]))
        return self._get_converted_buffer()

    def _poll_interval(self, default):
        if self.data_info.TechniqueID in self.PEIS_GEIS_TECH_IDS:
            return 0.02
        return default

    def peis_geis_points(self):
        """(freqs, z, step_index) of the PEIS/GEIS points received so far, or None. Safe to call
        from another thread while the channel's thread keeps appending: a row count is
        snapshotted once and all three lists are sliced to it."""
        if not self.peis_freqs:
            return None
        n = len(self.peis_freqs)  # freq is appended last, so z/step already have >= n entries
        return (
            np.array(self.peis_freqs[:n], dtype=float),
            np.array(self.peis_z[:n], dtype=complex),
            np.array(self.peis_step_index[:n], dtype=int),
        )


def write_peis_geis_csv(path, freqs, z, step_index):
    """Write PEIS/GEIS results as CSV: technique_index, freq_Hz, Zre_ohm, Zim_ohm, absZ_ohm, phase_deg."""
    np.savetxt(
        path,
        np.column_stack([step_index, freqs, z.real, z.imag, np.abs(z), np.degrees(np.angle(z))]),
        delimiter=",", header="technique_index,freq_Hz,Zre_ohm,Zim_ohm,absZ_ohm,phase_deg", comments="",
    )
