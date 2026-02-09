import numpy as np
import pytest
from balk.node import Node
from balk.material import Material
from balk.section import Section
from balk.element import Beam3D
from balk.model import Model
from balk.solver import StaticSolver

def test_cantilever_torsion_free_warping():
    E = 210e9
    G = 80e9
    mat = Material(E=E, G=G)
    sec = Section(A=1e-3, Iy=1e-5, Iz=1e-5, J=1e-6, Cw=1e-8)
    
    L = 2.0
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
        
    # Free Warping: Fix u, v, w, tx, ty, tz at Node 0. Allow tw (index 6).
    for i in range(6):
        model.add_constraint(0, i)
        
    T = 1000.0
    model.add_load(n_elems, [0, 0, 0, T, 0, 0, 0])
    
    solver = StaticSolver(model)
    u = solver.solve()
    
    twist = u[nodes[-1].dof_indices[3]]
    expected = T * L / (G * sec.J)
    
    # Allow 1% error (should be very close for free warping)
    assert np.isclose(twist, expected, rtol=0.01)

def test_cantilever_torsion_restrained_warping():
    E = 210e9
    G = 80e9
    mat = Material(E=E, G=G)
    sec = Section(A=1e-3, Iy=1e-5, Iz=1e-5, J=1e-6, Cw=1e-7) # Higher Cw to see effect
    
    L = 2.0
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
        
    # Restrained Warping: Fix all 7 DOFs at Node 0.
    for i in range(7):
        model.add_constraint(0, i)
        
    T = 1000.0
    model.add_load(n_elems, [0, 0, 0, T, 0, 0, 0])
    
    solver = StaticSolver(model)
    u = solver.solve()
    
    twist_restrained = u[nodes[-1].dof_indices[3]]
    twist_free = T * L / (G * sec.J)
    
    # Twist should be significantly smaller due to warping stiffness
    assert twist_restrained < twist_free
    # Maybe check specific analytical solution for restrained warping?
    # theta(L) = (T/GJ) * [L - tanh(kL)/k] where k = sqrt(GJ/ECw)
    k = np.sqrt((G * sec.J) / (E * sec.Cw))
    analytical_restrained = (T / (G * sec.J)) * (L - np.tanh(k * L) / k)
    
    # With 4 elements, accuracy might be so-so. Let's allow 5% error.
    assert np.isclose(twist_restrained, analytical_restrained, rtol=0.05)
