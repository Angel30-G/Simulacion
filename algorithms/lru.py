class LRU:
    def __init__(self):
        self.pages = []

    def add_page(self, page_id):
        if page_id not in self.pages:
            self.pages.append(page_id)

    def remove_page(self, page_id):
        if page_id in self.pages:
            self.pages.remove(page_id)

    def get_queue(self):
        return self.pages.copy()

    def select_victim(self, ram, protected=None):
        if protected is None:
            protected = set()

        victim = None

        for page in ram:
            if page is None:
                continue

            if page.page_id in protected:
                continue

            if victim is None or page.last_used < victim.last_used:
                victim = page

        if victim is None:
            raise MemoryError("No hay paginas para reemplazar")

        return victim.page_id
