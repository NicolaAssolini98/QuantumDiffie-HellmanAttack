import numpy as np
from qiskit import QuantumCircuit, Aer, transpile, assemble
from numpy.random import randint
from fractions import Fraction
from math import gcd


# blocco U
def c_amod15(a, power):
    # if a not in [2, 7, 8, 11, 13]: # tengo solo quelli con un uno o uno zero
    #     raise ValueError("'a' must be 2,7,8,11 or 13")

    U = QuantumCircuit(4)
    for iteration in range(power):
        # crea i numeri in binario 0001 -> 0010
        if a in [2, 13]:
            U.swap(0, 1)
            U.swap(1, 2)
            U.swap(2, 3)
        if a in [7, 8]:
            U.swap(2, 3)
            U.swap(1, 2)
            U.swap(0, 1)
        if a == 11:
            U.swap(1, 3)
            U.swap(0, 2)
        if a in [7, 11, 13]:
            for q in range(4):
                U.x(q)

    U = U.to_gate()
    U.name = "%i^%i mod 15" % (a, power)
    c_U = U.control()

    return c_U


# QFT inversa
def qft_dagger(n):
    qc = QuantumCircuit(n)

    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)

    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / float(2 ** (j - m)), m, j)
        qc.h(j)

    qc.name = "QFT†"

    return qc


def qpe_amod15(a):
    n_count = 4
    qc = QuantumCircuit(4 + n_count, n_count)

    # inizializzo qu bit a |+>
    for q in range(n_count):
        qc.h(q)
    # inizializzo 4 qu bit a |1>
    qc.x(3 + n_count)

    # aggiungo le U
    for q in range(n_count):
        # concateno agli ultimi 4
        qc.append(c_amod15(a, 2 ** q), [q] + [i + n_count for i in range(4)])

    # aggiunge QFT inversa
    qc.append(qft_dagger(n_count), range(n_count))
    qc.measure(range(n_count), range(n_count))
    # print(qc.draw())
    qasm_sim = Aer.get_backend('qasm_simulator')

    # transpile -> construct a circuit equivalent which can be run on the given configuration.
    t_qc = transpile(qc, qasm_sim)
    qobj = assemble(t_qc, shots=1)
    result = qasm_sim.run(qobj, memory=True).result()
    readings = result.get_memory()
    print("    Registro: " + readings[0])

    phase = int(readings[0], 2) / (2 ** n_count)
    print("    Fase: %f" % phase)

    return phase


N = 15
np.random.seed(1)

a = randint(2, N)

while gcd(a, N) != 1:
    a = randint(2, N)
    # print(a)


factor_found = False
attempt = 0

while not factor_found:
    attempt += 1
    print("\n %i:" % attempt)

    phase = qpe_amod15(a)  # Fase = s/r
    frac = Fraction(phase).limit_denominator(N)   # Frazioni continue
    r = frac.denominator
    print("    Periodo: %i" % r)

    # Se la fase è diversa da zero, controllo che i due fattori non siano 1 e 15
    if phase != 0:
        guesses = [gcd(a ** (r // 2) - 1, N), gcd(a ** (r // 2) + 1, N)]
        print("    Factori trovati: %i - %i" % (guesses[0], guesses[1]))

        for guess in guesses:
            if guess not in [1, N] and (N % guess) == 0:
                factor_found = True
