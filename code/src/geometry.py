import numpy as np
import scipy.special as special
import scipy.sparse as sp
import scipy.sparse.linalg as splinalg

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
from matplotlib import patches

import quadtree
import fem

# Here we build up the geometry.
# The code is included in the notebook because it makes it easier to see
# how the vertices get numbered.
class Geometry:
    def __init__(self, level, is_dirichlet):
        center = np.array([0.5, 0.5])
        size = 1.0
        self.grid = quadtree.Quadtree(center=center, size=size)
        self.grid.split_to_level(level)

        self.vertices_coords_to_idx, \
        self.number_of_vertices_per_level, \
        self.boundary_vertices = self.grid.get_vertices()
        self.vertices_idx_to_coords = {v: k for k, v in self.vertices_coords_to_idx.items()}
        self.grid.set_all_cell_vertices(self.vertices_coords_to_idx)
        self.grid.set_all_cell_indices()

        self.dirichlet_vertices = set()
        for v in self.boundary_vertices:
            eps = 1e-8
            if is_dirichlet(self.vertices_idx_to_coords[v]):
                self.dirichlet_vertices.add(v)

        dirichlet_vertices_array = np.array([*self.dirichlet_vertices])
        # We do not store the data for Dirichlet values

        self.data_size_per_level = []
        for level in range(self.grid.get_max_level()+1):
            n_vert = self.number_of_vertices_per_level[level]
            n_dirichlet_vert = len(
                dirichlet_vertices_array[
                    dirichlet_vertices_array < n_vert])
            self.data_size_per_level.append(n_vert - n_dirichlet_vert)

        self.vertex_idx_to_data_idx = np.zeros(self.number_of_vertices_per_level[-1], dtype=np.int32)
        self.data_idx_to_vertex_idx = np.zeros(self.data_size_per_level[-1], dtype=np.int32)
        cur_data_idx = 0
        for i in range(self.number_of_vertices_per_level[-1]):
            if i in self.dirichlet_vertices:
                self.vertex_idx_to_data_idx[i] = -1
            else:
                self.vertex_idx_to_data_idx[i] = cur_data_idx
                self.data_idx_to_vertex_idx[cur_data_idx] = i
                cur_data_idx += 1       

def plot_solution(geometry, discretization, dirichlet_val, sol,level):   # First find minimum and maximum material parameter
    min_k, max_k = float('inf'), float('-inf')
    for cell in geometry.grid.dfs(only_level=level):
        k = discretization.eval_k(cell.center[0], cell.center[1])
        min_k = min(k, min_k)
        max_k = max(k, max_k)

    # Set up color scales for the solution and the material k.
    norm_solution = mpl.colors.Normalize(vmin=min(0.0,sol.min()), vmax=max(1.0,sol.max()))
    norm_k = mpl.colors.Normalize(vmin=min_k, vmax=max_k)
    cmap = cm.viridis
    color_mapper_solution = cm.ScalarMappable(norm=norm_solution, cmap=cmap)
    color_mapper_k = cm.ScalarMappable(norm=norm_k, cmap=cmap)

    fig, axs = plt.subplots(1,2, figsize=(18,8))

    # Lists to store Dirichlet vertices.
    dirichlet_xs = []
    dirichlet_ys = []

    for cell in geometry.grid.dfs(only_level=level):
        value = 0.0
        # Evaluate all basis functions at (0.5, 0.5)
        for i, vertex in enumerate(cell.vertices):
            # Ignore dirichlet boundary conditions.
            # Their value is not stored and is always zero.
            if vertex not in geometry.dirichlet_vertices:
                # Here we get the index of the data correspond to the vertex.
                #data_idx = geometry.vertex_idx_to_data_idx[vertex]
                value += sol[vertex] * fem.lagrange_2d(discretization.nodes_x, i, (0.5,0.5))
            else:
                value += dirichlet_val(cell.center,cell.size, cell.size) * fem.lagrange_2d(discretization.nodes_x, i, (0.5,0.5))

        # Plot the rectangles that build up the grid.
        rect = patches.Rectangle(
            cell.offset,
            cell.size,
            cell.size,
            fill=True,
            color=color_mapper_solution.to_rgba(value))
        axs[0].add_patch(rect)

        # Plot material
        value = discretization.eval_k(cell.center[0], cell.center[1])
        rect = patches.Rectangle(
            cell.offset,
            cell.size,
            cell.size,
            fill=True,
            color=color_mapper_k.to_rgba(value))
        axs[1].add_patch(rect)    

        # Find dirichlet vertices
        for v in cell.vertices:
            if v in geometry.dirichlet_vertices:
                dirichlet_xs.append(geometry.vertices_idx_to_coords[v][0])
                dirichlet_ys.append(geometry.vertices_idx_to_coords[v][1])

    axs[0].set_title("Solution")
    axs[0].axis('square')

    axs[1].set_title("K")
    axs[1].axis('square')

    # Mark Dirichlet vertices with black x.
    for ax in axs:
        ax.scatter(dirichlet_xs, dirichlet_ys, c='black', zorder=10, marker='x', s=50)

    fig.colorbar(color_mapper_solution, ax=axs[0])    
    fig.colorbar(color_mapper_k, ax=axs[1])
