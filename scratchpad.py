import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

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
    if det.imag != 0:
        raise Exception("Determinant is complex something is wrong!")
    return det

def main():
    random_tri = Triangulator(Octahedron())
    random_graph, random_mesh = random_tri.generate_random_triangluation(258)
    print(f"Euler character: {euler_char(random_graph, random_mesh)}")

    icosphere = Triangulator(Icosphere(depth=1))
    ico_graph, ico_mesh = icosphere.get_current_graph()
    print(f"Euler character: {euler_char(ico_graph, ico_mesh)}")

    uv_sphere = Triangulator(UVSphere(count=(5,35)))
    uv_graph, uv_mesh = uv_sphere.get_current_graph()
    uv_sphere.draw(label=f"(13, 5), N={uv_graph.number_of_nodes()}, det={det(M(nx.adjacency_matrix(uv_graph)))}")
    uv_sphere2 = Triangulator(UVSphere(count=(10,8)))
    uv_graph2, uv_mesh = uv_sphere2.get_current_graph()
    uv_sphere2.draw(label=f"(10, 8), N={uv_graph2.number_of_nodes()}, det={det(M(nx.adjacency_matrix(uv_graph2)))}")
    uv_sphere3 = Triangulator(UVSphere(count=(7,11)))
    uv_graph3, uv_mesh = uv_sphere3.get_current_graph()
    uv_sphere3.draw(label=f"(7, 11), N={uv_graph3.number_of_nodes()}, det={det(M(nx.adjacency_matrix(uv_graph3)))}")

    edge_det = []
    for i in range(1,4):
        edge_tri = Triangulator(Octahedron())
        edge_graph, edge_mesh = edge_tri.triangulate_with_recursive_method(depth=i, method="edge")
        # print(f"Euler character: {euler_char(edge_graph, edge_mesh)}")
        determinant = det(M(nx.adjacency_matrix(edge_graph)))
        edge_det.append([edge_graph.number_of_nodes(), determinant])
    edge_det = np.array(edge_det)

    ico_det = []
    for i in range(0, 3):
        icosphere = Triangulator(Icosphere(depth=i))
        ico_graph, ico_mesh = icosphere.get_current_graph()
        determinant = det(M(nx.adjacency_matrix(ico_graph)))
        ico_det.append([ico_graph.number_of_nodes(), determinant])
    ico_det = np.array(ico_det)

    uv_det = [] 
    for i in range(5,6):
        for j in range(3, 35):
            uv_sphere = Triangulator(UVSphere(count=(i,j)))
            uv_graph, uv_mesh = uv_sphere.get_current_graph()
            determinant = det(M(nx.adjacency_matrix(uv_graph)))
            uv_det.append([uv_graph.number_of_nodes(), determinant, (i, j)])
    uv_det = np.array(sorted(uv_det, key=lambda x: x[0]))
    print(uv_det)
    
    random_det = []
    for i in range(1,300):
        random_tri = Triangulator(Octahedron())
        random_graph, random_mesh = random_tri.generate_random_triangluation(i)
        determinant = det(M(nx.adjacency_matrix(random_graph)))
        random_det.append([random_graph.number_of_nodes(), determinant])
    random_det = np.array(random_det)
        
    plt.figure()
    plt.plot(edge_det[:,0], abs(edge_det[:,1]), label="Octahedron: edge")
    plt.plot(uv_det[:,0], abs(uv_det[:,1]), label="UV Sphere")
    plt.plot(random_det[:,0], abs(random_det[:,1]), label="Octahedron: random centroid")
    plt.plot(ico_det[:,0], abs(ico_det[:,1]), label="Icosphere")
    plt.legend(fontsize="small")
    plt.yscale('log')
    plt.show()


    # random_tri.draw()
    # edge_tri.draw()
    # uv_sphere.draw()
    # icosphere.draw()
    # plt.show()

if __name__ == "__main__":
    main()