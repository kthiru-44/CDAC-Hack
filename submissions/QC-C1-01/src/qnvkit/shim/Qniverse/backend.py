"""Local stand-in for ``Qniverse.backend`` (used only when the real QSDK is not installed)."""

_SIMS = {
    ("CPU", "QACC_Cluster"): [
        "aer_simulator_density_matrix", "aer_simulator_statevector", "cirq_simulator",
        "qasm_simulator", "qsimcirq_simulator", "quest_simulator", "qulacs_multicpu_simulator",
    ],
    ("GPU", "QACC_Cluster"): [
        "aer_simulator_statevector_gpu", "nvidia_cudaq_statevector_simulator",
        "qsimcirq_cuquantum_gpu_simulator",
    ],
    ("CPU", "Param_Utkarsh"): [
        "aer_simulator_density_matrix", "aer_simulator_statevector", "cirq_simulator", "qasm_simulator",
    ],
    ("GPU", "Param_Utkarsh"): ["aer_simulator_statevector_gpu"],
}


class Backend:
    def __init__(self):
        self._processor = None
        self._hpc = None
        self._simulator = None

    def processor(self, name):
        if name not in ("CPU", "GPU"):
            raise ValueError("Unknown processor '%s'." % name)
        self._processor = name

    def hpc(self, name):
        if not self._processor:
            raise ValueError("Processor must be set before HPC.")
        if (self._processor, name) not in _SIMS:
            raise ValueError("HPC '%s' is not valid for processor '%s'." % (name, self._processor))
        self._hpc = name

    def simulator(self, name):
        if not self._processor or not self._hpc:
            raise ValueError("Processor and HPC must be set before setting Simulator.")
        if name not in _SIMS[(self._processor, self._hpc)]:
            raise ValueError("Simulator '%s' is not available on %s/%s." % (name, self._processor, self._hpc))
        self._simulator = name

    @staticmethod
    def get_processor():
        return ["CPU", "GPU"]

    @staticmethod
    def get_hpc(processor):
        return [h for (p, h) in _SIMS if p == processor]

    @staticmethod
    def get_simulator(processor, hpc):
        return list(_SIMS.get((processor, hpc), []))
