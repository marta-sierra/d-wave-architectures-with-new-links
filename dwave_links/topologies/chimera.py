import networkx as nx
import dwave_networkx as dnx
from itertools import product


class ChimeraModification:
    def __init__(self, m, n=None, t=4):
        self.g = nx.Graph()
        self.m = int(m)
        if n is None: self.n = m
        else: self.n = int(n)
        self.t = int(t)
        self.max_size = self.m * self.n * 2 * self.t
        self.add_all_nodes()
        self.pos = dnx.chimera_layout(self.g)
        self.add_bipartite_connections()

    def add_all_nodes(self):
        self.g.add_nodes_from(list(range(0, self.max_size)))
        self._add_chimera_indices()

    def _add_chimera_indices(self):
        def checkadd(v, q):
            if v in self.g:
                self.g.nodes[v]['chimera_index'] = q
        v = 0
        for i in range(self.m):
            for j in range(self.n):
                for u in range(2):
                    for k in range(self.t):
                        checkadd(v, (i, j, u, k))
                        v += 1

    def add_original_hor_ver_connections(self):
        hoff = 2 * self.t
        voff = self.n * hoff
        mi = self.m * voff
        ni = self.n * hoff

        # horizontal edges
        self.g.add_edges_from((k, k + hoff)
                         for i in range(self.t, 2 * self.t)
                         for j in range(i, ni - hoff, hoff)
                         for k in range(j, mi, voff))
        # vertical edges
        self.g.add_edges_from((k, k + voff)
                         for i in range(self.t)
                         for j in range(i, ni, hoff)
                         for k in range(j, mi - voff, voff))

    def add_bipartite_connections(self):
        hoff = 2 * self.t
        voff = self.n * hoff
        mi = self.m * voff
        ni = self.n * hoff

        # bipartite connections
        self.g.add_edges_from((k0, k1)
                         for i in range(0, ni, hoff)
                         for j in range(i, mi, voff)
                         for k0 in range(j, j + self.t)
                         for k1 in range(j + self.t, j + 2 * self.t))

    def add_horizontal_connections(self, order, all=True, even=True):
        hoff = 2 * self.t
        voff = self.n * 2 * self.t
        mi = self.m * voff
        ni = self.n * hoff
        for i in range(self.t, 2 * self.t):
            for j in range(i, ni - hoff, hoff):
                for k in range(j, mi, voff):
                    k2 = k + hoff + 2*self.t*(order-1)
                    if {k, k2}.issubset(set(self.g.nodes)) and k//(2*self.n*self.t) == k2//(2*self.n*self.t):
                        if all:
                            self.g.add_edge(k, k2)
                        elif even and k % 2 == 0:
                            self.g.add_edge(k, k2)
                        elif not even and k % 2 == 1:
                            self.g.add_edge(k, k2)

    def add_vertical_connections(self, order, all=True, even=True):
        hoff = 2 * self.t
        voff = self.n * 2 * self.t
        mi = self.m * voff
        ni = self.n * hoff
        for i in range(self.t):
            for j in range(i, ni, hoff):
                for k in range(j, mi - voff, voff):
                    k2 = k + voff + 2*self.t*self.n*(order-1)
                    if {k, k2}.issubset(set(self.g.nodes)):
                        if all:
                            self.g.add_edge(k, k2)
                        elif even and k % 2 == 0:
                            self.g.add_edge(k, k2)
                        elif not even and k % 2 == 1:
                            self.g.add_edge(k, k2)

    def add_hor_ver_connections(self, order, all=True, even=True):
        self.add_vertical_connections(order, all, even)
        self.add_horizontal_connections(order,all, even)

    def copy(self):
        c = ChimeraModification(self.m, self.n, self.t)
        c.g = self.g.copy()
        return c



