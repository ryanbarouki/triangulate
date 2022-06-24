from triangulator import Triangulator
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import scipy.sparse as scsp
import scipy.linalg as sclin
import trimesh as tri

from shapes import Icosphere, Octahedron, Tetrahedron, UVSphere

def euler_char(graph, mesh):
    V = graph.number_of_nodes()
    E = graph.number_of_edges()
    F = len(mesh.faces)
    print(f"V:{V}, E:{E}, F:{F}")
    return V - E + F

def M(adj):
    # adj is assumed to be a scipy sparse matrix
    q = np.array(adj.sum(axis=0))[0]
    mat = scsp.diags(q)
    return mat - adj

def M_dense(adj):
    # for normal matrices
    q = lambda i: sum(adj[i,])
    mat = np.diag([q(i) for i in range(len(adj))])
    return mat - adj

def det(mat):
    eigvals, eigvecs = sclin.eig(mat.toarray())
    det = 1
    zero = False
    for eig in eigvals:
        # we want to remove the one zero mode
        if abs(eig) == 0 and not zero:
            zero = True
            continue
        det *= eig
    return det

random_tri = Triangulator(Octahedron())
random_graph, random_mesh = random_tri.generate_random_triangluation(258)
print(f"Euler character: {euler_char(random_graph, random_mesh)}")
random_tri.draw()

edge_tri = Triangulator(Octahedron())
edge_graph, edge_mesh = edge_tri.triangulate_with_recursive_method(depth=3, method="edge")
print(f"Euler character: {euler_char(edge_graph, edge_mesh)}")
edge_tri.draw()

uv_sphere = Triangulator(UVSphere(count=(10,17)))
uv_graph, uv_mesh = uv_sphere.get_current_graph()
print(f"Euler character: {euler_char(uv_graph, uv_mesh)}")
uv_sphere.draw()

icosphere = Triangulator(Icosphere(depth=1))
ico_graph, ico_mesh = icosphere.get_current_graph()
print(f"Euler character: {euler_char(ico_graph, ico_mesh)}")
icosphere.draw()

print(f"Det random sphere:{det(M(nx.adjacency_matrix(random_graph)))}")
print(f"Det edge sphere:{det(M(nx.adjacency_matrix(edge_graph)))}")
print(f"Det UV sphere:{det(M(nx.adjacency_matrix(uv_graph)))}")

# Stragegy: 
# Make graphs of det vs N for all three types on triangulation and try to compare 
plt.show()