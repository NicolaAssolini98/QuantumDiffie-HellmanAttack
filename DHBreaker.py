import numpy as np
from qiskit import QuantumCircuit, Aer, transpile, assemble, ClassicalRegister, QuantumRegister

'''
p = 7, b = 3, a = 3^2 = 2
'''
n_count = 6
n_bit = 3
p = 7
b = 3
a = 2


def u_b3(power):
    """
     U|y> = |y3^power mod 7>
    """
    u = QuantumCircuit(3)
    for iteration in range(power):
        u.swap(1, 2)
        u.swap(0, 1)
        u.x(0)
        u.x(1)
        u.x(2)

    u = u.to_gate()
    u.name = "3^%i mod 7" % power

    return u.control()


def u_a2(power):
    """
    U|y> = |y2^power mod 7>
    """
    u = QuantumCircuit(3)
    for iteration in range(power):
        u.swap(0, 1)
        u.swap(1, 2)
    u = u.to_gate()
    u.name = "2^%i mod 7" % power

    return u.control()


# def u_a5(power):
#     """
#     a = 5
#     """
#     u = QuantumCircuit(3)
#     for iteration in range(power):
#         u.swap(0, 1)
#         u.swap(1, 2)
#         u.x(0)
#         u.x(1)
#         u.x(2)
#     u.name = "5^%i mod 7" % power
#
#     return u.control()


def inverse_qft(n):
    """
    QFT inversa
    """
    qc = QuantumCircuit(n)

    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)

    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / float(2 ** (j - m)), m, j)
        qc.h(j)

    qc.name = "QFT†"

    return qc.to_gate()


def quantum_c():
    """ creazione del circuito  """
    qr = QuantumRegister(n_bit + 2 * n_count)
    c_a = ClassicalRegister(n_count, name="c_a")
    c_b = ClassicalRegister(n_count, name="c_b")
    qc = QuantumCircuit(qr, c_a, c_b)

    """ aggiungo Hadamard """
    for q in range(2 * n_count):
        qc.h(q)

    """ inizializzo 3 qu bit a |1> """
    qc.x(2 + 2 * n_count)

    """ aggiungo le U """
    for q in range(n_count):
        qc.append(u_b3(2 ** q), [q + n_count] + [i + 2 * n_count for i in range(n_bit)])

    for q in range(n_count):
        qc.append(u_a2(2 ** q), [q] + [i + 2 * n_count for i in range(n_bit)])
    qc.barrier()

    """ aggiungo QFT inversa """
    qc.append(inverse_qft(n_count), range(n_count))
    qc.append(inverse_qft(n_count), range(n_count, 2 * n_count))

    """ aggiungo le misurazioni """
    qc.measure(range(n_count), range(n_count))
    qc.measure(range(n_count, 2 * n_count), range(n_count, 2 * n_count))
    print(qc.draw())

    """ simulo il circuito """
    qasm_sim = Aer.get_backend('qasm_simulator')
    t_qc = transpile(qc, qasm_sim)
    qobj = assemble(t_qc, shots=1)  # default 1024 shots

    result = qasm_sim.run(qobj, memory=True).result()
    readings = result.get_memory()
    regs = readings[0].split(" ")
    print("    Registri:", end=" ")
    print(regs)

    """ calcolo delle fasi """
    phase_a = int(regs[0], 2) / (2 ** n_count)
    phase_b = int(regs[1], 2) / (2 ** n_count)

    return phase_a, phase_b


attempt = 0
r = p - 1
""" eseguo il circuito fino a quando non ottengo t """
while True:
    attempt += 1
    print("\n %i:" % attempt)

    x, y = quantum_c()  # x ≈ k/r, y ≈ [kt]r/r

    x_t = int(round(x * r))
    y_t = int(round(y * r))

    print("x: %i   y: %i" % (x_t, y_t))

    if x_t != 0:
        t = int(y_t / x_t) % r
        print("dla(%i) mod %i = %i" % (a, p, t))
        """ se è corretto termino """
        if pow(b, t, p) == a:
            break
