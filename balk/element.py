import numpy as np
from scipy.linalg import block_diag

class Beam3D:
    """
    3D Thin-Walled Beam Element with 7 DOFs per node.
    DOFs: [u, v, w, theta_x, theta_y, theta_z, theta_x_prime]
    Total 14 DOFs.
    """
    def __init__(self, node1, node2, material, section):
        self.node1 = node1
        self.node2 = node2
        self.material = material
        self.section = section
        # Default local y-axis orientation helper
        self.iy_vector = None 

    def length(self):
        return np.linalg.norm(self.node2.coords - self.node1.coords)

    def direction_cosine_matrix(self):
        """
        Computes the 3x3 rotation matrix from local to global coordinates.
        Local x is along the beam axis.
        """
        L = self.length()
        diff = self.node2.coords - self.node1.coords
        x_local = diff / L

        # arbitrary vector to define y_local (if not specified)
        # We need a robust way to define the local frame.
        # If beam is vertical (along Z), we choose global X as local Y.
        if np.allclose(x_local[:2], 0):
             temp_vec = np.array([1.0, 0.0, 0.0])
        else:
             temp_vec = np.array([0.0, 0.0, 1.0])
        
        # If a specific orientation vector is provided (not implemented yet), use it.

        y_local = np.cross(temp_vec, x_local)
        if np.linalg.norm(y_local) < 1e-6:
             # Fallback if x_local is parallel to temp_vec (should catch above, but safety)
             y_local = np.cross(np.array([0.0, 1.0, 0.0]), x_local)
        
        y_local = y_local / np.linalg.norm(y_local)
        z_local = np.cross(x_local, y_local)

        # Rotation matrix R = [x_local, y_local, z_local] (columns)
        return np.column_stack((x_local, y_local, z_local))

    def transformation_matrix(self):
        """
        Returns the 14x14 transformation matrix T.
        """
        R = self.direction_cosine_matrix()
        # R is 3x3. We need R^T for Global -> Local.
        Rt = R.T
        
        # 7x7 transformation for one node
        # displacements (3), rotations (3), warping (1)
        T_node = np.eye(7)
        T_node[0:3, 0:3] = Rt
        T_node[3:6, 3:6] = Rt
        # index 6 is warping, left as 1.0 (Identity)

        return block_diag(T_node, T_node)

    def local_stiffness_matrix(self):
        """
        Computes the 14x14 element stiffness matrix in local coordinates.
        """
        E = self.material.E
        G = self.material.G
        A = self.section.A
        Iy = self.section.Iy
        Iz = self.section.Iz
        J = self.section.J
        Cw = self.section.Cw
        L = self.length()

        k = np.zeros((14, 14))

        # Helper indices (local)
        # Node 1: u(0), v(1), w(2), tx(3), ty(4), tz(5), w(6)
        # Node 2: u(7), v(8), w(9), tx(10), ty(11), tz(12), w(13)

        # 1. Axial (u) - indices 0, 7
        k_axial = (E * A / L) * np.array([[1, -1], [-1, 1]])
        k[np.ix_([0, 7], [0, 7])] += k_axial

        # 2. Torsion (tx, w) - indices 3, 6, 10, 13
        # Vlasov Torsion: ECw * theta'''' - GJ * theta'' = m
        # DOFs: [theta_x1, theta'_x1, theta_x2, theta'_x2] -> [3, 6, 10, 13]
        
        # Pure warping part (ECw) - analogous to bending beam stiffness
        # Corresponds to Hermite polynomials for theta_x
        k_w_bending = (E * Cw / L**3) * np.array([
            [12, 6*L, -12, 6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L, 12, -6*L],
            [6*L, 2*L**2, -6*L, 4*L**2]
        ])

        # St. Venant part (GJ) - analogous to "geometric stiffness" of a string/bar in tension
        # But with positive sign (stiffening). 
        # Integral N * v' * v' dx -> Integral GJ * theta' * theta' dx
        # Using Hermite shape functions for theta, the matrix is:
        k_w_sv = (G * J / (30 * L)) * np.array([
            [36, 3*L, -36, 3*L],
            [3*L, 4*L**2, -3*L, -L**2],
            [-36, -3*L, 36, -3*L],
            [3*L, -L**2, -3*L, 4*L**2]
        ])

        k_torsion = k_w_bending + k_w_sv
        torsion_indices = [3, 6, 10, 13]
        k[np.ix_(torsion_indices, torsion_indices)] += k_torsion

        # 3. Bending about Z (v, tz) - indices 1, 5, 8, 12
        # Beam bending in xy plane. Rotations are about z-axis (theta_z).
        # Note: In standard FEM, positive rotation theta_z is counter-clockwise.
        # Slope v' = theta_z.
        # Standard matrix for (v1, theta_z1, v2, theta_z2):
        k_bending_z = (E * Iz / L**3) * np.array([
            [12, 6*L, -12, 6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L, 12, -6*L],
            [6*L, 2*L**2, -6*L, 4*L**2]
        ])
        bending_z_indices = [1, 5, 8, 12]
        k[np.ix_(bending_z_indices, bending_z_indices)] += k_bending_z

        # 4. Bending about Y (w, ty) - indices 2, 4, 9, 11
        # Beam bending in xz plane. Rotations are about y-axis (theta_y).
        # Note: Slope w' = -theta_y (Standard convention: y cross x = -z?)
        k_bending_y = (E * Iy / L**3) * np.array([
            [12, -6*L, -12, -6*L],
            [-6*L, 4*L**2, 6*L, 2*L**2],
            [-12, 6*L, 12, 6*L],
            [-6*L, 2*L**2, 6*L, 4*L**2]
        ])
        bending_y_indices = [2, 4, 9, 11]
        k[np.ix_(bending_y_indices, bending_y_indices)] += k_bending_y

        return k

    def global_stiffness_matrix(self):
        k_local = self.local_stiffness_matrix()
        T = self.transformation_matrix()
        return T.T @ k_local @ T

    def geometric_stiffness_matrix(self, axial_force):
        """
        Computes the geometric stiffness matrix for buckling analysis.
        Assumes axial force P is constant along the element.
        P > 0 for Tension (stabilizing), P < 0 for Compression (destabilizing).
        
        This matrix includes Flexural Buckling terms (v, w) and Torsional Buckling terms (theta_x).
        """
        L = self.length()
        P = float(axial_force)
        
        k_g = np.zeros((14, 14))
        
        # 1. Flexural Buckling in xy plane (v, theta_z) - indices [1, 5, 8, 12]
        # Standard Geometric Stiffness: Coefficient P/30L
        kg_flex = (P / (30 * L)) * np.array([
            [36, 3*L, -36, 3*L],
            [3*L, 4*L**2, -3*L, -L**2],
            [-36, -3*L, 36, -3*L],
            [3*L, -L**2, -3*L, 4*L**2]
        ])
        
        indices_z = [1, 5, 8, 12] # v, theta_z
        k_g[np.ix_(indices_z, indices_z)] += kg_flex
        
        # 2. Flexural Buckling in xz plane (w, theta_y) - indices [2, 4, 9, 11]
        # Same matrix structure but with sign flips for rotation terms due to w' = -theta_y
        kg_flex_y = kg_flex.copy()
        # Flip signs for rows/cols corresponding to rotation (indices 1 and 3 in the 4x4 matrix)
        kg_flex_y[:, [1, 3]] *= -1
        kg_flex_y[[1, 3], :] *= -1
        
        indices_y = [2, 4, 9, 11] # w, theta_y
        k_g[np.ix_(indices_y, indices_y)] += kg_flex_y

        # 3. Torsional Buckling (theta_x, theta_x') - indices [3, 6, 10, 13]
        # Work term: Integral P * r0^2 * (theta_x')^2 dx
        # r0^2 = (Iy + Iz) / A (approx for doubly symmetric)
        r0_sq = (self.section.Iy + self.section.Iz) / self.section.A
        
        kg_torsion = (P * r0_sq / (30 * L)) * np.array([
            [36, 3*L, -36, 3*L],
            [3*L, 4*L**2, -3*L, -L**2],
            [-36, -3*L, 36, -3*L],
            [3*L, -L**2, -3*L, 4*L**2]
        ])
        
        indices_x = [3, 6, 10, 13] # theta_x, theta_x'
        k_g[np.ix_(indices_x, indices_x)] += kg_torsion
        
        return k_g

    def global_geometric_stiffness_matrix(self, axial_force):
        kg_local = self.geometric_stiffness_matrix(axial_force)
        T = self.transformation_matrix()
        return T.T @ kg_local @ T
