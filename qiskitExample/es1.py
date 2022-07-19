"""
BEll state
"""
from qiskit import QuantumCircuit, execute, Aer, IBMQ

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
print(qc.draw())

statevector_sim = Aer.get_backend('statevector_simulator')
print(execute(qc, backend=statevector_sim, shots=1).result().get_statevector())

unitary_sim = Aer.get_backend('unitary_simulator')
print(execute(qc, backend=unitary_sim, shots=1).result().get_unitary())

qasm_sim = Aer.get_backend('qasm_simulator')
qc.measure(0, 0)
qc.measure(1, 1)
print(execute(qc, backend=qasm_sim, shots=1000).result().get_counts())

IBMQ.load_account()
santiago = IBMQ.get_provider().get_backend('ibmq_santiago')
print(execute(qc, backend=santiago, shots=1000).result().get_counts())
