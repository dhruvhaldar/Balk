import numpy as np
from balk.node import Node
from balk.material import Material
from balk.section import Section
from balk.element import Beam3D
from balk.model import Model
from balk.solver import BucklingSolver

def run_buckling_example():
    print("Example 2: Euler Buckling of a Column")
    
    # Material: Steel
    E = 210e9
    G = 80e9
    mat = Material(E=E, G=G)
    
    # Section: IPE 100
    # h=100, b=55, tw=4.1, tf=5.7
    A = 10.3e-4 # m2
    Iy = 171e-8 # m4 (weak axis, z-axis in local frame usually? Wait standard: I_z is strong, I_y is weak)
    # Check standard: I_y usually about y-axis. I_z usually about z-axis.
    # For I-beam with web along y-axis? No, web along z-axis usually.
    # Let's assume:
    # Strong axis: I_z (bending in xy plane). I_z = 171e-8? No, IPE 100 Iz = 171e-8 is too small.
    # IPE 100 properties:
    # Iy = 171 cm4 = 171e-8 m4 (Strong axis? No wait. 171 cm4 is 1.71e-6 m4)
    # Iz = 15.9 cm4 = 15.9e-8 m4 (Weak axis)
    # Let's use generic values to avoid confusion.
    
    # Let's define a section with distinct Iy and Iz.
    # Strong axis z (bending stiffness EIz high).
    # Weak axis y (bending stiffness EIy low).
    Iz = 2.0e-5 
    Iy = 1.0e-6 # Weak axis
    J = 5.0e-7
    Cw = 1.0e-8
    
    sec = Section(A=1e-3, Iy=Iy, Iz=Iz, J=J, Cw=Cw)
    
    # Model: Pinned-Pinned Column
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
        
    # Boundary Conditions: Pinned-Pinned
    # Node 0: Fix u, v, w, tx (twist fixed). Allow rotations ty, tz.
    # Node N: Fix v, w, tx. Allow u (axial load), ty, tz.
    # Warping: Pinned usually allows warping? Or fixed?
    # "Fork support" usually means warping free (sigma_w = 0) but twist fixed.
    # So we fix tx, allow tw (index 6).
    
    # Fix Node 0: indices 0, 1, 2, 3
    for i in [0, 1, 2, 3]:
        model.add_constraint(0, i)
        
    # Fix Node N: indices 1, 2, 3
    for i in [1, 2, 3]:
        model.add_constraint(n_elems, i)
        
    # Apply Unit Compressive Load at Node N
    P_ref = -1.0
    model.add_load(n_elems, [P_ref, 0, 0, 0, 0, 0, 0])
    
    solver = BucklingSolver(model)
    vals, vecs, _ = solver.solve(num_modes=3)
    
    print("Buckling Analysis Results:")
    for i, val in enumerate(vals):
        print(f"Mode {i+1}: Critical Load P_cr = {val:.2f} N")
        
    # Theoretical Values
    # Flexural Buckling Weak Axis (Iy): P = pi^2 * E * Iy / L^2
    P_flex_y = (np.pi**2 * E * Iy) / L**2
    # Flexural Buckling Strong Axis (Iz): P = pi^2 * E * Iz / L^2
    P_flex_z = (np.pi**2 * E * Iz) / L**2
    # Torsional Buckling: P = (A/Ip) * (G*J + pi^2*E*Cw/L^2)
    # Ip = Iy + Iz approx
    Ip = Iy + Iz
    r0_sq = Ip / sec.A
    P_tor = (1 / r0_sq) * (G * J + (np.pi**2 * E * Cw) / L**2)
    
    print("-" * 30)
    print(f"Theoretical Flexural (Weak Axis):   {P_flex_y:.2f} N")
    print(f"Theoretical Flexural (Strong Axis): {P_flex_z:.2f} N")
    print(f"Theoretical Torsional:              {P_tor:.2f} N")
    
    # Identify modes
    # We can check eigenvectors to identify mode type.
    # But just comparing values is enough for now.
    
    min_theoretical = min(P_flex_y, P_flex_z, P_tor)
    print(f"Minimum Theoretical P_cr: {min_theoretical:.2f} N")
    
    error = abs(vals[0] - min_theoretical) / min_theoretical * 100
    print(f"Difference (Lowest Mode): {error:.2f}%")

if __name__ == "__main__":
    run_buckling_example()
