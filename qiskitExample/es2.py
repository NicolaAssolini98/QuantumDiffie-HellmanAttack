"""
How does the circuit size for arbitrary initialization grow when the number of qubit increases?
"""
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import random_statevector

qubits = [1, 2, 3, 4, 5, 6, 7, 8]
sizes = []
for qubit in qubits:
    qc = QuantumCircuit(qubit)
    statevector = random_statevector(2 ** qubit)
    qc.initialize(statevector.data)
    qc2 = transpile(qc, basis_gates=['u3', 'cx'])
    sizes.append(qc2.size())
print(sizes)


