class Material:
    """
    Represents an isotropic linear elastic material.

    Attributes:
        E (float): Young's Modulus (Elastic Modulus).
        G (float): Shear Modulus.
        rho (float): Density (mass per unit volume).
        nu (float): Poisson's ratio.
    """
    def __init__(self, E, G=None, nu=None, rho=0.0):
        """
        Initialize the material.
        
        Args:
            E (float): Young's Modulus.
            G (float, optional): Shear Modulus. If None, calculated from E and nu.
            nu (float, optional): Poisson's ratio. If None, calculated from E and G.
            rho (float): Density.
        """
        self.E = float(E)
        self.rho = float(rho)

        if G is not None and nu is not None:
            self.G = float(G)
            self.nu = float(nu)
            # Check consistency (optional warning could be added)
        elif G is not None:
            self.G = float(G)
            self.nu = self.E / (2 * self.G) - 1
        elif nu is not None:
            self.nu = float(nu)
            self.G = self.E / (2 * (1 + self.nu))
        else:
            raise ValueError("Must provide either G or nu in addition to E.")

    def __repr__(self):
        return f"Material(E={self.E:.2e}, G={self.G:.2e}, nu={self.nu:.2f}, rho={self.rho:.2f})"
