import numpy as np
import pytest
from balk.node import Node
from balk.material import Material
from balk.section import Section
from balk.element import Beam3D
from balk.model import Model
from balk.solver import BucklingSolver

def test_euler_buckling():
    E = 210e9
    G = 80e9
    mat = Material(E=E, G=G)
    # Weak axis bending buckling expected
    sec = Section(A=1e-3, Iy=1e-6, Iz=2e-5, J=5e-7, Cw=1e-8)
    
    L = 4.0
    n_elems = 4
    model = Model()
    nodes = []
    for i in range(n_elems + 1):
        n = Node(i, i * L / n_elems, 0, 0)
        model.add_node(n)
        nodes.append(n)
        
    for i in range(n_elems):
        el = Beam3D(nodes[i], nodes[i+1], mat, sec)
        model.add_element(el)
        
    # Pinned-Pinned
    # Node 0: Fix u, v, w, tx
    for i in [0, 1, 2, 3]:
        model.add_constraint(0, i)
        
    # Node N: Fix v, w, tx
    for i in [1, 2, 3]:
        model.add_constraint(n_elems, i)
        
    # Apply Unit Compressive Load
    model.add_load(n_elems, [-1.0, 0, 0, 0, 0, 0, 0])
    
    solver = BucklingSolver(model)
    vals, vecs, _ = solver.solve(num_modes=1)
    
    P_cr = vals[0]
    
    # Theoretical: P = pi^2 * E * I_min / L^2
    I_min = min(sec.Iy, sec.Iz)
    P_theo = (np.pi**2 * E * I_min) / L**2
    
    # Check accuracy. With 4 elements, error should be small (few %).
    assert np.isclose(P_cr, P_theo, rtol=0.02)
