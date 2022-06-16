from utils import Point, Triangle, normalize

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
            
        self.point_from_index = {
            0: Point(0, 1, 0),
            1: Point(-p, 0, p),
            2: Point(p, 0, p),
            3: Point(p, 0, -p),
            4: Point(-p, 0, -p),
            5: Point(0, -1, 0)
        }

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
            
        self.point_from_index = {
            0: normalize(Point(1, 0, -p)),
            1: normalize(Point(-1, 0, -p)),
            2: normalize(Point(0, 1, p)),
            3: normalize(Point(0, -1, p))
        }

        self.faces = [
            Triangle(0, 1, 2),
            Triangle(0, 2, 3),
            Triangle(0, 3, 1),
            Triangle(1, 3, 2),
        ]