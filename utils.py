from collections import namedtuple

Triangle = namedtuple("Triangle", "a,b,c")
Point = namedtuple("Point", "x,y,z")

def normalize(p):
    s = sum(u*u for u in p) ** 0.5
    return Point(*(u/s for u in p))

def midpoint(u, v):
    return Point(*((a+b)/2 for a, b in zip(u, v)))
