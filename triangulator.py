import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from collections import namedtuple
import trimesh as tri
from utils import Point, Triangle, normalize, midpoint

class Triangulator:
    def __init__(self, initial_shape, depth, method) -> None:
        self.initial_faces = initial_shape.faces
        self.point_from_index = initial_shape.point_from_index
        self.index_from_point = initial_shape.index_from_point
        self.depth = depth
        self.method = {"edge": self.subdivide_edge,
                       "midpoint2": self.subdivide_midpoint2}[method]
        self.graph = None
    
    def get_graph(self):
        new_faces = []
        for i, face in enumerate(self.subdivide(self.depth, self.method)):
            new_faces.append(face)
        mesh = tri.Trimesh(faces=new_faces)
        graph = nx.Graph()
        graph.add_edges_from(mesh.edges)
        return graph
    
    def draw(self):
        X = []
        Y = []
        Z = []
        T = []
        for i, face in enumerate(self.subdivide(self.depth, self.method)):
            X.extend([self.point_from_index[p].x for p in face])
            Y.extend([self.point_from_index[p].y for p in face])
            Z.extend([self.point_from_index[p].z for p in face])
            T.append([3*i, 3*i+1, 3*i+2])

        X = np.array(X)
        Y = np.array(Y)
        Z = np.array(Z)
        T = mtri.Triangulation(X, Y, np.array(T))
        fig = plt.figure()
        ax  = fig.add_subplot(111, projection='3d')
        ax.plot_trisurf(T, Z, lw=0.2, edgecolor="black", color="grey", alpha=1, cmap='YlGnBu_r')
        plt.axis('off')
        plt.show()
        

    def get_index_from_point(self, point):
        if point in self.index_from_point:
            return self.index_from_point[point]
        # we need to make a new index and add to dictionaries
        new_idx = max(self.point_from_index.keys()) + 1
        self.point_from_index[new_idx] = point
        self.index_from_point[point] = new_idx
        return new_idx

    def subdivide(self, depth, method):
        for tri in self.initial_faces:
            yield from method(tri, depth)

    def subdivide_edge(self, tri, depth):
        if depth == 0:
            yield tri
            return
        #       p0
        #      /  \
        # m01 /....\ m02
        #    / \  / \
        #   /___\/___\
        # p1    m12   p2
        i1, i2, i3 = tri
        m01 = normalize(midpoint(self.point_from_index[i1], self.point_from_index[i2]))
        m02 = normalize(midpoint(self.point_from_index[i1], self.point_from_index[i3]))
        m12 = normalize(midpoint(self.point_from_index[i2], self.point_from_index[i3]))

        i01 = self.get_index_from_point(m01)
        i02 = self.get_index_from_point(m02)
        i12 = self.get_index_from_point(m12)

        triangles = [
            Triangle(i1,  i01, i02),
            Triangle(i01, i2,  i12),
            Triangle(i02, i12, i3),
            Triangle(i01, i02, i12),
        ]
        for t in triangles:
            yield from self.subdivide_edge(t, depth-1)

    def subdivide_midpoint2(self, tri, depth):
        if depth == 0:
            yield tri
            return
        #       p0
        #      /|\
        #     / | \
        #    /  |  \
        #   /___|___\
        # p1   m12   p2
        i0, i1, i2 = tri
        m12 = normalize(midpoint(self.point_from_index[i1], self.point_from_index[i2]))
        i12 = self.get_index_from_point(m12)
        # WRONG TRIANGULATION!
        yield from self.subdivide_midpoint2(Triangle(i0, i12, i1), depth-1)
        yield from self.subdivide_midpoint2(Triangle(i0, i2, i12), depth-1)