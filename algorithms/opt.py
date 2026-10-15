class OPT:
    def __init__(self):
        self.pages = []
        self.operations = []
        self.current_index = 0

    def add_page(self, page_id):
        if page_id not in self.pages:
            self.pages.append(page_id)

    def remove_page(self, page_id):
        if page_id in self.pages:
            self.pages.remove(page_id)

    def get_queue(self):
        return self.pages.copy()

    def set_operations(self, operations):
        self.operations = operations

    def set_current_index(self, index):
        self.current_index = index

    def select_victim(self, ram, protected=None):
        if protected is None:
            protected = set()

        victim = None
        farthest_use = -1

        # Se revisa cuando se volvera a utilizar cada pagina
        for page in ram:
            if page is None or page.page_id in protected:
                continue

            next_use = None

            for i in range(self.current_index + 1, len(self.operations)):
                op, args = self.operations[i]

                if op == "use" and args[0] == page.ptr:
                    next_use = i
                    break

            # Si no se vuelve a utilizar se puede reemplazar
            if next_use is None:
                return page.page_id

            if next_use > farthest_use:
                farthest_use = next_use
                victim = page

        if victim is None:
            raise MemoryError("No hay paginas para reemplazar")

        return victim.page_id
