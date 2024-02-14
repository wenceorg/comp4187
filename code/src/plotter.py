import matplotlib.pyplot as plt
import matplotlib.patches as patches
def plot_grid(fig, ax, grid, vertices=None, level=None, c='black', plot_center=False, plot_curve=False, plot_vertices=False):
    xs = []
    ys = []
    vertices_xs = []
    vertices_ys = []
    for cell in grid.dfs(only_level=level):
        xs.append(cell.center[0])
        ys.append(cell.center[1])
        if plot_center:
            ax.scatter(cell.center[0], cell.center[1], c=c)
        rect = patches.Rectangle(
            cell.offset,
            cell.size,
            cell.size,
            fill=False)
        ax.add_patch(rect)
        if plot_vertices:
            for vertex_idx in cell.vertices:
                vertex_coords = vertices[vertex_idx]
                vertices_xs.append(vertex_coords[0])
                vertices_ys.append(vertex_coords[1])
    if plot_curve:
        ax.plot(xs, ys, c=c)
    if plot_vertices:
        ax.scatter(vertices_xs, vertices_ys, c='red', marker='x', s=100)
    
