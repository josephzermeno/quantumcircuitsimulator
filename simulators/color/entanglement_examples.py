from CircuitSimulator import QCircuit
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np
import matplotlib.pyplot as plt



qc = QCircuit(5)

qc.h(1)

qc.rx(-3.1415926/2, 2)

qc.h(3)
qc.cx(3, 4)

qc.x(0)
qc.ry(3.141592, 1)
qc.rx(3.1415926, 2)



qc.draw(output="mpl") # Qiskit plot
qc.draw_color()

plt.savefig("example1")
plt.show()


qc = QCircuit(2)

# Apply Y-rotation to qubit 1
alpha = 2 * np.arccos(np.sqrt(1/3))
qc.ry(alpha, 1)

# Apply CNOT from qubit 1 to qubit 0
qc.cx(1, 0)


qc.draw()
fig, ax = qc.draw_color(return_fig=True)

ax.set_title(r'$\sqrt{\frac{1}{3}}|00\rangle + \sqrt{\frac{2}{3}}|11\rangle$')

plt.show()


qc = QCircuit(2)

# Apply Y-rotation to qubit 1
alpha = 2 * np.arccos(np.sqrt(1/3))
qc.ry(alpha, 1)

# Apply CNOT from qubit 1 to qubit 0
qc.cx(1, 0)

qc.x(1)


qc.draw()
fig, ax = qc.draw_color(return_fig=True)

ax.set_title(r'$\sqrt{\frac{1}{3}}|01\rangle + \sqrt{\frac{2}{3}}|10\rangle$')
plt.savefig("example2")

plt.show()

qc = QCircuit(2)

# Apply Y-rotation to qubit 1
alpha = 2 * np.arccos(np.sqrt(4/10))
qc.ry(alpha, 1)

# Apply CNOT from qubit 1 to qubit 0
qc.cx(1, 0)

qc.x(1)

qc.h([0, 1])


qc.draw()
fig, ax = qc.draw_color(return_fig=True)

ax.set_title(r'$\sqrt{\frac{4}{10}}|+-\rangle + \sqrt{\frac{6}{10}}|-+\rangle$')
plt.savefig("example3")

plt.show()
