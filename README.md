# Simulador de Paginación — Proyecto 2 de Sistemas Operativos

Simulación de un sistema operativo doméstico que compara el algoritmo de
reemplazo **Óptimo (OPT)** contra uno seleccionable por el usuario
(**FIFO**, **Second Chance**, **LRU**, **LFU**), con visualización en vivo
del estado de la memoria RAM, la memoria virtual en disco y estadísticas
de rendimiento (thrashing, fragmentación interna, uso de RAM, etc.).

---

## Requisitos

- **Debian / Ubuntu** (o cualquier derivado de Linux con entorno gráfico X11 o Wayland)
- **Python 3.10 o superior**
- **pip** y **venv**
- Bibliotecas gráficas de Qt (necesarias para que PyQt5 abra ventanas)

Para verificar que tienes Python:

```bash
python3 --version
pip3 --version
```

Si te falta alguno, instálalos con:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Angel30-G/Simulacion.git
cd Simulacion
```

### 2. Crear y activar un entorno virtual

> **Importante:** crea el entorno virtual con tu **usuario normal**, nunca como `root`.
> Si trabajas como `root` tendrás problemas de permisos después.

```bash
python3 -m venv venv
source venv/bin/activate
```

Sabrás que el entorno está activo porque el prompt cambia a algo como:

```
(venv) angel@debian:~/Documentos/Simulacion$
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instalar las librerías gráficas del sistema (solo la primera vez)

PyQt5 necesita algunas librerías de Qt que Debian no trae por defecto. Si al
ejecutar el programa ves errores como
`Could not load the Qt platform plugin "xcb"` o `libGL.so.1 not found`,
ejecuta:

```bash
sudo apt install libgl1 libglib2.0-0 libxcb-xinerama0 \
                 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0
```

---

## Cómo ejecutar

Con el entorno virtual activado y estando **dentro de la carpeta del proyecto**:

```bash
cd ~/Documentos/Simulacion    # o donde hayas clonado el repo
source venv/bin/activate
python3 main.py
```

Se abrirá la **ventana de configuración**. Desde ahí puedes:

1. Definir la **semilla** de aleatoriedad (para reproducir escenarios).
2. Elegir el **algoritmo** a comparar contra OPT (FIFO, SC, LRU, LFU).
3. Cargar un **archivo de operaciones** existente, *o* generar uno nuevo
   indicando la **cantidad de procesos (P)** y la **cantidad de operaciones (N)**.
4. **Descargar** el archivo de operaciones generado (formato compatible con el
   Anexo 1 del enunciado).
5. Presionar **Iniciar Simulación** para abrir la ventana de simulación.

En la ventana de simulación encontrarás los controles:

- **⏸ Pausar / ▶ Reanudar** la simulación en cualquier momento.
- **⏭ Paso a paso** para avanzar una operación a la vez.
- **⟲ Reiniciar** para volver al inicio con el mismo escenario.

---

## Formato del archivo de operaciones

El archivo debe estar en texto plano, una instrucción por línea, con el
siguiente formato (compatible con el Anexo 1 del enunciado):

```
new(1,500)
use(1)
new(1,1000)
use(1)
use(2)
new(2,500)
use(3)
use(1)
new(2,50)
use(4)
delete(1)
use(2)
use(3)
delete(2)
kill(1)
kill(2)
```

Reglas:

- `new(pid, size)` → solicita memoria de `size` bytes para el proceso `pid`.
- `use(ptr)` → accede a un puntero ya asignado.
- `delete(ptr)` → libera la memoria del puntero.
- `kill(pid)` → libera toda la memoria del proceso. Debe ser **la última
  instrucción** de ese proceso.
- Los `ptr` se numeran por **orden de aparición** de los `new` (el primer
  `new` produce el ptr `1`, el segundo el ptr `2`, y así sucesivamente).

En la carpeta `examples/` hay un archivo `Prueba.txt` que puedes usar como
referencia o para probar la simulación.

---

## Estructura del proyecto

```
Simulacion/
├── algorithms/          # Implementación de los algoritmos de reemplazo
├── core/                # Motor de la simulación
│   ├── models.py        # Clases Page, Frame, Process
│   ├── mmu.py           # Memory Management Unit (RAM + V-RAM)
│   └── simulator.py     # Coordinación de OPT y el algoritmo elegido
├── interface/           # Interfaz gráfica (PyQt5)
│   ├── app.py           # Ventana de configuración
│   └── visualization.py # Ventana de simulación con las dos memorias
├── operations/          # Manejo de operaciones
│   ├── generator.py     # Generación de escenarios con semilla, P y N
│   └── parser.py        # Lectura del archivo de operaciones
├── tests/               # Pruebas unitarias (pytest)
├── examples/            # Archivos de ejemplo
├── main.py              # Punto de entrada
└── requirements.txt     # Dependencias de Python
```

---

## Ejecutar las pruebas

```bash
source venv/bin/activate
pytest tests/ -v
```

---

## Problemas comunes

### `python3: can't open file '/root/main.py': [Errno 2] No such file or directory`

Estás ejecutando el comando desde la carpeta equivocada (probablemente
`/root`). Verifica con `pwd` y muévete a la carpeta del proyecto:

```bash
cd ~/Documentos/Simulacion
python3 main.py
```

### `ModuleNotFoundError: No module named 'PyQt5'`

El entorno virtual no está activado, o no instalaste las dependencias:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"`

Faltan librerías gráficas del sistema:

```bash
sudo apt install libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0
```

### `libGL.so.1: cannot open shared object file`

```bash
sudo apt install libgl1
```

### Error de permisos al usar el venv

Si creaste el venv como `root` por accidente:

```bash
sudo rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Notas sobre la simulación

- **RAM simulada:** 100 páginas × 4 KB = 400 KB.
- **Tiempo de acceso a disco:** 5 s por cada fallo de página (miss).
- **Tiempo de acceso a RAM (hit):** 1 s por página.
- El programa corre **OPT y el algoritmo elegido en paralelo**, avanzando
  una operación a la vez para mantener ambos relojes sincronizados.
- La métrica de **thrashing** se marca en rojo cuando supera el 50 % del
  tiempo total de simulación.

---

Proyecto desarrollado para el curso de **Sistemas Operativos**.
