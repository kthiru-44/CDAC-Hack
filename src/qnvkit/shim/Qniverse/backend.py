"""
qnvkit.shim.Qniverse.backend: Mock Backend builder pattern.
"""

from typing import List


class Backend:
    def __init__(self):
        self._processor = None
        self._hpc = None
        self._simulator = None

    def processor(self, name: str) -> 'Backend':
        self._processor = name
        return self

    def hpc(self, name: str) -> 'Backend':
        if not self._processor:
            raise ValueError("Processor must be set before HPC.")
        self._hpc = name
        return self

    def simulator(self, name: str) -> 'Backend':
        if not self._hpc:
            raise ValueError("HPC must be set before Simulator.")
        self._simulator = name
        return self

    @staticmethod
    def get_processor() -> List[str]:
        return ["CPU", "GPU", "FPGA", "QPU"]

    @staticmethod
    def get_hpc(processor: str) -> List[str]:
        if processor == "CPU":
            return ["QACC_Cluster"]
        elif processor == "GPU":
            return ["Param_Utkarsh"]
        return ["QACC_Cluster"]

    @staticmethod
    def get_simulator(processor: str, hpc: str) -> List[str]:
        if processor == "CPU":
            return ["qasm_simulator", "aer_simulator_statevector", "cirq_simulator", "quest_simulator"]
        return ["nvidia_cudaq_statevector_simulator"]
