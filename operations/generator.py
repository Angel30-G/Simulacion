import random

def generate_scenario(seed, num_processes, total_ops):
    rng = random.Random(seed)
    operations = []
    ops_count = 0
    pid = 1
    while ops_count < total_ops and pid <= num_processes:
        # Generar operaciones para el proceso pid
        process_ops = []
        symbol_table = []  # lista de ptrs
        ptr_counter = 1  # contador global de ptrs (si aplica)
        # Al menos un new
        size = rng.choice([100, 500, 1000, 5000, 10000])
        process_ops.append(('new', [pid, size]))
        symbol_table.append(ptr_counter)
        ptr_counter += 1
        # Operaciones aleatorias intermedias
        for _ in range(rng.randint(1, 5)):
            if symbol_table and rng.random() < 0.6:
                op = rng.choice(['use', 'delete', 'new'])
            else:
                op = 'new'
            if op == 'new':
                size = rng.choice([100, 500, 1000, 5000, 10000])
                process_ops.append(('new', [pid, size]))
                symbol_table.append(ptr_counter)
                ptr_counter += 1
            elif op == 'use':
                ptr = rng.choice(symbol_table)
                process_ops.append(('use', [ptr]))
            elif op == 'delete':
                ptr = rng.choice(symbol_table)
                process_ops.append(('delete', [ptr]))
                symbol_table.remove(ptr)
            if ops_count + len(process_ops) >= total_ops:
                break
        # kill al final
        process_ops.append(('kill', [pid]))
        operations.extend(process_ops)
        ops_count += len(process_ops)
        pid += 1
    return operations[:total_ops]