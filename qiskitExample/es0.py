"""
Quantum teleport
"""
from qiskit.quantum_info.states.random import random_statevector
from qiskit import *


def create_bell_circuit():
    bell_circuit = QuantumCircuit(2, name='bell')
    bell_circuit.h(0)
    bell_circuit.cx(0, 1)
    return bell_circuit


qr = QuantumRegister(3, 'q')
crx = ClassicalRegister(1, 'crx')
crz = ClassicalRegister(1, 'crz')
qc = QuantumCircuit(qr, crx, crz)
# Use to initialize qubit psi di Alice
psi = random_statevector(2).data
qc.initialize(psi, qr[0])
qc.draw()
qc.append(create_bell_circuit(), [qr[1], qr[2]])
qc.draw()
# show composed circuits
qc.decompose().draw()

qc.cx(qr[0], qr[1])
qc.h(qr[0])
qc.draw()

qc.measure(qr[0], crz)
qc.measure(qr[1], crx)
qc.draw()

qc.x(qr[2]).c_if(crx, 1)
qc.z(qr[2]).c_if(crz, 1)
qc.draw()

sv_sim = Aer.get_backend('statevector_simulator')
sv = execute(qc, sv_sim).result().get_statevector()

# sv == |psi> x |b1> x |b2>
print(sv)

"""
verifichiamo che spostando la misurazione in fondo, e controllando x e z con bit quantistico, il risultato sia uguale
"""
qr_dm = QuantumRegister(3, 'q')
crx_dm = ClassicalRegister(1, 'crx')
crz_dm = ClassicalRegister(1, 'crz')
qc_dm = QuantumCircuit(qr_dm, crx_dm, crz_dm)
qc_dm.initialize(psi, qr[0])
qc_dm.append(create_bell_circuit(), [qr[1], qr[2]])
qc_dm.cx(qr[0], qr[1])
qc_dm.h(qr[0])

# sposto misurazioni e x,z diventano cx e cz
qc_dm.cx(qr[0], qr[2])
qc_dm.cz(qr[1], qr[2])
qc_dm.measure(qr[0], crz_dm)
qc_dm.measure(qr[1], crx_dm)
qc_dm.draw()

sv_dm = execute(qc_dm, Aer.get_backend('statevector_simulator')).result().get_statevector()

print("sv qc: ", sv)
print("sv qc_dm: ", sv_dm)

"""
Inverse of initialize gate
"""

from qiskit.extensions import Initialize

psi = random_statevector(2).data
init_gate = Initialize(psi)
init_gate.label = 'init'
inverse_init_gate = init_gate.gates_to_uncompute()
qc = QuantumCircuit(1)
qc.append(init_gate, [0])
qc.append(inverse_init_gate, [0])
sv = execute(qc, sv_sim).result().get_statevector

inverse_init_gate = init_gate.gates_to_uncompute() # no reset
# se io faccio inverso dell'inverso ottengo init senza reset
init_wo_reset = inverse_init_gate.inverse()
#ora lo posso fare
init_wo_reset.inverse()

