# D-Wave architectures with new links

Support code I wrote in 2024, during my second year of university, for some of the
experiments in **Section 5** of:

> N. Apostolakis, **M. Sierra-Obea**, M. Gramaglia, J. A. Ayala-Romero, A. Garcia-Saavedra,
> M. Fiore, A. Banchs, X. Costa-Perez.
> *Quantum Computing in the RAN with Qu4Fec: Closing Gaps Towards Quantum-based FEC processors.*
> Proceedings of the ACM on Measurement and Analysis of Computing Systems (POMACS), 9(2), 2025.
> [doi:10.1145/3727128](https://doi.org/10.1145/3727128)

The question behind it: **what would happen if a D-Wave QPU had extra couplers between its
qubits?** The code builds D-Wave hardware graphs from scratch so that you can add
couplers the real hardware doesn't have. It then embeds LDPC decoding problems onto those
graphs with [minorminer](https://github.com/dwavesystems/minorminer) and measures chain
lengths. Shorter chains mean fewer physical qubits per logical variable, which generally
means better annealing results.

This is research support code shared as it was used, not a maintained library.

## Repository layout

```
dwave_links/
├── topologies/
│   ├── chimera.py              # Chimera graph builder + extra (longer-range) couplers
│   ├── pegasus.py              # Pegasus graph builder (standard couplers)
│   └── zephyr.py               # Zephyr graph builder (standard couplers)
└── embedding/
    ├── ldpc.py                 # (2,3)-regular LDPC code -> QUBO interaction graph
    ├── minorminer_embedder.py  # minorminer wrapper, keeps the best of N embeddings
    └── evaluator.py            # chain-length statistics over many random LDPC codes
scripts/
├── chimera_chain_lengths.py    # chain-length experiment on 5 Chimera variants -> CSV
└── visualize_topologies.py     # draw the graphs with matplotlib
```

## Installation

Python 3.9+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`pyldpc` is pinned to `0.7.8` because the code calls `make_ldpc(n_code=...)`, an argument
name that only that release uses. `numba` is listed separately because `pyldpc` imports it
without declaring it as a dependency.

## Usage

Run the scripts as modules from the repository root:

```bash
# Chain-length experiment on Chimera variants -> chimera_orders_data.csv
python -m scripts.chimera_chain_lengths

# Plot a Chimera graph (Pegasus/Zephyr examples are commented out in the file)
python -m scripts.visualize_topologies
```

Or use the package directly:

```python
from dwave_links.topologies import ChimeraModification
from dwave_links.embedding import Evaluator

c = ChimeraModification(10)              # 10x10 grid of K_{4,4} unit cells
c.add_original_hor_ver_connections()     # standard Chimera couplers
c.add_hor_ver_connections(order=2)       # + couplers that skip one unit cell

ev = Evaluator(c.g)
print(ev.nice_results_eval_lengths(n=12, iterations=10, attempts=10))
# {'mean': ..., 'max': ...}  average and max chain length over 10 random LDPC codes
```

## How it works

### Topologies

Each `*Modification` class starts from an empty graph that contains only the qubits, using
the same linear indexing and drawing positions as
[`dwave_networkx`](https://github.com/dwavesystems/dwave-networkx). You then add couplers
one family at a time.

- **`ChimeraModification(m, n=None, t=4)`**: an `m × n` grid of `K_{t,t}` unit cells.
  The intra-cell bipartite couplers are always added.
  - `add_original_hor_ver_connections()` adds the standard inter-cell couplers. The
    result is isomorphic to `dnx.chimera_graph(m, n, t)`.
  - `add_hor_ver_connections(order, all=True, even=True)` connects each qubit to the qubit
    in the same position `order` cells away, horizontally and vertically. `order=1` gives
    the standard couplers; `order=2` skips one cell, and so on. With `all=False` only
    even-indexed (`even=True`) or odd-indexed (`even=False`) qubits get the new couplers,
    so you can mix link lengths within a cell.
  - `add_horizontal_connections` / `add_vertical_connections` do the same in one direction.
- **`PegasusModification(m)`**: `add_original_connections()` reproduces
  `dnx.pegasus_graph(m)` (fabric only) edge for edge.
- **`ZephyrModification(m, t=4)`**: `add_original_connections()` reproduces
  `dnx.zephyr_graph(m, t)`.

Only Chimera has extra-coupler methods. Pegasus and Zephyr stop at the standard
couplers, in the same form, so they're ready for the same kind of changes.

### Problem graphs

`ldpc.generate_2_3_regular_ldpc_code(n)` draws a random (2,3)-regular LDPC parity-check
matrix with `n` variable nodes (via `pyldpc`). It turns every check into a clique over
its variable nodes plus `log2(d_c/2) + 1` ancilla qubits (named `qe0`, `qe1`, …). That is
the interaction graph of the QUBO formulation of the parity constraints.

### Evaluation

`Evaluator(target_graph).eval_lengths(n, iterations, attempts)`:

1. generates `iterations` random LDPC problem graphs of size `n`,
2. embeds each one up to `attempts` times with minorminer and keeps the embedding with
   the shortest maximum chain,
3. returns the chain length of every logical variable for every problem graph.

It returns `None` after 5 failed embeddings (the problem doesn't fit the target).

### The included experiment

`scripts/chimera_chain_lengths.py` compares five 10×10 Chimera graphs:

| name                      | couplers                                                     |
|---------------------------|--------------------------------------------------------------|
| `original`                | standard Chimera                                             |
| `only_order_2`            | order-2 links instead of the standard ones                   |
| `order1_plus_order2`      | standard + order-2 links                                     |
| `order1_plus_order3`      | standard + order-3 links                                     |
| `order1_combined_order2`  | order-1 on even qubits + order-2 on odd qubits               |

It runs the combinations in parallel and writes one row per logical variable to
`chimera_orders_data.csv`, with columns `target_graph, n, embedding_id, chain_length`.

## Known quirks

- In `MinorminerEmbedder`, the default `seed=random.randint(...)` is evaluated once, when
  the class is defined, not on each call. All the "retry" embeddings in one process
  therefore use the same seed. Different LDPC codes still get different random problem
  graphs.
- `scripts/visualize_topologies.py` opens matplotlib windows, so it needs a GUI backend.

## Citation

If this code is useful to you, please cite the paper:

```bibtex
@article{apostolakis2025qu4fec,
  title   = {Quantum Computing in the RAN with Qu4Fec: Closing Gaps Towards Quantum-based FEC processors},
  author  = {Apostolakis, Nikolaos and Sierra-Obea, Marta and Gramaglia, Marco and Ayala-Romero, Jose A. and Garcia-Saavedra, Andres and Fiore, Marco and Banchs, Albert and Costa-Perez, Xavier},
  journal = {Proceedings of the ACM on Measurement and Analysis of Computing Systems},
  volume  = {9},
  number  = {2},
  year    = {2025},
  doi     = {10.1145/3727128}
}
```
