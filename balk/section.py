class Section:
    """
    Represents the cross-sectional properties of a thin-walled beam.

    Attributes:
        A (float): Cross-sectional area.
        Iy (float): Moment of inertia about the local y-axis (bending in local xz-plane).
        Iz (float): Moment of inertia about the local z-axis (bending in local xy-plane).
        J (float): St. Venant torsional constant.
        Cw (float): Vlasov warping constant.
    """
    def __init__(self, A, Iy, Iz, J, Cw):
        self.A = float(A)
        self.Iy = float(Iy)
        self.Iz = float(Iz)
        self.J = float(J)
        self.Cw = float(Cw)

    def __repr__(self):
        return f"Section(A={self.A:.2e}, Iy={self.Iy:.2e}, Iz={self.Iz:.2e}, J={self.J:.2e}, Cw={self.Cw:.2e})"
