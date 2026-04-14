# Dune Dominion

> *"La especia debe fluir."* — Frank Herbert

**Dune Dominion** es un videojuego 2D de gestión estratégica y supervivencia ambientado en el universo de Dune. Asumes el rol de administrador de una Casa Menor autorizada por el Emperador para operar enclaves en el hostil planeta Arrakis. Construye instalaciones, cría criaturas exóticas, gestiona tu economía en Solaris y defiende tu base de las amenazas nocturnas del desierto.

---

## Tabla de Contenidos

1. [Descripción](#descripción)
2. [Características Principales](#características-principales)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Requisitos Previos](#requisitos-previos)
6. [Instalación](#instalación)
7. [Configuración](#configuración)
8. [Ejecución del Proyecto](#ejecución-del-proyecto)
9. [Despliegue y Distribución](#despliegue-y-distribución)
10. [Guía del Jugador](#guía-del-jugador)
11. [Contribución](#contribución)
12. [Licencia](#licencia)

---

## Descripción

Dune Dominion combina mecánicas de *tycoon* de gestión de parques con supervivencia activa en tiempo real. Durante el día, gestionas la economía de tu enclave: compras criaturas, construyes instalaciones y recibes visitantes que generan ingresos. Por la noche, el desierto cobra vida y deberás defender tu base de oleadas de enemigos.

El juego está ambientado en el año 10191 del Imperio Galáctico. La Casa Atreides acaba de tomar el control de Arrakis, y las sombras de la Casa Harkonnen acechan. Tu misión es establecer un enclave rentable y asegurar el flujo de la Especia Melange, el recurso más valioso del universo conocido.

---

## Características Principales

- **Gestión de Enclaves**: Construye y posiciona libremente en el mapa más de 9 tipos de instalaciones, desde Invernaderos y Mercados hasta Búnkeres y Oficinas de Especia.
- **Catálogo de 14 Criaturas**: Captura, cría y exhibe especies únicas del universo Dune, cada una con sus propias necesidades de alimentación, hábitat y nivel de peligrosidad.
- **Ciclo Día/Noche Dinámico**: El día trae visitantes e ingresos; la noche trae enemigos que escalan en dificultad con el paso del tiempo.
- **Sistema Económico**: Equilibra tus ingresos en Solaris, los costes de mantenimiento de instalaciones y la alimentación diaria de tus criaturas.
- **Combate Activo**: Equípate con armas (Cuchillo Fremen, Pistola Maula, Lasgun), usa pociones consumibles y contrata Reclutas Fremen o Mercenarios Sardaukar para defender tu base.
- **Mapa Procedural Infinito**: Explora un mundo generado proceduralmente con biomas de arena, roca y oasis.
- **Accesibilidad**: Incluye modos para daltónicos, escala de texto ajustable, control de fotosensibilidad y velocidad de texto configurable.
- **Audio Completo**: Música original para cada estado del juego (menú, partida, eventos de peligro, créditos) con fallback chiptune procedural.

---

## Tecnologías Utilizadas

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.8+ |
| Motor Gráfico | Pygame |
| Datos del Juego | JSON |
| Empaquetado | PyInstaller |
| Arquitectura | State Machine + Sistema de Entidades |

---

## Estructura del Proyecto

```text
Dunita/
├── dunita_game/                    # Código fuente principal (versión activa)
│   ├── assets/
│   │   ├── music/                  # Pistas de audio del juego
│   │   └── sprites/
│   │       ├── buildings_8bit/     # Sprites de edificios en pixel-art
│   │       ├── creatures_8bit/     # Sprites de criaturas en pixel-art
│   │       ├── tiles/              # Tiles del mapa (arena, roca, oasis, suelo)
│   │       └── ui/                 # Elementos de interfaz (botones, iconos, armas)
│   ├── data/
│   │   └── game_data.json          # Datos de criaturas, edificios e ítems
│   ├── src/
│   │   ├── states/
│   │   │   ├── main_menu.py        # Menú principal y subpaneles
│   │   │   ├── loading_screen.py   # Pantalla de carga
│   │   │   └── gameplay.py         # Loop principal del juego
│   │   ├── systems/
│   │   │   ├── audio_manager.py    # Gestión de música y efectos de sonido
│   │   │   ├── economy_manager.py  # Sistema económico (Solaris, criaturas, edificios)
│   │   │   ├── entities.py         # Entidades dinámicas (enemigos, visitantes, mercenarios)
│   │   │   └── world.py            # Mapa procedural, jugador y cámara
│   │   ├── ui/
│   │   │   ├── ui_manager.py       # HUD, Tienda, Panel de Turno, Modo Construcción
│   │   │   └── widgets.py          # Componentes reutilizables (botones, sliders, paneles)
│   │   ├── utils/
│   │   │   └── asset_manager.py    # Carga y gestión de recursos gráficos
│   │   ├── config.py               # Constantes, rutas, configuración y paleta de colores
│   │   └── engine.py               # Motor principal: bucle de juego y máquina de estados
│   ├── main.py                     # Punto de entrada de la aplicación
│   ├── dune_dominion.spec          # Configuración de PyInstaller
│   └── test_imports.py             # Script de validación headless
├── Documentacion/                  # Manuales, diseño y lore del juego
│   ├── Guia_Jugador/               # Manual del jugador (PDF)
│   ├── Diseno_Juego/               # Documentos de mecánicas y diseño
│   ├── Contexto/                   # Lore del universo Dune (archivos .docx)
│   ├── Imagenes-Estilo visual/     # Referencias visuales e imágenes de inspiración
│   ├── Musica/                     # Pistas de audio originales
│   ├── imagenes_edificios/         # Sprites originales de edificios (sin procesar)
│   └── Legacy_Prototipo/           # Documentación de la versión antigua (solo referencia)
└── Prototipo/                      # (Legacy) Versión anterior en C# — no usar
```

> **Nota importante**: La carpeta `Prototipo/` contiene una versión anterior del proyecto basada en C# y arquitectura web multi-agente. El desarrollo activo se encuentra exclusivamente en `dunita_game/`.

---

## Requisitos Previos

Para ejecutar el juego desde el código fuente necesitas:

- **Python 3.8** o superior — [Descargar Python](https://www.python.org/downloads/)
- **pip** (incluido con Python 3.4+)

Para compilar el ejecutable standalone adicionalmente necesitas:

- **PyInstaller** (se instala con pip)

---

## Instalación

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/carlosalonsolopez14-eng/Dunita.git
cd Dunita
```

### Paso 2: Instalar dependencias

El juego tiene una única dependencia de ejecución: Pygame.

```bash
pip install pygame
```

> Se recomienda usar un entorno virtual para aislar las dependencias:
> ```bash
> python -m venv venv
> source venv/bin/activate  # En Windows: venv\Scripts\activate
> pip install pygame
> ```

---

## Configuración

El juego no requiere ningún archivo `.env` ni configuración manual previa. Al ejecutarse por primera vez, crea automáticamente una carpeta `saves/` en el directorio de ejecución con los siguientes archivos:

| Archivo | Descripción |
|---|---|
| `saves/savegame.json` | Datos de la partida guardada (oro, día, criaturas, edificios) |
| `saves/settings.json` | Preferencias del jugador (resolución, volumen, controles, accesibilidad) |

Los datos base del juego (estadísticas de criaturas, costes de edificios, ítems) se encuentran en `dunita_game/data/game_data.json`. Este archivo puede modificarse para ajustar el balance si se desea.

---

## Ejecución del Proyecto

Desde la carpeta raíz del repositorio, navega a `dunita_game` y ejecuta el punto de entrada principal:

```bash
cd dunita_game
python main.py
```

El juego arrancará mostrando el menú principal con las opciones: **Nueva Partida**, **Cargar Partida**, **Configuración**, **Accesibilidad** y **Créditos**.

### Validación sin entorno gráfico (headless)

Si necesitas verificar que todas las importaciones y sistemas funcionan correctamente sin una pantalla (por ejemplo, en un servidor CI), puedes ejecutar el script de prueba:

```bash
cd dunita_game
python test_imports.py
```

---

## Despliegue y Distribución

El proyecto está preparado para ser compilado en un ejecutable standalone multiplataforma que **no requiere que el usuario final instale Python ni ninguna dependencia**.

### Compilar con PyInstaller

#### Paso 1: Instalar PyInstaller

```bash
pip install pyinstaller
```

#### Paso 2: Compilar el ejecutable

Desde la carpeta `dunita_game`, ejecuta el archivo de especificación incluido en el repositorio:

```bash
cd dunita_game
pyinstaller dune_dominion.spec
```

El proceso de compilación tardará unos minutos. Al finalizar, se generarán dos carpetas:

- `build/`: Archivos intermedios de compilación (se puede ignorar).
- `dist/DuneDominion/`: **El ejecutable final listo para distribuir.**

#### Paso 3: Distribuir el juego

La carpeta `dist/DuneDominion/` contiene todo lo necesario para ejecutar el juego. Comprímela en un archivo `.zip` para su distribución:

```bash
# En Linux/macOS
zip -r DuneDominion_v1.0.zip dist/DuneDominion/

# En Windows (PowerShell)
Compress-Archive -Path dist\DuneDominion\ -DestinationPath DuneDominion_v1.0.zip
```

Los usuarios finales solo necesitan descomprimir el `.zip` y ejecutar el archivo `DuneDominion` (o `DuneDominion.exe` en Windows).

### Opciones de Despliegue

| Opción | Descripción | Requisitos |
|---|---|---|
| **Ejecución desde código fuente** | Para desarrolladores. Requiere Python y Pygame instalados. | Python 3.8+, Pygame |
| **Ejecutable compilado (PyInstaller)** | Para usuarios finales. Sin dependencias externas. | Ninguno |
| **Distribución en plataformas** | ⚠️ No configurado actualmente. Se podría publicar en itch.io u otras plataformas usando el ejecutable compilado. | Cuenta en la plataforma destino |

---

## Guía del Jugador

### El Universo de Dune

Arrakis es el planeta desértico central del Imperio Galáctico y la única fuente natural de **Melange** (la Especia), la sustancia más valiosa del universo. Es esencial para la navegación interestelar y el aumento de capacidades mentales. Como administrador de una Casa Menor, tu misión es establecer un enclave que permita la explotación segura y rentable de este recurso.

### Inicio Rápido

Al comenzar una **Nueva Partida**, recibirás un presupuesto inicial de **25.000 Solaris** y una **Caseta Básica** ya colocada en el mapa. Sigue estos pasos para establecer un enclave funcional:

1. **Construye un Invernadero** (9.000 Solaris): Proporciona capacidad para criaturas herbívoras y genera ingresos pasivos.
2. **Añade un Recinto Pequeño** (5.000 Solaris): Para albergar tus primeras criaturas pequeñas.
3. **Compra tus primeras criaturas**: Empieza con especies económicas como la Liebre del Desierto (1.200 Solaris) o el Zorro del Desierto (1.800 Solaris).
4. **Construye un Mercado** (15.000 Solaris): Para atraer visitantes y multiplicar tus ingresos.
5. **Equípate para la noche**: Compra un Cuchillo Fremen (500 Solaris) antes de que caiga la oscuridad.

### Controles

| Tecla / Acción | Función |
|---|---|
| `W` / `A` / `S` / `D` o Flechas | Mover al personaje |
| `Clic Izquierdo` | Disparar arma equipada / Colocar edificio |
| `TAB` o `E` | Abrir / Cerrar la Tienda |
| `B` | Activar modo construcción (para colocar edificios comprados) |
| `I` | Abrir inventario rápido |
| `ESPACIO` | Avanzar turno |
| `ESC` | Pausar el juego / Cancelar modo construcción |

### Instalaciones

Las instalaciones son las estructuras que construyes en tu enclave. Cada una tiene una función específica y estadísticas únicas.

| Instalación | Coste | Categoría | Capacidad | Ingresos | Mantenimiento |
|---|---|---|---|---|---|
| Caseta Básica | 0 | Base | 5 | 0 | 10 |
| Recinto Pequeño | 5.000 | Alojamiento | 5 | 55 | 20 |
| Recinto Grande | 18.000 | Alojamiento | 15 | 85 | 45 |
| Búnker | 8.000 | Defensa | 4 | 20 | 50 |
| Centro de Investigación | 12.000 | Investigación | 3 | 50 | 40 |
| Mercado | 15.000 | Comercio | 10 | 95 | 30 |
| Oficina de Especia | 20.000 | Producción | 2 | 100 | 60 |
| Invernadero | 9.000 | Producción | 8 | 45 | 15 |
| Centro de Mantenimiento | 6.000 | Servicio | 6 | 30 | 25 |

### Catálogo de Criaturas

Las criaturas son especímenes que puedes comprar, exhibir y criar. Cada una requiere un tipo de recinto compatible y tiene un coste de alimentación diario.

| Criatura | Coste | Alimentación/Día | Peligrosidad | Recinto |
|---|---|---|---|---|
| Shai-Hulud (Gusano de Arena) | 50.000 | 500 | Extrema | Grande |
| Tigre Laza | 15.000 | 150 | Extrema | Grande |
| Gusano Marino | 20.000 | 200 | Alta | Grande |
| Escorpión del Desierto | 8.000 | 60 | Alta | Pequeño |
| Águila Imperial | 4.000 | 45 | Moderada | Pequeño |
| Perro-Silla | 5.000 | 50 | Moderada | Pequeño |
| Slig | 3.500 | 35 | Moderada | Pequeño |
| Ciélago | 3.000 | 30 | Baja | Pequeño |
| Águila del Desierto | 2.500 | 40 | Moderada | Pequeño |
| Muad'Dib (Ratón Canguro) | 2.500 | 25 | Baja | Pequeño |
| Tortuga de Arena | 2.000 | 20 | Baja | Pequeño |
| Zorro del Desierto | 1.800 | 20 | Baja | Pequeño |
| Araña Trampa | 1.500 | 15 | Moderada | Pequeño |
| Liebre del Desierto | 1.200 | 12 | Baja | Pequeño |

### Armas e Ítems

En la Tienda puedes adquirir armas para el combate nocturno, pociones consumibles y unidades militares.

**Armas:**

| Arma | Coste | Daño | Rango | Rareza |
|---|---|---|---|---|
| Cuchillo Fremen | 500 | 25 | 60 | Común |
| Pistola Maula | 2.500 | 40 | 300 | Raro |
| Lasgun | 8.000 | 100 | 600 | Épico |

**Pociones:**

| Ítem | Coste | Efecto | Rareza |
|---|---|---|---|
| Poción de Curación | 100 | +50 HP instantáneo | Común |
| Poción de Escudo | 250 | Escudo de 100 puntos (15 turnos) | Raro |
| Poción de Velocidad | 400 | +50% velocidad, +30% ataque (20 turnos) | Épico |

**Unidades Militares:**

| Unidad | Coste | Descripción |
|---|---|---|
| Recluta Fremen | 2.000 | Guerrero básico que patrulla y ataca enemigos cercanos |
| Mercenario Sardaukar | 8.000 | Soldado de élite con mayor potencia de fuego |

### El Ciclo Día/Noche

El juego transcurre en ciclos continuos. **Durante el día** (5 minutos reales), los visitantes llegan a tu enclave generando ingresos y puedes gestionar libremente tu base. **Durante la noche** (2 minutos reales), los visitantes se marchan y aparecen oleadas de enemigos que escalan en dificultad con cada día que pasa. Al amanecer, el juego avanza automáticamente un turno y descuenta los costes de alimentación y mantenimiento.

### Estrategias Recomendadas

**Estrategia Económica**: Prioriza el Mercado y la Oficina de Especia para maximizar ingresos. Invierte en el Centro de Investigación para desbloquear criaturas más valiosas.

**Estrategia Defensiva**: Construye el Búnker para proteger a los visitantes durante eventos. Contrata Mercenarios Sardaukar y equípate con el Lasgun para las noches más difíciles.

**Estrategia Equilibrada (Recomendada)**: Comienza con Invernadero y Recinto Pequeño, añade un Mercado en cuanto puedas y diversifica tus criaturas para maximizar el atractivo del enclave. Mantén siempre un arma equipada.

### Glosario

| Término | Definición |
|---|---|
| Arrakis | Planeta desértico donde transcurre el juego |
| Melange / Especia | Recurso estratégico y moneda simbólica del universo Dune |
| Solaris | Moneda principal del juego |
| Casa Menor | Tu facción, autorizada para operar en Arrakis |
| Enclave | Tu base de operaciones |
| Shai-Hulud | El Gusano de Arena, criatura más poderosa y venerada de Arrakis |
| Fremen | Pueblo nativo de Arrakis, adaptado al desierto |
| Rareza | Nivel de poder de un ítem: Común, Raro, Épico, Legendario |

---

## Contribución

Las contribuciones son bienvenidas. Si deseas mejorar el juego:

1. Haz un Fork del repositorio.
2. Crea una rama para tu característica (`git checkout -b feature/NuevaCaracteristica`).
3. Haz commit de tus cambios (`git commit -m 'Añadir NuevaCaracteristica'`).
4. Haz push a la rama (`git push origin feature/NuevaCaracteristica`).
5. Abre un Pull Request describiendo los cambios realizados.

---

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

*Inspirado en el universo de Dune de Frank Herbert. Construido con Python y Pygame.*

*Que la especia fluya en tu favor.*
