from collections import deque


class FIFO:
    def __init__(self):
        self.queue = deque()

    def add_page(self, page_id):
        """Registra una página cuando ingresa a RAM."""
        if page_id not in self.queue:
            self.queue.append(page_id)

    def remove_page(self, page_id):
        """Elimina una página de la cola."""
        try:
            self.queue.remove(page_id)
        except ValueError:
            pass

    def select_victim(self):
        """Selecciona la página que lleva más tiempo en RAM."""
        if not self.queue:
            raise MemoryError("No hay páginas para reemplazar")

        return self.queue.popleft()

    def get_queue(self):
        """Devuelve una copia del orden de las páginas."""
        return list(self.queue)
