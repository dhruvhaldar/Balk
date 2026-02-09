import numpy as np
from balk.node import Node
from balk.element import Beam3D

class Model:
    """
    Finite Element Model Manager.
    """
    def __init__(self):
        self.nodes = {}
        self.elements = []
        self.constraints = {} # map node_id -> set of constrained dof indices (0-6)
        self.loads = {} # map node_id -> array of 7 values (forces/moments)
        self.ndof_per_node = 7
        self._dof_map_generated = False
        self.total_dofs = 0

    def add_node(self, node):
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists.")
        self.nodes[node.id] = node
        self._dof_map_generated = False

    def add_element(self, element):
        self.elements.append(element)

    def add_constraint(self, node_id, dof_index):
        """
        Constrains a specific DOF at a node (sets displacement to 0).
        dof_index: 0=u, 1=v, 2=w, 3=tx, 4=ty, 5=tz, 6=tw (warping)
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found.")
        if node_id not in self.constraints:
            self.constraints[node_id] = set()
        self.constraints[node_id].add(dof_index)

    def add_load(self, node_id, load_vector):
        """
        Adds a load vector to a node.
        load_vector: array-like of length 7.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found.")
        if node_id not in self.loads:
            self.loads[node_id] = np.zeros(7)
        self.loads[node_id] += np.array(load_vector)

    def _generate_dof_map(self):
        """Assigns global DOF indices to nodes."""
        current_dof = 0
        sorted_node_ids = sorted(self.nodes.keys())
        for nid in sorted_node_ids:
            node = self.nodes[nid]
            node.dof_indices = list(range(current_dof, current_dof + self.ndof_per_node))
            current_dof += self.ndof_per_node
        self.total_dofs = current_dof
        self._dof_map_generated = True

    def assemble_stiffness(self):
        if not self._dof_map_generated:
            self._generate_dof_map()
        
        K_global = np.zeros((self.total_dofs, self.total_dofs))
        
        for el in self.elements:
            k_el_global = el.global_stiffness_matrix()
            # Get global DOF indices for the element nodes
            dofs = el.node1.dof_indices + el.node2.dof_indices
            
            # Assemble
            K_global[np.ix_(dofs, dofs)] += k_el_global
            
        return K_global

    def assemble_geometric_stiffness(self, element_axial_forces):
        """
        Assembles the global geometric stiffness matrix.
        element_axial_forces: dict mapping element index to axial force P.
                              Or list matching elements order.
        """
        if not self._dof_map_generated:
            self._generate_dof_map()
            
        Kg_global = np.zeros((self.total_dofs, self.total_dofs))
        
        if isinstance(element_axial_forces, dict):
            forces = [element_axial_forces.get(i, 0.0) for i in range(len(self.elements))]
        else:
            forces = element_axial_forces

        for i, el in enumerate(self.elements):
            P = forces[i]
            if abs(P) < 1e-9:
                continue
            
            kg_el_global = el.global_geometric_stiffness_matrix(P)
            dofs = el.node1.dof_indices + el.node2.dof_indices
            
            Kg_global[np.ix_(dofs, dofs)] += kg_el_global
            
        return Kg_global

    def get_load_vector(self):
        if not self._dof_map_generated:
            self._generate_dof_map()
            
        F = np.zeros(self.total_dofs)
        for nid, load in self.loads.items():
            node = self.nodes[nid]
            dofs = node.dof_indices
            F[dofs] += load
        return F

    def get_constrained_dofs(self):
        if not self._dof_map_generated:
            self._generate_dof_map()
            
        constrained = []
        for nid, dofs in self.constraints.items():
            node = self.nodes[nid]
            for d in dofs:
                constrained.append(node.dof_indices[d])
        return np.unique(constrained)
