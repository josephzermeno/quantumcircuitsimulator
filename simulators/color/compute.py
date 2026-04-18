import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qiskit.quantum_info import DensityMatrix, partial_trace
from qiskit.circuit.library import (
    HGate, XGate, YGate, ZGate, SGate, TGate,
    CXGate, RXGate, RYGate, RZGate,
)
from CircuitSimulator import QCircuit

STATIC_GATES = {
    'h': HGate(), 'x': XGate(), 'y': YGate(), 'z': ZGate(),
    's': SGate(), 't': TGate(), 'cx': CXGate(),
}
ROTATION_CLASSES = {'rx': RXGate, 'ry': RYGate, 'rz': RZGate}


def apply_unitary(rho, g):
    name = g['gate']
    qubits = g['qubits']
    if name in ROTATION_CLASSES:
        return rho.evolve(ROTATION_CLASSES[name](g['angle']), qargs=qubits)
    return rho.evolve(STATIC_GATES[name], qargs=qubits)


def apply_measurement_collapse(rho, q, num_qubits):
    """Non-selective projective measurement on qubit q in the computational basis.
    ρ → Σ_k Π_k ρ Π_k, zeroing coherences between |0⟩ and |1⟩ of qubit q while
    preserving the Born-rule diagonal."""
    data = rho.data.copy()
    dim = 2 ** num_qubits
    for i in range(dim):
        for j in range(dim):
            if ((i >> q) & 1) != ((j >> q) & 1):
                data[i, j] = 0
    return DensityMatrix(data)


def reduced_qubit_density(rho, q, num_qubits):
    trace_out = [qq for qq in range(num_qubits) if qq != q]
    reduced = partial_trace(rho, trace_out)
    return DensityMatrix(np.round(reduced.data, 4))


def compute(circuit_data):
    num_qubits = circuit_data['num_qubits']
    helper = QCircuit(num_qubits)  # borrow colormap + lab_to_rgb only

    ops_at_position = {}
    measurements_at_position = {}
    gates_at_positions = []
    max_pos = 0

    for g in circuit_data['gates']:
        col = g.get('col', 0)
        pos = col + 1  # position 0 is reserved for initial state
        qubits = g['qubits']
        entry = {'gate': g['gate'], 'position': pos, 'qubits': qubits}

        if g['gate'] == 'measure':
            measurements_at_position.setdefault(pos, []).append(qubits[0])
        else:
            ops_at_position.setdefault(pos, []).append(g)
            if 'angle' in g:
                entry['angle'] = round(float(g['angle']), 4)

        gates_at_positions.append(entry)
        max_pos = max(max_pos, pos)

    numpositions = max_pos + 1

    rho = DensityMatrix.from_label('0' * num_qubits)
    wire_colors = []
    measurement_results = []

    for i in range(numpositions):
        for g in ops_at_position.get(i, []):
            rho = apply_unitary(rho, g)

        if i in measurements_at_position:
            for q in measurements_at_position[i]:
                rho_reduced = reduced_qubit_density(rho, q, num_qubits)
                measurement_results.append({
                    'position': i,
                    'qubit': q,
                    'prob_0': float(rho_reduced.data[0][0].real),
                    'prob_1': float(rho_reduced.data[1][1].real),
                })
                rho = apply_measurement_collapse(rho, q, num_qubits)

        for q in range(num_qubits):
            rho_reduced = reduced_qubit_density(rho, q, num_qubits)
            L, A, B = helper.colormap(rho_reduced)
            rgb = helper.lab_to_rgb(float(L), float(A), float(B))
            wire_colors.append({
                'position': i,
                'qubit': q,
                'color': [float(c) for c in rgb],
            })

    return {
        'num_qubits': num_qubits,
        'num_positions': numpositions,
        'gates_at_positions': gates_at_positions,
        'wire_colors': wire_colors,
        'measurements': measurement_results,
    }


if __name__ == '__main__':
    print(json.dumps(compute(json.loads(sys.stdin.read()))))
