import re

def parse_operations_file(file_path):
    operations = []
    pattern = re.compile(r'(\w+)\(([^)]*)\)')
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = pattern.match(line)
            if match:
                op = match.group(1)
                args = [int(x.strip()) for x in match.group(2).split(',')]
                operations.append((op, args))
    return operations