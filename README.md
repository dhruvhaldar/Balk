# Balk - SD2411 Lightweight Structures and FEM Solver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

**Balk** is a Python-based Finite Element Method (FEM) solver designed for the analysis of thin-walled beam structures, inspired by the KTH course **[SD2411 Lightweight Structures and FEM](https://www.kth.se/student/kurser/kurs/SD2411)**.

This project implements advanced structural mechanics concepts such as **Vlasov torsion**, **warping**, and **instability (buckling)**, providing a computational tool to explore the behavior of lightweight structural elements.

## Syllabus Coverage

This project directly addresses the core learning outcomes of SD2411:

| SD2411 Syllabus Topic | Implementation in Balk |
| :--- | :--- |
| **"Analysis of structural elements... for lightweight structures"** | Implementation of 3D beam elements capable of modeling frames and trusses. |
| **"Introduction to the finite element method"** | Core FEM implementation: Stiffness matrix assembly, boundary conditions, solvers. |
| **"Bending, shear, torsion and warping of open... thin-walled beams"** | `Beam3D` element includes: <br> - Euler-Bernoulli bending ($EI$) <br> - St. Venant torsion ($GJ$) <br> - **Vlasov warping** ($EC_w$) |
| **"Local and global instability of beams"** | **Linear Buckling Analysis** using geometric stiffness matrices ($K_g$). Captures Euler buckling and torsional buckling modes. |
| **"Finite element codes... for analysis of basic structural elements"** | Complete Python codebase with `Node`, `Element`, `Model`, and `Solver` classes. |
| **"Write a small finite element code"** | The project is a concise, educational FEM implementation (~500 lines of code). |

## Theoretical Background

### Thin-Walled Beams and Warping
Unlike standard beam theory which assumes plane sections remain plane, thin-walled open sections (like I-beams and channels) exhibit **warping**—out-of-plane deformation of the cross-section. 

The governing equation for non-uniform torsion (Vlasov torsion) is:

$$ E C_w \frac{d^4 \phi}{dx^4} - G J \frac{d^2 \phi}{dx^2} = m_x $$

Where:
- $\phi(x)$ is the angle of twist.
- $GJ$ is the St. Venant torsional stiffness.
- $EC_w$ is the warping stiffness ($C_w$ is the warping constant).

**Balk** implements a 14-DOF beam element (7 DOFs per node) where the 7th DOF is the **rate of twist** ($\phi'$), allowing for the enforcement of warping boundary conditions (e.g., restrained warping at a fixed support).

### Stability and Buckling
Structural stability is analyzed by solving the generalized eigenvalue problem:

$$ [K + \lambda K_g] \{u\} = 0 $$

Where:
- $K$ is the elastic stiffness matrix.
- $K_g$ is the geometric stiffness matrix (dependent on internal axial forces).
- $\lambda$ is the critical load factor.

**Balk** computes $K_g$ including terms for flexural buckling (Euler) and torsional buckling (Wagner effect), allowing prediction of critical loads for columns and frames.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dhruvhaldar/balk.git
    cd balk
    ```

2.  **Create and activate a virtual environment:**

    *   **Windows:**
        ```powershell
        python -m venv venv
        .\venv\Scripts\activate.ps1
        ```
    *   **macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running Examples

The `examples/` directory contains scripts demonstrating the capabilities of the solver.

**Example 1: Torsion and Warping**
Demonstrates the effect of warping restraint on the torsional stiffness of an I-beam.
```bash
python examples/ex01_torsion_warping.py
```
*Output: Comparison of twist angle for free vs. restrained warping.*

**Example 2: Euler Buckling**
Calculates the critical buckling load of a column.
```bash
python examples/ex02_buckling.py
```
*Output: Critical loads for first 3 modes, compared with analytical Euler formulas.*

### Creating Your Own Model

```python
from balk.node import Node
from balk.material import Material
from balk.section import Section
from balk.element import Beam3D
from balk.model import Model
from balk.solver import StaticSolver
from balk.plotter import Plotter

# 1. Define Material and Section
mat = Material(E=210e9, nu=0.3)
sec = Section(A=1e-3, Iy=1e-5, Iz=1e-5, J=1e-6, Cw=1e-8)

# 2. Create Model
model = Model()
n1 = Node(1, 0, 0, 0)
n2 = Node(2, 2.0, 0, 0)
model.add_node(n1)
model.add_node(n2)
el = Beam3D(n1, n2, mat, sec)
model.add_element(el)

# 3. Apply Boundary Conditions (Fix Node 1)
for i in range(7):
    model.add_constraint(1, i)

# 4. Apply Loads (Force at Node 2)
model.add_load(2, [0, 1000, 0, 0, 0, 0, 0])

# 5. Solve
solver = StaticSolver(model)
u = solver.solve()

# 6. Visualize
plotter = Plotter(model)
plotter.plot_deformed(u, scale=50)
plotter.show()
```

## Project Structure

-   `balk/`
    -   `node.py`: Nodal definitions.
    -   `element.py`: `Beam3D` implementation (Stiffness & Geometric Stiffness).
    -   `model.py`: Assembly of global matrices.
    -   `solver.py`: Static and Eigenvalue solvers.
    -   `section.py`: Cross-section properties.
    -   `material.py`: Material definitions.
    -   `plotter.py`: 3D visualization using Matplotlib/Seaborn.
-   `tests/`: Unit and End-to-End tests (pytest).
-   `examples/`: Usage demonstrations.

## License

MIT License. See `LICENSE` for details.
