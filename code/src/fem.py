import numpy as np
import scipy.special as special
import scipy.sparse as sp
import scipy.sparse.linalg as splinalg

# Some numerics stolen from:
# https://www.sciencedirect.com/science/article/pii/S0010465519303364


# Discretization, polynomials
# Use tensor product nodal basis with x = [-1,1], y = [-1, 1]
# reference quad is also in [-1,1]^2
def map_to_reference_coordinates(cell, coordinate_global):
    return 2.0 / cell.size * (coordinate_global - cell.center)

def map_to_global_coordinates(cell, coordinate_reference):
    return cell.center + 0.5 * coordinate_reference * cell.size

def area(cell):
    return cell.size * cell.size

def lagrange(points, i, x):
    node = points[i]
    value = 1.0
    for (j, point) in enumerate(points):
        if i != j:
            value *= (x - point) / (node - point)
    return value

def lagrange_diff(points, i, x):
    result = 0.0
    for j in range(len(points)):
        acc = 1.0
        if i == j:
            continue
        frac = 1.0 / (points[i] - points[j])
        for m in range(len(points)):
            if m == i or m == j:
                continue
            acc *= (x - points[m])/(points[i] - points[m])
        result += frac * acc
    return result

def lin2cart(linear_index):
    i = linear_index // 2
    j = linear_index % 2
    return i,j

def lagrange_2d(points, linear_index, x):
    i, j = lin2cart(linear_index)
    return lagrange(points, i, x[0]) * lagrange(points, j, x[1])

def lagrange_2d_diffx(points, linear_index, x):
    i, j = lin2cart(linear_index)
    return lagrange_diff(points, i, x[0]) * lagrange(points, j, x[1])

def lagrange_2d_diffy(points, linear_index, x):
    i, j = lin2cart(linear_index)
    return lagrange(points, i, x[0]) * lagrange_diff(points, j, x[1])    


class Discretization:
    def __init__(self, geometry, level, eval_k=None):
        # Standard linear tensor-prod. basis
        self.nodes_x = np.array([-1, 1])

        # Gauss-Legendre quadrature
        self.quad_x, self.quad_w = special.roots_legendre(n=2)
        
        # Ref cell is [-1,1]^2
        self.area_reference_cell = 4
    
        self.geometry = geometry
        self.level = level
        
        self.number_of_vertices = geometry.number_of_vertices_per_level[level]
        self.number_of_data = geometry.data_size_per_level[level]
        self.cur_dirichlet_vertices = set([v for v in geometry.dirichlet_vertices if v < self.number_of_vertices])

        self.eval_k = eval_k

    def setup_stiffness(self):
        # TODO: Move those to a class
        stiffness = sp.lil_matrix((self.number_of_data, self.number_of_data), dtype=np.float64)
        for cell in self.geometry.grid.dfs(only_level=self.level):
            for lin_0, vertex_0 in enumerate(cell.vertices):
                for lin_1, vertex_1 in enumerate(cell.vertices):
                    data_0 = self.geometry.vertex_idx_to_data_idx[vertex_0]
                    data_1 = self.geometry.vertex_idx_to_data_idx[vertex_1]
                    if vertex_0 in self.geometry.dirichlet_vertices:
                        #stiffness[vertex_0, :] = 0
                        #stiffness[vertex_0, vertex_0] = 1
                        continue
                    if vertex_1 in self.geometry.dirichlet_vertices:
                        # Dirichlet vertex has zero contribution
                        continue
                    for lin_quad in range(4):
                        quad_i, quad_j = lin2cart(lin_quad)
                        x, y = self.quad_x[quad_i], self.quad_x[quad_j]
                        quad_coords = np.array([x, y])
                        quad_weight = self.quad_w[quad_i] * self.quad_w[quad_j]
                        diff_x = lagrange_2d_diffx(self.nodes_x, lin_0, quad_coords) * \
                            lagrange_2d_diffx(self.nodes_x, lin_1, quad_coords)
                        diff_y = lagrange_2d_diffy(self.nodes_x, lin_0, quad_coords) * \
                            lagrange_2d_diffy(self.nodes_x, lin_1, quad_coords)
                        K = self.eval_k(cell.center[0], cell.center[1])

                        # TODO Check area factor
                        factor = area(cell) / self.area_reference_cell / cell.size * quad_weight * K
                        stiffness[data_0, data_1] += factor * (diff_x + diff_y)

        return stiffness.tocsc()
    
    def setup_rhs(self):
        rhs = np.zeros(self.number_of_data)
        for cell in self.geometry.grid.dfs(self.level):
            for lin, vertex in enumerate(cell.vertices):
                if vertex in self.cur_dirichlet_vertices:
                    # Dirichlet vertices not contained in rhs
                    continue
                data_idx = self.geometry.vertex_idx_to_data_idx[vertex]
                for lin_quad in range(4):
                    quad_i, quad_j = lin2cart(lin_quad)
                    x, y = self.quad_x[quad_i], self.quad_x[quad_j]
                    quad_coords = np.array([x, y])
                    quad_weight = self.quad_w[quad_i] * self.quad_w[quad_j]
                    factor = area(cell) * quad_weight
                    rhs[data_idx] += factor * lagrange_2d(self.nodes_x, lin, quad_coords)

        return rhs
