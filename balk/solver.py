import numpy as np
from scipy.linalg import eig

class StaticSolver:
    def __init__(self, model):
        self.model = model

    def solve(self):
        # 1. Assemble K and F
        self.model._generate_dof_map() # Ensure DOFs are assigned
        K = self.model.assemble_stiffness()
        F = self.model.get_load_vector()
        
        # 2. Apply Boundary Conditions
        constrained_dofs = self.model.get_constrained_dofs()
        free_dofs = np.setdiff1d(np.arange(self.model.total_dofs), constrained_dofs)
        
        if len(free_dofs) == 0:
            return np.zeros(self.model.total_dofs)

        # Partition matrices
        K_ff = K[np.ix_(free_dofs, free_dofs)]
        F_f = F[free_dofs]
        
        # 3. Solve
        u_f = np.linalg.solve(K_ff, F_f)
        
        # 4. Reconstruct full displacement vector
        u = np.zeros(self.model.total_dofs)
        u[free_dofs] = u_f
        
        return u

    def compute_element_forces(self, u):
        """
        Computes internal forces for all elements based on displacement u.
        Returns a list of force vectors (one per element).
        For now, we return the local element forces (14x1 vector).
        """
        forces = []
        for el in self.model.elements:
            # Extract element DOFs
            dofs = el.node1.dof_indices + el.node2.dof_indices
            u_global = u[dofs]
            
            # Transform to local
            T = el.transformation_matrix()
            u_local = T @ u_global
            
            # Compute forces: f = k_local * u_local
            k_local = el.local_stiffness_matrix()
            f_local = k_local @ u_local
            forces.append(f_local)
        return forces

class BucklingSolver:
    def __init__(self, model):
        self.model = model

    def solve(self, num_modes=1):
        """
        Solves the linear buckling eigenvalue problem.
        1. Runs static analysis with current loads to get internal axial forces.
        2. Assembles geometric stiffness matrix Kg.
        3. Solves (K + lambda * Kg) * phi = 0.
        
        Returns:
            eigenvalues (critical load factors), eigenvectors (buckling modes), free_dofs
        """
        # 1. Static Analysis to get internal forces
        static_solver = StaticSolver(self.model)
        u_static = static_solver.solve()
        element_forces = static_solver.compute_element_forces(u_static)
        
        # Extract axial forces (N) from element forces
        # Local DOF 7 (node 2 axial force) corresponds to tension.
        axial_forces = [f[7] for f in element_forces]
        
        # 2. Assemble Matrices
        K = self.model.assemble_stiffness()
        Kg = self.model.assemble_geometric_stiffness(axial_forces)
        
        # 3. Apply Boundary Conditions
        constrained_dofs = self.model.get_constrained_dofs()
        free_dofs = np.setdiff1d(np.arange(self.model.total_dofs), constrained_dofs)
        
        K_ff = K[np.ix_(free_dofs, free_dofs)]
        Kg_ff = Kg[np.ix_(free_dofs, free_dofs)]
        
        # 4. Solve Eigenvalue Problem
        # (K + lambda * Kg) v = 0  => K v = -lambda Kg v
        # A = K_ff, B = -Kg_ff. A v = lambda B v.
        vals, vecs = eig(K_ff, -Kg_ff)
        
        # Filter for real, positive values (critical load factors)
        valid_indices = []
        for i, v in enumerate(vals):
            # Check for real and positive, and finite (not inf/nan)
            if np.isreal(v) and np.real(v) > 1e-6 and np.isfinite(v):
                valid_indices.append(i)
        
        if not valid_indices:
             return np.array([]), np.array([]), free_dofs
             
        valid_vals = np.real(vals[valid_indices])
        valid_vecs = vecs[:, valid_indices]
        
        # Sort by value (smallest lambda is critical)
        idx = np.argsort(valid_vals)
        sorted_vals = valid_vals[idx]
        sorted_vecs = valid_vecs[:, idx]
        
        return sorted_vals[:num_modes], sorted_vecs[:, :num_modes], free_dofs
