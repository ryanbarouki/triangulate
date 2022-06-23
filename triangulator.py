import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from collections import namedtuple
import trimesh as tri
import random
from utils import Point, Triangle, normalize, midpoint

class Triangulator:
    def __init__(self, initial_shape) -> None:
        self.initial_faces = initial_shape.faces[:]
        self.faces = []
        self.point_from_index = initial_shape.point_from_index
        self.index_from_point = initial_shape.index_from_point
        self.methods = {"edge": self.subdivide_edge,
                       "midpoint2": self.subdivide_midpoint2,
                       "midpoint": self.subdivide_midpoint,
                       "centroid": self.subdivide_centroid,
                       "hybrid": self.subdivide_hybrid,
                       "hybrid2": self.subdivide_hybrid2,
                       "hybrid3": self.subdivide_hybrid3,
                       }
        self.graph = None

    def triangulate_with_recursive_method(self, depth, method):
        for i, face in enumerate(self.subdivide(depth, self.methods[method])):
            self.faces.append(face)
        return self.get_current_graph()
    
    def generate_random_triangluation(self, N):
        self.faces.extend(self.initial_faces[:])
        for i in range(N - len(self.point_from_index)):
            random_face_id = random.randint(0, len(self.faces)-1)
            random_face = self.faces.pop(random_face_id)
            for j, new_faces in enumerate(self.subdivide_centroid(random_face, 1)):
                self.faces.append(new_faces)
        return self.get_current_graph()

    def get_current_graph(self):
        faces = self.faces
        if self.faces == []:
            faces = self.initial_faces
        mesh = tri.Trimesh(faces=faces)
        graph = nx.Graph()
        graph.add_edges_from(mesh.edges)
        return graph, mesh
    
    def draw(self):
        X = []
        Y = []
        Z = []
        T = []
        faces = self.faces
        if self.faces == []:
            faces = self.initial_faces
        for i in range(len(faces)):
            face = faces[i]
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

    def subdivide_midpoint(self, tri, depth):
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
        yield from self.subdivide_midpoint2(Triangle(i12, i0, i1), depth-1)
        yield from self.subdivide_midpoint2(Triangle(i12, i2, i0), depth-1)

    def subdivide_centroid(self, tri, depth):
        if depth == 0:
            yield tri
            return
        #       p0
        #       /|\
        #      / | \
        #     /  c  \
        #    /_______\
        #  p1         p2
        i0, i1, i2 = tri
        p0 = self.point_from_index[i0]
        p1 = self.point_from_index[i1]
        p2 = self.point_from_index[i2]
        centroid = normalize(Point(
            (p0.x + p1.x + p2.x) / 3,
            (p0.y + p1.y + p2.y) / 3,
            (p0.z + p1.z + p2.z) / 3,
        ))
        ic = self.get_index_from_point(centroid)
        t1 = Triangle(i0, i1, ic)
        t2 = Triangle(i2, ic, i0)
        t3 = Triangle(ic, i1, i2)

        yield from self.subdivide_centroid(t1, depth - 1)
        yield from self.subdivide_centroid(t2, depth - 1)
        yield from self.subdivide_centroid(t3, depth - 1)

    def subdivide_hybrid3(self, tri, depth):
        def triangle(tri, depth):
            if depth == 0:
                yield tri
                return
            for t in self.subdivide_centroid(tri, 1):
                yield from edge(t, depth - 1)

        def centroid(tri, depth):
            if depth == 0:
                yield tri
                return
            for t in self.subdivide_midpoint(tri, 2):
                yield from triangle(t, depth - 1)

        def edge(tri, depth):
            if depth == 0:
                yield tri
                return
            for t in self.subdivide_edge(tri, 1):
                yield from centroid(t, depth - 1)

        return centroid(tri, depth)


    def subdivide_hybrid2(self, tri, depth):
        def centroid(tri, depth):
            if depth == 0:
                yield tri
                return
            for t in self.subdivide_centroid(tri, 1):
                yield from edge(t, depth - 1)

        def edge(tri, depth):
            if depth == 0:
                yield tri
                return
            for t in self.subdivide_edge(tri, 1):
                yield from centroid(t, depth - 1)

        return centroid(tri, depth)


    def subdivide_hybrid(self, tri, depth):
        def centroid(tri, depth):
            if depth == 0:
                yield tri
                return
            for t in self.subdivide_centroid(tri, 1):
                yield from edge(t, depth - 1)

        def edge(tri, depth):
            if depth == 0:
                yield tri
                return
            for t in self.subdivide_edge(tri, 1):
                yield from centroid(t, depth - 1)

        return edge(tri, depth)
