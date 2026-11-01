from pyldpc import make_ldpc
import networkx as nx
import numpy as np
import random


def generate_2_3_regular_ldpc_code(n, d_v=2, d_c=3):
    H_pcm, G = make_ldpc(n_code=n, d_v=d_v, d_c=d_c, systematic=True, seed=random.randint(0, 5000))
    nodes_in_H_pcm = set()
    edges_in_H_pcm = list()

    qe_idx = 0
    for idx, constraint in enumerate(H_pcm):
        nodes_in_constraint = np.where(constraint > 0)[0]
        num_anc_variables   = np.log2(int(len(nodes_in_constraint) / 2)) + 1
        
        qe_ = []
        for i in np.arange(num_anc_variables):
            qe_.append(f'qe{qe_idx}')
            qe_idx += 1

        nodes_in_constraint = [*nodes_in_constraint, *qe_]
        nodes_in_H_pcm = nodes_in_H_pcm | set(nodes_in_constraint)
        edges_in_constraint = []
        for i in range(len(nodes_in_constraint)):
            for j in range(i+1, len(nodes_in_constraint)):
                nodes_in_edge = [nodes_in_constraint[i], nodes_in_constraint[j]]
                if type(nodes_in_edge[1]) is str: ## ancillary variable
                    _min = nodes_in_edge[0]
                    _max = nodes_in_edge[1]
                else:
                    _min, _max = min(nodes_in_edge), max(nodes_in_edge)
                edges_in_constraint.append((_min, _max))
        edges_in_H_pcm.extend(edges_in_constraint)

    graph = nx.Graph()
    graph.add_nodes_from(nodes_in_H_pcm)
    graph.add_edges_from(edges_in_H_pcm)

    return graph



