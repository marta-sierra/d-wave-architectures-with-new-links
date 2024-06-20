import networkx as nx
import dwave_networkx as dnx
import numpy as np


class PegasusModification:
    def __init__(self, m):
        self.g = nx.Graph()
        self.m = int(m)
        self.max_size = self.m * (self.m - 1) * 24
        self.add_all_nodes()
        self.pos = {}
        self._compute_pos()

    def add_all_nodes(self):
        self.g.add_nodes_from(list(range(0, self.max_size)))
        self._add_pegasus_indices()

    def _compute_pos(self):
        h_offsets = (6, 6, 6, 6, 2, 2, 2, 2, 10, 10, 10, 10,)
        v_offsets = (2, 2, 2, 2, 10, 10, 10, 10, 6, 6, 6, 6,)
        for node in self.g.nodes:
            u, w, k, z = self.read_label(node)
            if k % 2:
                p = -.1
            else:
                p = .1
            if u:
                xy = np.array([z * 12 + h_offsets[k] + 5.5, -12 * w - k - p ])
            else:
                xy = np.array([12 * w + k + p , -z * 12 - v_offsets[k] - 5.5])
                # convention for Pegasus-lattice pictures is to invert the y-axis
            self.pos[node] = np.hstack((xy, np.zeros(0)))

    def _add_pegasus_indices(self):
        v = 0
        def fill_data():
            d = get_node_data(v)
            if d is not None:
                d['pegasus_index'] = (u, w, k, z)
        get_node_data = self.g.nodes.get
        for u in range(2):
            for w in range(self.m):
                for k in range(12):
                    for z in range(self.m - 1):
                        fill_data()
                        v += 1

    def label(self, u, w, k, z):
            return u * 12 * self.m * (self.m - 1) + w * 12 * (self.m - 1) + k * (self.m - 1) + z

    def read_label(self, label):
        label, z = divmod(label, self.m-1)
        label, k = divmod(label, 12)
        u, w = divmod(label, self.m)
        return u, w, k, z

    def add_original_connections(self):
        offset_lists = [(2, 2, 2, 2, 10, 10, 10, 10, 6, 6, 6, 6,), (6, 6, 6, 6, 2, 2, 2, 2, 10, 10, 10, 10,)]
        fabric_start = min(s for s in offset_lists[1]), min(s for s in offset_lists[0])
        fabric_end = 12 - max(s for s in offset_lists[1]), 12 - max(s for s in offset_lists[0])
        self.g.add_edges_from((self.label(u, w, k, z), self.label(u, w, k, z + 1))
                         for u in (0, 1)
                         for w in range(self.m)
                         for k in range(fabric_start[u] if w == 0 else 0, 12 - (fabric_end[u] if w == (self.m - 1) else 0))
                         for z in range(self.m - 2))

        self.g.add_edges_from((self.label(u, w, k, z), self.label(u, w, k + 1, z))
                         for u in (0, 1)
                         for w in range(self.m)
                         for k in range(fabric_start[u] if w == 0 else 0, 12 - (fabric_end[u] if w == (self.m - 1) else 0), 2)
                         for z in range(self.m - 1))

        off0, off1 = offset_lists

        def qfilter(u, w, k, z):
            if w == 0: return k >= fabric_start[u]
            if w == (self.m - 1): return k < 12 - fabric_end[u]
            return True

        def efilter(e):
            return qfilter(*e[0]) and qfilter(*e[1])

        internal_couplers = (((0, w, k, z), (1, z + (kk < off0[k]), kk, w - (k < off1[kk])))
                             for w in range(self.m)
                             for kk in range(12)
                             for k in range(0 if w else off1[kk], 12 if w < (self.m - 1) else off1[kk])
                             for z in range(self.m - 1))
        self.g.add_edges_from((self.label(*e[0]), self.label(*e[1])) for e in internal_couplers if efilter(e))

