import csv
from concurrent.futures import ProcessPoolExecutor
from evaluator import Evaluator
from itertools import product
from multiprocessing import Lock
from chimeraModification import ChimeraModification

csv_file = 'chimera_orders_data.csv'

with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['target_graph', 'n', 'embedding_id', 'chain_length'])

lock = Lock()

c1, c2, c5 = ChimeraModification(10), ChimeraModification(10), ChimeraModification(10)
c1.add_original_hor_ver_connections()
c2.add_hor_ver_connections(2)
c3, c4 = c1.copy(), c1.copy()
c3.add_hor_ver_connections(2)
c4.add_hor_ver_connections(3)
c5.add_hor_ver_connections(1, all=False, even=True)
c5.add_hor_ver_connections(2, all=False, even=False)

target_graphs = {'original': c1.g, 'only_order_2': c2.g, 'order1_plus_order2': c3.g,
                 'order1_plus_order3': c4.g, 'order1_combined_order2': c5.g}



def chain_length_function(combination):
    tg, n = combination
    print(f'Starting combination: {tg}, n={n}')
    ev = Evaluator(target_graphs[tg])
    results = []
    values = ev.eval_lengths(n, iterations=10, attempts=10)
    if values is None:
        results.append((tg, n, 0, 'NA'))
    else:
        id_num = 0
        for row in values:
            for value in row:
                results.append((tg, n, id_num, value))
            id_num += 1
    with lock:
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(results)
    print(f'Finished combination: {tg}, n={n}')


def main():
    #n_values = list(range(9, 60, 9))
    n_values = [12]
    # n_values.append(list(range(141, 240, 30)))
    combinations = [(tg, n) for tg, n in product(target_graphs, n_values)]

    print(f'Total combinations to process: {len(combinations)}')

    with ProcessPoolExecutor() as executor:
        executor.map(chain_length_function, combinations)


if __name__ == '__main__':
    main()
    print(f'CSV file {csv_file} created successfully.')
