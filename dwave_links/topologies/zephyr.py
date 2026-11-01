import networkx as nx
import dwave_networkx as dnx
from itertools import product
import numpy as np


class ZephyrModification:
    def __init__(self, m, t=4):
        self.g = nx.Graph()
        self.m = int(m)
        self.t = int(t)
        self.M = 2*self.m + 1
        self.max_size = 2 * 2 * self.M * self.t * self.m
        self.add_all_nodes()
        self.pos = {}
        self._compute_pos()

    def add_all_nodes(self):
        self.g.add_nodes_from(list(range(0, self.max_size)))
        self._add_zephyr_indices()

    def _add_zephyr_indices(self):
        def fill_data():
            d = get_node_data(v)
            if d is not None:
                d['zephyr_index'] = (u, w, k, j, z)
        v = 0
        get_node_data = self.g.nodes.get
        for u in range(2):
            for w in range(self.M):
                for k in range(self.t):
                    for j in (0, 1):
                        for z in range(self.m):
                            fill_data()
                            v += 1

    def _compute_pos(self):
        for node in self.g.nodes:
            u, w, k, j, z = self.read_label(node)

            W = 2 * self.t * w + 2 * k + .625 * j + .125
            Z = (2 * z + j + 1) * 2 * self.t - .5

            if u:
                xy = np.array([Z, -W])
            else:
                xy = np.array([W, -Z])

            self.pos[node] = np.hstack((xy, np.zeros(0)))


    def add_original_connections(self):
        # external edges
        self.g.add_edges_from((self.label(u, w, k, j, z), self.label(u, w, k, j, z + 1))
                         for u, w, k, j, z in product(
            (0, 1), range(self.M), range(self.t), (0, 1), range(self.m - 1)
        ))

        # odd edges
        self.g.add_edges_from((self.label(u, w, k, 0, z), self.label(u, w, k, 1, z - a))
                         for u, w, k, a in product(
            (0, 1), range(self.M), range(self.t), (0, 1)
        )
                         for z in range(a, self.m))

        # internal edges
        self.g.add_edges_from(
            (self.label(0, 2 * w + 1 + a * (2 * i - 1), k, j, z), self.label(1, 2 * z + 1 + b * (2 * j - 1), h, i, w))
            for w, z, h, k, i, j, a, b in product(
                range(self.m), range(self.m), range(self.t), range(self.t), (0, 1), (0, 1), (0, 1), (0, 1)
            ))

    def label(self, u, w, k, j, z):
        return (((u * self.M + w) * self.t + k) * 2 + j) * self.m + z

    def read_label(self, label):
        label, z = divmod(label, self.m)
        label, j = divmod(label, 2)
        label, k = divmod(label, self.t)
        u, w = divmod(label, self.M)
        return u, w, k, j, z
