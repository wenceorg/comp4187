import numpy as np
from collections import defaultdict


class Quadtree:
    def __init__(self,center, size, level=0, parent=None):
        self.center = center
        self.size = size
        self.offset = center - 0.5 * size
        self.children = [
            None, None, None, None
        ]
        self.is_leaf = True
        self.level = level
        self.parent = parent
        self.vertices = [None, None, None, None]
        self.index = -1 # index if level treated as max level
        
    def split(self):
        max_level = self.level
        new_size = self.size / 2
        offsets = [
            np.array([0.25 * self.size,
                      0.75 * self.size]),
            np.array([0.75 * self.size,
                      0.75 * self.size]),
            np.array([0.25 * self.size,
                      0.25 * self.size]),
            np.array([0.75 * self.size,
                      0.25 * self.size])
        ]
        
        for i, offset in enumerate(offsets):
            if self.is_leaf:
                new_level = self.level + 1
                new_center = self.offset + offset
                self.children[i] = Quadtree(
                    center = new_center,
                    size = new_size,
                    level = new_level,
                    parent=self)
            else:
                new_level = self.children[i].split()
            max_level = max(max_level, new_level)
            
        self.is_leaf = False
        
        return max_level
    
    def get_max_level(self):
        return max(c.level for c in self.dfs())
    
    def split_to_level(self, level):
        max_level = self.get_max_level()
        while (max_level < level):
            max_level = self.split()
        return max_level
        
    def dfs(self, only_level=None):
        for child in self.children:
            if child is not None:
                yield from child.dfs(only_level=only_level)
        if only_level is None or self.level == only_level:
            yield self
            
    def find_root(self):
        ptr = self
        while ptr.parent is not None:
            ptr = ptr.parent
        return ptr
    
    def is_inside(self, point, eps=1e-6):
        #print("Searching for {}".format(point))
        if self.is_leaf:
            print("In leaf")
        left = self.offset[0]
        right = self.offset[0] + size
        top = self.offset[1] + size
        bottom = self.offset[1]
        #print("left = {}, right = {}, top = {}, bottom {}".format(
        #left, right,top,bottom))
        #print()
        return (
            (left - point[0]) <= eps and
            (right - point[0]) >= eps and
            (bottom - point[1]) <= eps and
            (top - point[1]) >= eps
        )
            
    
    def find_cell(self, point, eps, originator=None):
        if originator is None:
            originator = self
            ptr = self.find_root()
            # Handle case of level 0
            if ptr.is_leaf:
                return None
        else:
            ptr = self
            
        print(self.center)
        if self.is_leaf:
            assert(self.is_inside(point, eps=eps))
            assert(self is not originator)
            return self
        
        for child in ptr.children:
            if child is None:
                continue
            elif child is not originator and child.is_inside(point):
                result_child = child.find_cell(point, eps, originator)
                if result_child is not None:
                    return result_child
        return None
            
        
    def get_cell_vertices(self, rounded_decimals=6):
        # TODO Fix order of vertices
        factors = [-1, 1]
        for f1 in factors:
            for f2 in factors:
                # 0 0 -1.0 -1.0
                # 0 1 -1.0 1.0
                # 1 0 1.0 -1.0
                # 1 1 1.0 1.0
                yield tuple(
                    np.round(
                        np.array([self.center[0]+f1 * self.size / 2,
                                  self.center[1] + f2 * self.size / 2]), decimals=rounded_decimals))

    def get_vertices(self,):           
        cur_idx = 0
        max_level = self.get_max_level()
        vertices = dict() # coord -> idx
        count_before = 0
        number_of_vertices_per_level = []
        boundary_vertices = set()
        for level in range(max_level+1):
            vertices_count = defaultdict(int) # idx -> how many cells this vertex is member of
            count_before = len(vertices)
            for cell in self.dfs(only_level=level):
                cell.vertices = []
                for vertex_coord in cell.get_cell_vertices(rounded_decimals=max_level+1): # TODO fix rounding
                    if not vertex_coord in vertices:
                        vertex_idx = cur_idx
                        vertices[vertex_coord] = vertex_idx
                        cur_idx += 1
                    else:
                        vertex_idx = vertices[vertex_coord]

                    cell.vertices.append(vertex_idx)
                    vertices_count[vertex_idx] += 1
            number_of_vertices_per_level.append(len(vertices))
            #print("Level {} has \t{} vertices".format(level, len(vertices) - count_before))
                
            boundary_vertices |= set([i for (i,j) in vertices_count.items() if j < 4])
            #print(vertices_count)
        return vertices, np.array(number_of_vertices_per_level), boundary_vertices
    
    def set_all_cell_vertices(self, vertices_map):
        max_level = self.get_max_level()
        for cell in self.dfs():
            for i, vertex_coord in enumerate(cell.get_cell_vertices(rounded_decimals=max_level+1)): # TODO fix rounding
                    assert(vertex_coord in vertices_map)
                    cell.vertices[i] = vertices_map[vertex_coord]
                    
    def set_all_cell_indices(self):
        # for each level
        max_level = self.get_max_level()
        for level in range(max_level+1):
            for i, cell in enumerate(self.dfs(only_level=level)):
                    cell.index = i

                    
def get_number_of_cells(level):
    return 4**level


    
