import numpy as np
import pytest
from balk.node import Node
from balk.material import Material
from balk.section import Section
from balk.element import Beam3D

@pytest.fixture
def basic_element():
    n1 = Node(1, 0, 0, 0)
    n2 = Node(2, 1, 0, 0) # Length = 1
    mat = Material(E=200e9, nu=0.3)
    sec = Section(A=0.01, Iy=1e-5, Iz=1e-5, J=1e-6, Cw=1e-8)
    return Beam3D(n1, n2, mat, sec)

def test_stiffness_matrix_symmetry(basic_element):
    k = basic_element.local_stiffness_matrix()
    assert np.allclose(k, k.T)

def test_geometric_stiffness_symmetry(basic_element):
    kg = basic_element.geometric_stiffness_matrix(axial_force=-1000)
    assert np.allclose(kg, kg.T)

def test_rigid_body_modes(basic_element):
    k = basic_element.local_stiffness_matrix()
    vals, _ = np.linalg.eigh(k)
    # Count zero eigenvalues (should be at least 6 for 3D beam)
    # DOFs: 14.
    # Rigid body modes: 6 (3 trans + 3 rot).
    # Warping DOF theta_x' is internal deformation?
    # If we have rigid body motion, theta_x' should be zero (except for rigid rotation).
    # Rigid rotation theta_x = const => theta_x' = 0.
    # So yes, 6 zero eigenvalues.
    zero_eigenvalues = np.sum(np.abs(vals) < 1e-4)
    assert zero_eigenvalues == 6

def test_axial_stiffness(basic_element):
    k = basic_element.local_stiffness_matrix()
    # Apply displacement u2 = 0.001
    u = np.zeros(14)
    u[7] = 0.001 # u at node 2
    f = k @ u
    
    # Expected Force = EA/L * u
    # E=200e9, A=0.01, L=1. F = 2e9 * 0.01 * 0.001 = 20,000
    expected_force = basic_element.material.E * basic_element.section.A * 0.001 / basic_element.length()
    assert np.isclose(f[7], expected_force)
    assert np.isclose(f[0], -expected_force)

def test_transformation_matrix_identity(basic_element):
    # Element is along X-axis, so T should be roughly identity (with some block shifts maybe?)
    # Our T is block_diag(R^T, R^T) with R=I.
    # So T should be Identity.
    T = basic_element.transformation_matrix()
    assert np.allclose(T, np.eye(14))

def test_transformation_matrix_rotation():
    n1 = Node(1, 0, 0, 0)
    n2 = Node(2, 0, 1, 0) # Along Y-axis
    mat = Material(E=200e9, nu=0.3)
    sec = Section(A=0.01, Iy=1e-5, Iz=1e-5, J=1e-6, Cw=1e-8)
    el = Beam3D(n1, n2, mat, sec)
    
    T = el.transformation_matrix()
    # Check shape
    assert T.shape == (14, 14)
    # Check orthogonality
    assert np.allclose(T @ T.T, np.eye(14))
    
