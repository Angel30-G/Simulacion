
class SecondChance:
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

        # Se revisan las paginas en orden para darles otra oportunidad
        while True:
            disponibles = 0

            for page_id in self.pages.copy():
                if page_id in protected:
                    continue

                for page in ram:
                    if page is None or page.page_id != page_id:
                        continue

                    disponibles += 1

                    if page.reference_bit:
                        page.reference_bit = False
                        self.pages.remove(page_id)
                        self.pages.append(page_id)
                    else:
                        return page_id

            # Si no hay paginas disponibles no se puede reemplazar
            if disponibles == 0:
                raise MemoryError("No hay paginas para reemplazar")
