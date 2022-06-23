from utils import Point, Triangle, normalize
import trimesh as tri

p = 2**0.5 / 2

class Octahedron:
    def __init__(self) -> None:
        self.index_from_point = {
            Point(0, 1, 0): 0,
            Point(-p, 0, p): 1,
            Point(p, 0, p): 2,
            Point(p, 0, -p): 3,
            Point(-p, 0, -p): 4,
            Point(0, -1, 0): 5
        }

        self.point_from_index = {v: k for k, v in self.index_from_point.items()}

        self.faces = [
            # top half
            Triangle(0, 1, 2),
            Triangle(0, 2, 3),
            Triangle(0, 3, 4),
            Triangle(0, 4, 1),

            # bottom half
            Triangle(5, 2, 1),
            Triangle(5, 3, 2),
            Triangle(5, 4, 3),
            Triangle(5, 1, 4),
        ]

class Tetrahedron:
    def __init__(self) -> None:
        self.index_from_point = {
            normalize(Point(1, 0, -p)): 0,
            normalize(Point(-1, 0, -p)): 1,
            normalize(Point(0, 1, p)): 2,
            normalize(Point(0, -1, p)): 3
        }
            
        self.point_from_index = {v: k for k, v in self.index_from_point.items()}

        self.faces = [
            Triangle(0, 1, 2),
            Triangle(0, 2, 3),
            Triangle(0, 3, 1),
            Triangle(1, 3, 2),
        ]

class UVSphere:
    def __init__(self, count=(32,32)) -> None:
        uv_mesh = tri.creation.uv_sphere(count=count)
        self.faces = [Triangle(*face) for face in uv_mesh.faces]
        self.point_from_index = {i: Point(*uv_mesh.vertices[i]) for i in range(len(uv_mesh.vertices)) if uv_mesh.referenced_vertices[i]}
        self.index_from_point = {Point(*uv_mesh.vertices[i]):i for i in range(len(uv_mesh.vertices)) if uv_mesh.referenced_vertices[i]}
