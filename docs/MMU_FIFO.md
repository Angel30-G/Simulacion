
# Implementación de la MMU y FIFO

## Responsable
Keylor Herrera Fuentes

## Descripción

Este módulo implementa la unidad de gestión de memoria (MMU)
del simulador de paginación y el algoritmo de reemplazo FIFO.

## Características de la memoria

- RAM simulada: 400 KB.
- Marcos de memoria física: 100.
- Tamaño de página: 4 KB.
- Memoria virtual: sin límite fijo en la simulación.

## Estructuras

El archivo `core/models.py` define:

- `Page`: representa una página y su ubicación.
- `Pointer`: representa una asignación que contiene una o varias páginas.
- `Process`: registra los punteros asociados a un proceso.

## Operaciones de la MMU

`new(pid, size)`

Crea un puntero y asigna las páginas correspondientes al
tamaño solicitado. Los identificadores de punteros no se
reutilizan.

`use(ptr)`

Accede a las páginas de un puntero. Registra los hits y
recupera las páginas que se encuentran en memoria virtual,
utilizando reemplazo cuando corresponde.

`delete(ptr)`

Elimina el puntero y libera todas sus páginas.

`kill(pid)`

Finaliza el proceso y libera todos sus punteros y páginas.

## Algoritmo FIFO

FIFO mantiene el orden de ingreso de las páginas residentes.

Cuando la RAM está llena y se necesita cargar una página,
se selecciona la página residente más antigua para enviarla
a memoria virtual.

Los accesos a páginas residentes no modifican su orden FIFO.

## Estadísticas

La MMU registra:

- Procesos activos.
- Memoria RAM utilizada y su porcentaje.
- Memoria virtual utilizada.
- Hits y fallos de página.
- Tiempo de simulación.
- Tiempo y porcentaje de thrashing.
- Fragmentación interna de las asignaciones existentes.

Cada hit contabiliza 1 segundo y cada fallo 5 segundos.

## Archivos principales

- `core/models.py`
- `core/mmu.py`
- `algorithms/fifo.py`

## Pruebas

Las pruebas están en:

- `tests/test_mmu.py`
- `tests/test_fifo.py`
- `tests/test_virtual_memory.py`
- `tests/test_mmu_final.py`

Para ejecutarlas desde la raíz del proyecto:

```bash
python3 -m unittest discover -s tests -v
```

## Integración

La MMU recibe opcionalmente un algoritmo en su constructor.
La implementación actual está integrada y probada con FIFO.

Los demás algoritmos deben acordar una interfaz común antes
de sustituir FIFO en la MMU.

## Consideración de diseño

Cuando un puntero necesita más páginas que los 100 marcos
disponibles, se procesan sus páginas secuencialmente, sin
exceder la capacidad de la RAM.

Esta interpretación debe confirmarse con el profesor, ya que
no es posible mantener simultáneamente más de 100 páginas
en los 100 marcos físicos disponibles.
