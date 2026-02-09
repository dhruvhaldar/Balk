import numpy as np

class Node:
    """
    Represents a node in the finite element model.

    Attributes:
        id (int): Unique identifier for the node.
        x (float): X-coordinate.
        y (float): Y-coordinate.
        z (float): Z-coordinate.
        dof_indices (list): List of global DOF indices associated with this node.
                            Assigned during model assembly.
    """
    def __init__(self, id, x, y, z):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.dof_indices = []

    @property
    def coords(self):
        """Returns the coordinates as a numpy array."""
        return np.array([self.x, self.y, self.z])

    def __repr__(self):
        return f"Node(id={self.id}, x={self.x}, y={self.y}, z={self.z})"
