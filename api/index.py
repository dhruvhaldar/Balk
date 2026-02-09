from flask import Flask, request, jsonify
from balk.node import Node
from balk.material import Material
from balk.section import Section
from balk.element import Beam3D
from balk.model import Model
from balk.solver import StaticSolver
import numpy as np

app = Flask(__name__)

@app.route('/api/solve', methods=['POST'])
def solve():
    data = request.json
    
    # Extract parameters
    try:
        E = float(data.get('E', 210e9))
        G = float(data.get('G', 80e9))
        A = float(data.get('A', 1e-3))
        Iy = float(data.get('Iy', 1e-5))
        Iz = float(data.get('Iz', 1e-5))
        J = float(data.get('J', 1e-6))
        Cw = float(data.get('Cw', 1e-8))
        length = float(data.get('length', 2.0))
        n_elems = int(data.get('n_elems', 10))
        load_val = float(data.get('load', 1000.0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid input parameters'}), 400

    # Create Material and Section
    mat = Material(E=E, G=G)
    sec = Section(A=A, Iy=Iy, Iz=Iz, J=J, Cw=Cw)

    # Create Model
    model = Model()
    nodes = []
    for i in range(n_elems + 1):
        n = Node(i, i * length / n_elems, 0, 0)
        model.add_node(n)
        nodes.append(n)

    for i in range(n_elems):
        el = Beam3D(nodes[i], nodes[i+1], mat, sec)
        model.add_element(el)

    # Boundary Conditions (Cantilever at Node 0)
    for i in range(7):
        model.add_constraint(0, i)

    # Load (Point load at tip)
    # Applying load in Z direction (vertical) for bending, or Torsion if requested
    # For this demo, let's apply a vertical load Pz = load_val
    model.add_load(n_elems, [0, 0, load_val, 0, 0, 0, 0])

    # Solve
    solver = StaticSolver(model)
    u = solver.solve()

    # Prepare results for frontend
    results = {
        'x': [n.x for n in nodes],
        'uz': [], # Vertical displacement
        'tx': []  # Twist angle (if we added torsion)
    }

    for i, n in enumerate(nodes):
        # Global indices for node i start at i*7
        # uz is index 2, tx is index 3
        dof_start = i * 7
        uz = u[dof_start + 2]
        tx = u[dof_start + 3]
        results['uz'].append(float(uz))
        results['tx'].append(float(tx))

    return jsonify(results)

# For local development
if __name__ == '__main__':
    app.run(port=5328)
