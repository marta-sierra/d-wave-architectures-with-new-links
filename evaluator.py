import generate_regular_ldpc_codes
from minorminerEmbedder import MinorminerEmbedder
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


class Evaluator:
    def __init__(self, u, pos={}):
        self.u = u
        self.pos = pos

    def eval_lengths(self, n, iterations=20, attempts=20):
        not_embedded = 0
        lengths_matrix = list()
        while len(lengths_matrix) < iterations:
            g = generate_regular_ldpc_codes.generate_2_3_regular_ldpc_code(n)
            minor = MinorminerEmbedder(g, self.u)
            lengths = minor.best_chain_lengths(attempts=attempts)
            if lengths is None:
                not_embedded += 1
                if not_embedded >= 5:
                    return None
            else:
                lengths_matrix.append(list(map(int, list(lengths))))
        return lengths_matrix

    def nice_results_eval_lengths(self, n, iterations=20, attempts=20):
        results = self.eval_lengths(n, iterations, attempts)
        if results is None:
            return None
        means, maxes = list(), list()
        for row in results:
            means.append(np.mean(np.array(row)))
            maxes.append(np.max(np.array(row)))

        return {'mean': np.mean(np.array(means)), 'max': np.mean(np.array(maxes))}

    def draw_embedding(self, n, attempts=5):
        g = generate_regular_ldpc_codes.generate_2_3_regular_ldpc_code(n)
        minor = MinorminerEmbedder(g, self.u)
        minor.best_chain_lengths(attempts=attempts)
        nx.draw(self.u, self.pos, node_color='lightgray', node_size=50, edge_color='gray', alpha=0.5)

        def draw_embedding(G, embedding, **kwargs):
            for logical_node, chain in embedding.items():
                chain_color = 'red' if isinstance(logical_node, str) else 'blue'
                nx.draw(G.subgraph(chain), self.pos, node_color=chain_color, **kwargs)
            nx.draw_networkx_labels(G, self.pos)
        draw_embedding(self.u, minor.embedding, node_size=100)
        plt.show()





