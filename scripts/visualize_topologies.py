import networkx as nx
import matplotlib.pyplot as plt
from dwave_links.topologies.chimera import ChimeraModification
from dwave_links.topologies.pegasus import PegasusModification
from dwave_links.topologies.zephyr import ZephyrModification

# CHIMERA LAYOUT VISUALIZATION
c = ChimeraModification(6)
#c.add_original_connections()
#nx.draw(c.g, pos = c.pos, node_size = 20)
#plt.show()

c.add_vertical_connections(1, all=False)
#c.add_horizontal_connections(1, all=True)
c.add_bipartite_connections()
nx.draw(c.g, pos = c.pos, node_size = 20, with_labels=True)
plt.show()

# PEGASUS LAYOUT VISUALIZATION
"""p = PegasusModification(6)
nx.draw(p.g, pos = p.pos, node_size = 40)
plt.show()

p.add_original_connections()
nx.draw(p.g, pos = p.pos, node_size = 40)
plt.show()"""

# ZEPHYR LAYOUT VISUALIZATION
"""z = ZephyrModification(6)
nx.draw(z.g, pos = z.pos, node_size = 40)
plt.show()

z.add_original_connections()
nx.draw(z.g, pos = z.pos, node_size = 40)
plt.show()"""