import random

def generate_scenario(seed, num_processes, total_ops):
    rng = random.Random(seed)
    operations = []
    symbol_tables = {}
    ptr_counter = 1

    if total_ops < num_processes * 2:
        raise ValueError("No hay suficientes operaciones para los procesos")

    # Al menos un new por proceso
    for pid in range(1, num_processes + 1):
        symbol_tables[pid] = []
        size = rng.choice([100, 500, 1000, 5000, 10000])
        operations.append(('new', [pid, size]))
        symbol_tables[pid].append(ptr_counter)
        ptr_counter += 1

    # Operaciones aleatorias intermedias
    cantidad = total_ops - num_processes * 2

    for _ in range(cantidad):
        pid = rng.randint(1, num_processes)
        symbol_table = symbol_tables[pid]

        if symbol_table and rng.random() < 0.6:
            op = rng.choice(['use', 'delete', 'new'])
        else:
            op = 'new'

        if op == 'new':
            size = rng.choice([100, 500, 1000, 5000, 10000])
            operations.append(('new', [pid, size]))
            symbol_table.append(ptr_counter)
            ptr_counter += 1

        elif op == 'use':
            ptr = rng.choice(symbol_table)
            operations.append(('use', [ptr]))

        elif op == 'delete':
            ptr = rng.choice(symbol_table)
            operations.append(('delete', [ptr]))
            symbol_table.remove(ptr)

    # kill al final de cada proceso
    for pid in range(1, num_processes + 1):
        operations.append(('kill', [pid]))

    return operations
