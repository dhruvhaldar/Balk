import pytest
from balk.node import Node
from balk.material import Material
from balk.section import Section

def test_node_creation():
    n = Node(1, 10.0, 20.0, 30.0)
    assert n.id == 1
    assert n.x == 10.0
    assert n.y == 20.0
    assert n.z == 30.0
    assert n.dof_indices == []

def test_material_creation_with_nu():
    m = Material(E=200e9, nu=0.3)
    expected_G = 200e9 / (2 * (1 + 0.3))
    assert abs(m.G - expected_G) < 1e-6
    assert m.nu == 0.3

def test_material_creation_with_G():
    m = Material(E=200e9, G=76.92e9)
    expected_nu = 200e9 / (2 * 76.92e9) - 1
    assert abs(m.nu - expected_nu) < 1e-3

def test_section_creation():
    s = Section(A=1e-3, Iy=2e-6, Iz=3e-6, J=1e-7, Cw=1e-9)
    assert s.A == 1e-3
    assert s.Iy == 2e-6
    assert s.Iz == 3e-6
    assert s.J == 1e-7
    assert s.Cw == 1e-9
