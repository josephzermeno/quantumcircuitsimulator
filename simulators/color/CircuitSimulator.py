import numpy as np
if not hasattr(np, 'asscalar'):
    np.asscalar = lambda a: a.item()
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
import colorspacious as cs
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.circuit.library import *
from qiskit.quantum_info import Operator, DensityMatrix, partial_trace
from qiskit.visualization import plot_state_city, plot_bloch_multivector



class QCircuit(QuantumCircuit):

    def __init__(self, n):
        super().__init__(n)  # initialize the base QuantumCircuit class
        self.numqubits = n
        self.wirelengths = 0.75 # length of wires in between gates
        self.wirewidth = 7 # thickness of wire

        # gate dimensions
        self.gatewidth = 0.5
        self.gateheight = 0.5

        self.textcolor = 'black'

        # possible rotations
        self.rotations = ['rx', 'ry', 'rz', 'crx', 'cry', 'crz', '$R_X$', '$R_Y$', '$R_Z$']

        self.gatecolor = 'white'


        # map gate names to functions for drawing
        self.gatedrawings = {
            "h": lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, 'H'), # Hadamard gate
            "x": lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, 'X'), # Pauli-X gate
            "y": lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, 'Y'), # Pauli-Y gate
            "z": lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, 'Z'), # Pauli-Z gate
            "s": lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, 'S'), # S gate (phase gate)
            "sdg": lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, '$S^†$'), # S dagger gate
            "t": lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, 'T'), # T gate
            "tdg": lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, '$T^†$'), # T dagger gate
            "u1": lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, 'U1'), # U1 gate
            "u2":lambda self, ax, position, color, qubits: self.draw_simple_gate(ax, position, color, qubits, 'U2'), # U2 gate
            "u3": lambda self, ax, position, color, qubits, angles: self.draw_rotation_gate(ax, position, color, qubits, angles, 'U3'), # U3 gate
            "rx": lambda self, ax, position, color, qubits, angle: self.draw_rotation_gate(ax, position, color, qubits, angle, '$R_X$'), # Rotation around X-axis
            "ry": lambda self, ax, position, color, qubits, angle: self.draw_rotation_gate(ax, position, color, qubits, angle, '$R_Y$'), # Rotation around Y-axis
            "rz": lambda self, ax, position, color, qubits, angle: self.draw_rotation_gate(ax, position, color, qubits, angle, '$R_Z$'),  # Rotation around Z-axis
            "cx" : lambda self, ax, position, color, qubits: self.draw_cnot_gate(ax, position, color, qubits),
            "cy" : lambda self, ax, position, color, qubits: self.draw_control_gate(ax, position, color, qubits, "Y"),
            "cz" : lambda self, ax, position, color, qubits: self.draw_control_gate(ax, position, color, qubits, "Z"),
            "crx" : lambda self, ax, position, color, qubits, angle: self.draw_control_gate(ax, position, color, qubits, "$R_X$", angle),
            "cry" : lambda self, ax, position, color, qubits, angle: self.draw_control_gate(ax, position, color, qubits, "$R_Y$", angle),
            "crz" : lambda self, ax, position, color, qubits, angle: self.draw_control_gate(ax, position, color, qubits, "$R_Z$", angle),
        }

        # map gate names to gate objects
        self.gateobject = {
        'h': HGate(),
        'x': XGate(),
        'y': YGate(),
        'z': ZGate(),
        's' : SGate(),
        'sdg' : SdgGate(),
        't' : TGate(),
        'cx': CXGate(),
        'cy' : CYGate(),
        'cz' : CZGate(),
        'rx' : RXGate,
        'ry' : RYGate,
        'rz' : RYGate,
        'crx' : CRXGate,
        'cry' : CRYGate,
        'crz' : CRZGate,
        'u3' : U3Gate
    }


    def setwirelength(self, length):
        self.wirelengths = length
    def setwirewidth(self, width):
        self.wirewidth = width
    def setgatecolor(self, gatecolor, textcolor):
        self.gatecolor = gatecolor
        self.textcolor = textcolor

    def getdensitymatrix(self, circ):
        simulator = Aer.get_backend('statevector_simulator')
        compiled_circuit = transpile(circ, simulator)
        job = simulator.run(compiled_circuit)
        result = job.result()
        statevector = result.get_statevector()
        density_matrix = np.outer(statevector, np.conj(statevector))
        return density_matrix

    
    def colormap(self, density):
        # Calculates the LAB color map for a density state
        rho = density.data

        z = np.array([[1, 0], [0, -1]])
        avgZ = np.trace(np.matmul(rho, z)).real
        l = 100 * (1 - avgZ) * 0.5

        x = np.array([[0, 1], [1, 0]])
        avgx = np.trace(np.matmul(rho, x)).real
        a = 127 * avgx

        y = np.array([[0, -1j], [1j, 0]])
        avgy = np.trace(np.matmul(rho, y)).real
        b = 127 * avgy

        return l, a, b
        
    
    def lab_to_rgb(self, l, a, b):
        '''
        # Using cv2
        # Rescale L and shift a, b
        l_scaled = l * 255 / 100
        a_shifted = a + 128
        b_shifted = b + 128
        '''

        # using pycolormath
        lab = LabColor(lab_l=l, lab_a=a, lab_b=b)
        rgb = convert_color(lab, sRGBColor)
        rgb_values = (rgb.rgb_r, rgb.rgb_g, rgb.rgb_b)



        # Find the maximum value among the RGB components
        max_value = max(rgb_values)

        # If the maximum value is greater than 1.0, renormalize all values
        if max_value > 1.0:
            rgb_values = tuple(value / max_value for value in rgb_values)


        '''
        # using cv2
        # Create an array and convert
        lab = np.array([[[l_scaled, a_shifted, b_shifted]]], dtype=np.uint8)
        bgr = cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)
        rgb = bgr[0][0][[2, 1, 0]]
        rgb_scaled = tuple(map(lambda x: x / 255.0, rgb))
        '''
        
        return rgb_values



    def gate_map(self):
        # map to keep track of gate positions
        gatepos = {} # gate : (position, qubits)

        # map to keep track of qubit position
        # qubits all in state 0 at pos = 0
        qubitpos = {}
        for q in range(self.numqubits):
            qubitpos[q] = 1

        # populate gatepos map    
        for gate, qubits, _ in self.data:
            qubits = [self.find_bit(q).index for q in qubits] # redefine qubits to be the indicies
            pos = max(qubitpos[q] for q in qubits) # get the current position

            # initialize gate if not in map
            if gate.name not in gatepos:
                gatepos[gate.name] = []
            
            if gate.name in self.rotations:
                angle = gate.params[0]
                gatepos[gate.name].append((pos, qubits, angle))
            else:
                gatepos[gate.name].append((pos, qubits))

            # update qubit positions
            for q in qubits:
                qubitpos[q] = pos + 1

        return gatepos, max(qubitpos.values())

            

        
    def draw_color(self, return_fig=False):
        # map of gate and the positions it was applied
        gatehistory, numpositions = self.gate_map()

        fig, ax = plt.subplots()

        # Set the facecolor of the figure and axes to transparent
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)

        # Maps the qubit to a list of wire positions
        wires = {}

        # Draw the qubits on the leftmost side and initialize wire positions
        for qubit in range(self.numqubits):
            # Draw qubit label
            ax.text(-0.1, qubit, r'$q_{' + str(qubit) + '}$', ha='right', va='center', fontsize='14')
            
            # List of wire positions
            wirepos = []
            for i in range(numpositions):
                x = i * self.wirelengths
                wirepos.append(((x, qubit), (x + self.wirelengths, qubit)))
            wires[qubit] = wirepos

        # Draw the gates
        # First, draw box for gate, then draw the gate name
        for gatename, data in gatehistory.items():
            for d in data:
                pos = d[0]
                qubits = d[1]
                drawfunc = self.gatedrawings[gatename]

                xpos = pos * self.wirelengths # x position of gate

                # draw the gate
                if gatename in self.rotations:
                    angle = d[2]
                    drawfunc(self, ax, xpos, self.gatecolor, qubits, angle)
                else:
                    drawfunc(self, ax, xpos, self.gatecolor, qubits)
        
        # Draw wires
        tempcirc = QuantumCircuit(self.numqubits) # initialize the starting state
        density = DensityMatrix(tempcirc) # initialize the density matrix
        for i in range(numpositions):
            # gate operation at given position (gate, qubits)
            ops = []

            # indicies of qubits that were affected
            qubit_indices = []
            for gate in gatehistory.keys():
                ophistory = gatehistory[gate]
                for t in ophistory:
                    if t[0] == i:
                        qubits = t[1]
                        if gate in self.rotations:
                            ops.append((gate, qubits, t[2]))
                        else:
                            ops.append((gate, qubits))

                        # add qubits to index list
                        # note that the same qubit won't be added twice because of how
                        # the position is defined. When a new gate was applied to a qubit,
                        # the position for all qubits was incrmented
                        for q in qubits:
                            qubit_indices.append(qubit)
            for o in ops:
                g = o[0] # gate to be applied
                if g not in self.rotations:
                    qb = o[1] # qubits to apply the gate to 
                    tempcirc.append(self.gateobject[g], qb)
                else:
                    qb = o[1] # qubits to apply the gate to 
                    theta = o[2] # rotation angle
                    tempcirc.append(self.gateobject[g](theta), qb)

            # update density matrix
            density = DensityMatrix(tempcirc)

            # wires to color
            wiredata = [(qubit, position[i]) for qubit, position in wires.items()]

            # color each qubit wire
            for q in range(self.numqubits):
                # qubits to trace out
                trace_out = [qubit for qubit in range(self.numqubits) if q != qubit]

                # calculate the reduced density matrix
                # reduced_density = self.partial_trace(density, q, self.numqubits)
                reduced_density = partial_trace(density, trace_out)

                # round data to 4 decimal places
                rounded_data = np.round(reduced_density.data, 4)
                reduced_density = DensityMatrix(rounded_data)

                # find color map
                L, A, B = self.colormap(reduced_density)
                print("Color for q", q, " is ", L, A, B)

                # convert LAB to RGB
                rgb_color = self.lab_to_rgb(L, A, B)

                # wire to color
                wire = None
                for w in wiredata:
                    if w[0] == q:
                        wire = w
                if wire == None:
                    raise ValueError("Unable to locate wire for plotting")

                start, end = wire[1] # pair of coordinates
                x1, x2 = start[0], end[0]
                y1, y2 = start[1], end[1]
                ax.plot([x1, x2], [y1, y2], color=rgb_color, zorder=1, linewidth=self.wirewidth)

    


        # Invert the y-axis so that qubit 0 is at the top
        ax.invert_yaxis()

        # Remove axes
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)



        # Set axis to make the plot to scale
        ax.axis('scaled')
        
        if return_fig:
            return fig, ax

    
    def draw_simple_gate(self, ax, xposition, color, qubits, gatename):
        width = self.gatewidth
        height = self.gateheight
        for q in qubits:
            # Adjusted coordinates to center the rectangle at (x, y)
            x = xposition - width / 2
            y = q - height / 2
            # Rectangle((x, y), width, height)
            rect = patches.Rectangle((x, y), width, height, linewidth=1, edgecolor=self.textcolor, facecolor=color, zorder=2)

            # Add the rectangle patch to the plot
            ax.add_patch(rect)

            # Calculate the text coordinates
            text_x = x + width / 2 
            text_y = y + 1 * height / 3

            # Add the text
            ax.text(text_x, text_y, gatename, ha='center', va='center', zorder=2)

    def draw_rotation_gate(self, ax, xposition, color, qubits, angle, gatename):
        width = self.gatewidth
        height = self.gateheight
        for q in qubits:
            # Adjusted coordinates to center the rectangle at (x, y)
            x = xposition - width / 2
            y = q - height / 2
            # Rectangle((x, y), width, height)
            rect = patches.Rectangle((x, y), width, height, linewidth=1, edgecolor=self.textcolor, facecolor=color, zorder=2)

            # Add the rectangle patch to the plot
            ax.add_patch(rect)

            # Calculate the text coordinates
            text_x = x + width / 2 
            text_y = y + 1 * height / 3

            # Calculate the angle text coordinates
            angle_x = text_x
            angle_y = text_y + 1 * height / 2.3

            # Add the text
            ax.text(text_x, text_y, gatename, ha='center', va='center', zorder=2, fontsize=10)
            ax.text(angle_x, angle_y, str(round(angle, 2)), ha='center', va='center', zorder=2, fontsize=8)


    def draw_cnot_gate(self, ax, xposition, color, qubits):
        width = self.gatewidth
        height = self.gateheight
        control, target = qubits

        # Calculate the y-coordinates of the control and target qubits
        control_y = control
        target_y = target

        # Calculate the center position of the CNOT gate
        control_x_center = xposition
        target_x_center = xposition
            
        # Draw control qubit circle
        control_radius = min(width, height) * 0.2
        control_circle = patches.Circle((control_x_center, control_y), control_radius, edgecolor=self.textcolor, facecolor=color, zorder=2)
        ax.add_patch(control_circle)
            
        # Draw the target qubit circle
        target_radius = min(width, height) * 0.3  # You can adjust this as per your needs
        target_circle = patches.Circle((target_x_center, target_y), target_radius, edgecolor=self.textcolor, facecolor=color, zorder=2)
        ax.add_patch(target_circle)

        # Draw the white plus sign on the target qubit circle
        plus_length = target_radius * 0.8
        vertical_line = [(target_x_center, target_y - plus_length/2), (target_x_center, target_y + plus_length/2)]
        horizontal_line = [(target_x_center - plus_length/2, target_y), (target_x_center + plus_length/2, target_y)]
            
        ax.plot(*zip(*vertical_line), color=self.textcolor, lw=2, zorder=3)  # zorder 3 ensures it's drawn on top of the circle
        ax.plot(*zip(*horizontal_line), color=self.textcolor, lw=2, zorder=3)
            
        # Draw a vertical line connecting the control and target qubits
        if control_y < target_y:
            ax.plot([control_x_center, target_x_center], [control_y + control_radius, target_y - target_radius], color=self.textcolor, zorder=2, linewidth=2)
        else:
            ax.plot([control_x_center, target_x_center], [control_y - control_radius, target_y + target_radius], color=self.textcolor, zorder=2, linewidth=2)
        return

    def draw_control_gate(self, ax, xposition, color, qubits, gatename, params=None):
        width = self.gatewidth
        height = self.gateheight
        control, target = qubits

        # Calculate the y-coordinates of the control and target qubits
        control_y = control
        target_y = target

        # Calculate the center position of the CNOT gate
        control_x_center = xposition
        target_x_center = xposition
            
        # Draw control qubit circle
        control_radius = min(width, height) * 0.2
        control_circle = patches.Circle((control_x_center, control_y), control_radius, edgecolor=self.textcolor, facecolor=color, zorder=2)
        ax.add_patch(control_circle)

        
        # Draw a vertical line connecting the control and target qubits
        ax.plot([control_x_center, target_x_center], [control_y, target_y], color=self.textcolor, linewidth=1.5, zorder=2)

        # Draw the target qubit gate
        if gatename not in self.rotations:
            self.draw_simple_gate(ax, target_x_center, color, [target], gatename)
        else:
            if params is None:
                raise ValueError("Attempted to draw a rotation gate but angle is None")
            self.draw_rotation_gate(ax, target_x_center, color, [target], params, gatename)

        return
