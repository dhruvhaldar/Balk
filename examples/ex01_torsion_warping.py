import numpy as np
import matplotlib.pyplot as plt
from balk.node import Node
from balk.material import Material
from balk.section import Section
from balk.element import Beam3D
from balk.model import Model
from balk.solver import StaticSolver
from balk.plotter import Plotter

def run_torsion_example():
    print("Example 1: Torsion of a Cantilever I-Beam with Warping")
    
    # Material: Steel
    E = 210e9
    G = 80e9
    mat = Material(E=E, G=G)
    
    # Section: I-beam (IPE 300 approx)
    # h = 300 mm, b = 150 mm, tw = 7.1 mm, tf = 10.7 mm
    # A = 53.8e-4 m2
    # Iy (weak axis) = 6.04e-6 m4 (bending about z)
    # Iz (strong axis) = 83.6e-6 m4 (bending about y)
    # J = 2.01e-7 m4
    # Cw = 1.26e-7 m6 (Vlasov warping constant)
    
    sec = Section(A=53.8e-4, Iy=6.04e-6, Iz=83.6e-6, J=2.01e-7, Cw=1.26e-7)
    
    # Model 1: Restrained Warping (Fixed end: all DOFs fixed including warping)
    model1 = Model()
    L = 2.0 # 2 meters
    n_elems = 10
    
    nodes1 = []
    for i in range(n_elems + 1):
        n = Node(i, i * L / n_elems, 0, 0)
        model1.add_node(n)
        nodes1.append(n)
        
    for i in range(n_elems):
        el = Beam3D(nodes1[i], nodes1[i+1], mat, sec)
        model1.add_element(el)
        
    # Fix Node 0 (Fixed Support) - Restrained Warping
    # Fix all 7 DOFs: u, v, w, tx, ty, tz, tw
    for i in range(7):
        model1.add_constraint(0, i)
        
    # Apply Torque Mx at tip (Node n_elems)
    T = 1000.0 # Nm
    model1.add_load(n_elems, [0, 0, 0, T, 0, 0, 0])
    
    solver1 = StaticSolver(model1)
    u1 = solver1.solve()
    
    # Get twist angle at tip
    # Node n_elems has global indices for tx at: index 3
    # Wait, need to find the global index.
    # Node.dof_indices[3]
    tip_twist1 = u1[nodes1[-1].dof_indices[3]]
    
    # Model 2: Free Warping (Fixed end: warping free)
    model2 = Model()
    nodes2 = []
    for i in range(n_elems + 1):
        n = Node(i, i * L / n_elems, 0, 0)
        model2.add_node(n)
        nodes2.append(n)
        
    for i in range(n_elems):
        el = Beam3D(nodes2[i], nodes2[i+1], mat, sec)
        model2.add_element(el)
        
    # Fix Node 0 (Pinned Torsion? No, Fixed but warping free)
    # Fix u, v, w, tx, ty, tz. Allow tw (index 6).
    for i in range(6):
        model2.add_constraint(0, i)
        
    # Apply Torque
    model2.add_load(n_elems, [0, 0, 0, T, 0, 0, 0])
    
    solver2 = StaticSolver(model2)
    u2 = solver2.solve()
    
    tip_twist2 = u2[nodes2[-1].dof_indices[3]]
    
    print(f"Tip Twist (Restrained Warping): {tip_twist1:.6f} rad")
    print(f"Tip Twist (Free Warping):       {tip_twist2:.6f} rad")
    
    ratio = tip_twist2 / tip_twist1
    print(f"Ratio (Free/Restrained): {ratio:.2f}")
    
    # Analytical Solution (St. Venant only): theta = T*L / (G*J)
    theta_sv = T * L / (G * sec.J)
    print(f"Analytical St. Venant (No Warping Stiffness): {theta_sv:.6f} rad")
    
    print("-" * 30)
    print("The restrained warping case is stiffer because it engages the Vlasov stiffness (ECw).")
    print("The free warping case should match St. Venant solution closely if L is large,")
    print("but near the support the warping constraint has an effect if restrained.")
    print("Wait, Free Warping at support means warping is allowed.")
    print("This means the warping stress sigma_w = 0 at support.")
    print("Actually, 'Free Warping' usually refers to the condition where warping is unconstrained.")
    print("In that case, the differential equation solution matches St. Venant torsion for constant torque.")
    print("So Model 2 should match theta_sv exactly.")
    
    diff = abs(tip_twist2 - theta_sv) / theta_sv * 100
    print(f"Difference Model 2 vs St. Venant: {diff:.2f}%")
    
    # Visualization
    plotter = Plotter(model1)
    plotter.plot_deformed(u1, scale=100, title="Restrained Warping Deformed Shape (scaled)")
    # plt.show() # Uncomment to show plot

if __name__ == "__main__":
    run_torsion_example()
