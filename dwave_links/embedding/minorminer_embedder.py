from minorminer import find_embedding
import numpy as np
import random


class MinorminerEmbedder:
    def __init__(self, g, u):
        self.__g = g
        self.__u = u
        self.embedding = self.embed()

    def embed(self, seed=random.randint(0, 5000)):
        self.embedding = find_embedding(self.__g.edges, self.__u.edges, random_seed=seed)
        return self.embedding

    def try_to_embed(self, seed=random.randint(0, 5000)):
        return find_embedding(self.__g.edges, self.__u.edges, random_seed=seed)

    def all_nodes_embedded(self, embedding=None):
        if embedding is None:
            embedding = self.embedding
        return len(embedding) == len(self.__g.nodes)

    def _embedding_chain_lengths(self, embedding=None):
        if embedding is None:
            embedding = self.embedding
        if not self.all_nodes_embedded():
            return None
        lengths = np.empty(len(embedding))
        for i in range(len(embedding)):
            lengths[i] = len(list(embedding.values())[i])
        return lengths

    def _embedding_chain_length_evaluation(self, embedding):
        if embedding is None:
            embedding = self.embedding
        lengths = self._embedding_chain_lengths(embedding)
        if lengths is None:
            return None, None, None
        return np.max(lengths), np.min(lengths), np.mean(lengths)

    def max_chain_length(self, embedding):
        if embedding is None:
            embedding = self.embedding
        return self._embedding_chain_length_evaluation(embedding)[0]

    def min_chain_length(self, embedding):
        if embedding is None:
            embedding = self.embedding
        return self._embedding_chain_length_evaluation(embedding)[1]

    def mean_chain_length(self, embedding):
        if embedding is None:
            embedding = self.embedding
        return self._embedding_chain_length_evaluation(embedding)[2]

    def best_chain_lengths(self, attempts=20, min_enough=1):
        lengths = np.empty(len(list(self.__g.nodes)))
        self.embed()
        minmax = self.max_chain_length(self.embedding)
        lengths = self._embedding_chain_lengths()
        for _ in range(attempts-1):
            if minmax is not None and minmax == min_enough:
                break
            tried_embedding = self.try_to_embed()
            x = self.max_chain_length(tried_embedding)
            if minmax is None or (x is not None and x < minmax):
                minmax = x
                self.embedding = tried_embedding
                lengths = self._embedding_chain_lengths()
        return lengths