import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

class Plotter:
    def __init__(self, model):
        self.model = model
        sns.set_theme(style="whitegrid")
        
    def plot_undeformed(self, ax=None, show_nodes=True, show_labels=False):
        if ax is None:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
        # Plot Elements
        for el in self.model.elements:
            n1 = el.node1
            n2 = el.node2
            x = [n1.x, n2.x]
            y = [n1.y, n2.y]
            z = [n1.z, n2.z]
            ax.plot(x, y, z, color='gray', linestyle='--', alpha=0.5)
            
        # Plot Nodes
        if show_nodes:
            xs = [n.x for n in self.model.nodes.values()]
            ys = [n.y for n in self.model.nodes.values()]
            zs = [n.z for n in self.model.nodes.values()]
            ax.scatter(xs, ys, zs, color='black', s=20)
            
            if show_labels:
                for nid, n in self.model.nodes.items():
                    ax.text(n.x, n.y, n.z, str(nid), fontsize=8)

        self._set_axes_equal(ax)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        return ax

    def plot_deformed(self, displacement, scale=1.0, ax=None, title="Deformed Shape"):
        if ax is None:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
        # Plot Undeformed (reference)
        self.plot_undeformed(ax=ax, show_nodes=False)
        
        # Plot Deformed Elements
        # Note: Linear interpolation between nodes.
        # For better visualization of curvature, we would need to interpolate using shape functions.
        # Given "small finite element code", linear connecting deformed nodes is standard.
        
        for el in self.model.elements:
            n1 = el.node1
            n2 = el.node2
            
            # Get displacements
            # Assuming displacement vector matches global DOFs
            # Global Indices
            idx1 = n1.dof_indices
            idx2 = n2.dof_indices
            
            u1 = displacement[idx1] # [u, v, w, tx, ty, tz, tw]
            u2 = displacement[idx2]
            
            # Deformed coordinates
            # Only use translational DOFs (0, 1, 2)
            d1 = u1[:3] * scale
            d2 = u2[:3] * scale
            
            x = [n1.x + d1[0], n2.x + d2[0]]
            y = [n1.y + d1[1], n2.y + d2[1]]
            z = [n1.z + d1[2], n2.z + d2[2]]
            
            ax.plot(x, y, z, color='blue', linewidth=2)
            
        ax.set_title(f"{title} (Scale: {scale})")
        return ax

    def show(self):
        plt.show()

    def _set_axes_equal(self, ax):
        """
        Make axes of 3D plot have equal scale so that spheres appear as spheres,
        cubes as cubes, etc.
        """
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        plot_radius = 0.5 * max([x_range, y_range, z_range])

        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
