import numpy as np
import pytest
from balk.node import Node
from balk.material import Material
from balk.section import Section
from balk.element import Beam3D
from balk.model import Model
from balk.solver import StaticSolver, BucklingSolver

@pytest.fixture
def simple_model():
    m = Model()
    n1 = Node(1, 0, 0, 0)
    n2 = Node(2, 1, 0, 0) # L=1
    m.add_node(n1)
    m.add_node(n2)
    
    mat = Material(E=1e5, nu=0.3)
    sec = Section(A=1.0, Iy=1.0, Iz=1.0, J=1.0, Cw=1.0)
    el = Beam3D(n1, n2, mat, sec)
    m.add_element(el)
    
    return m

def test_static_axial(simple_model):
    # Fix Node 1 completely
    for i in range(7):
        simple_model.add_constraint(1, i)
    
    # Fix Node 2 all except u (axial)
    for i in range(1, 7):
        simple_model.add_constraint(2, i)
        
    # Apply load at Node 2, u direction (index 0)
    F = 100.0
    simple_model.add_load(2, [F, 0, 0, 0, 0, 0, 0])
    
    solver = StaticSolver(simple_model)
    u = solver.solve()
    
    # Check displacement at Node 2 (index 7 in global array)
    # Global indices: Node 1 (0-6), Node 2 (7-13).
    # u2 is at index 7.
    u2 = u[7]
    
    # Theoretical: delta = FL / EA
    # F=100, L=1, E=1e5, A=1. delta = 100 / 1e5 = 1e-3
    assert np.isclose(u2, 1e-3)

def test_buckling_one_element(simple_model):
    # Euler buckling of pinned-pinned column (or fixed-fixed, etc.)
    # Let's do Pinned-Pinned for Bending about Z.
    # Pinned: u=0, v=0, w=0, tx=0 at both ends?
    # No, Pinned allows rotation about bending axis.
    # Fix: u, v, w, tx at Node 1.
    # Fix: v, w, tx at Node 2 (allow u for loading).
    # Allow rotation theta_z (bending).
    
    # Constraint Setup:
    # Node 1: Fix 0,1,2,3,4,6 (Allow 5? No, pinned allows rotation. So don't fix 5.)
    # Node 2: Fix 1,2,3,4,6 (Allow 0-u, 5-theta_z)
    
    for i in [0, 1, 2, 3, 4, 6]:
        simple_model.add_constraint(1, i)
    for i in [1, 2, 3, 4, 6]:
        simple_model.add_constraint(2, i)
        
    # Apply compressive load at Node 2
    P_ref = -1.0
    simple_model.add_load(2, [P_ref, 0, 0, 0, 0, 0, 0])
    
    solver = BucklingSolver(simple_model)
    vals, vecs, _ = solver.solve(num_modes=1)
    
    # One element solution for Pinned-Pinned: P_cr = 12 EI / L^2
    # E=1e5, Iz=1, L=1. P_cr = 12e5.
    # Load factor lambda should be 12e5 (since P_ref = 1).
    
    assert len(vals) > 0
    P_cr = vals[0]
    
    # With 1 element, error is expected but formula is exact for the discrete system.
    expected = 12 * 1e5 * 1.0 / 1.0**2
    assert np.isclose(P_cr, expected, rtol=1e-3)

