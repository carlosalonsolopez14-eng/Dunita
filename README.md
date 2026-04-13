
# Dunita - Dune Dominion Multi-Agent Simulator

Un simulador de gestión de zoológico/parque temático ambientado en el universo de Dune, construido con una arquitectura multi-agente para una simulación realista y modular.

## 🎯 Visión General

Dunita es un proyecto de simulación que combina elementos de gestión estratégica con inteligencia artificial distribuida. Los jugadores gestionan enclaves en Arrakis, criando criaturas exóticas, construyendo instalaciones y maximizando ingresos a través de visitantes.

El proyecto destaca por su arquitectura multi-agente, donde cada aspecto del sistema está manejado por agentes especializados que cooperan de manera autónoma.

## 🏗️ Arquitectura Multi-Agente

### Jerarquía de Agentes

```
🏛️ ORQUESTADOR PRINCIPAL (Client)
├── 🐾 AGENTE DE ANIMALES (Simulation)
├── 🏗️ AGENTE DE CONSTRUCCIÓN (Simulation)
├── 🗺️ AGENTE DE MAPAS (Simulation)
└── 💾 AGENTE DE PERSISTENCIA (Persistence)
```

### Componentes

- **DuneDominion.Shared**: Modelos de datos y clase base `Agent`
- **DuneDominion.Simulation**: Agentes especializados en simulación
  - `AnimalAgent`: Gestiona ciclo de vida de criaturas
  - `ConstructionAgent`: Maneja monetización y visitantes
  - `MapAgent`: Controla enclaves y territorio
  - `SimulationOrchestrator`: Coordina agentes de simulación
- **DuneDominion.Persistence**: Gestión de datos
  - `PersistenceAgent`: Guardado/carga de estado
  - `PersistenceOrchestrator`: Coordinación de persistencia
- **DuneDominion.Client**: Interfaz y orquestación principal
  - `MainOrchestrator`: Punto de entrada unificado

## ✨ Características

- **Simulación mensual**: Ciclos realistas de recursos y población
- **Sistema de enclaves**: Diferentes tipos (aclimatación, exhibición)
- **Gestión de criaturas**: Necesidades biológicas, salud, edad
- **Monetización dinámica**: Basada en visitantes y atracciones
- **Persistencia JSON**: Guardado y carga de partidas
- **Interfaz consola**: Menú interactivo completo

## 🚀 Instalación y Ejecución

### Prerrequisitos

- .NET 8.0 SDK
- Sistema operativo compatible (Linux/Windows/macOS)

### Ejecutar la Aplicación

```bash
cd DuneDominion.Client
dotnet run
```

### Ejecutar Documentación Web

```bash
cd Documentacion
python3 -m http.server 8000
```

Visita `http://localhost:8000` para ver la documentación.

## 📊 Documentación

- **[Arquitectura IA](Documentacion/arquitectura-ai-zoo.html)**: Diagrama interactivo de la jerarquía de agentes
- **[Homepage Web](index.html)**: Página principal con visión general del proyecto

## 🎮 Cómo Jugar

1. **Nueva Partida**: Comienza con el escenario Arrakeen preconfigurado
2. **Gestionar Enclaves**: Construye instalaciones y cría criaturas
3. **Ejecutar Rondas**: Avanza el tiempo mensualmente
4. **Monetizar**: Atrae visitantes y genera ingresos
5. **Guardar Progreso**: Persiste tu partida en JSON

### Controles

- `1`: Ver estado de enclaves y criaturas
- `2`: Ejecutar ronda mensual
- `3`: Guardar partida
- `4`: Tienda (próximamente)
- `5`: Salir

## 🛠️ Desarrollo

### Compilar

```bash
dotnet build
```

### Ejecutar Tests

```bash
dotnet test
```

### Arquitectura de Agentes

Cada agente implementa la interfaz `Agent` con el método `ExecuteAsync(Partida partida)`. Los orquestadores coordinan la ejecución de agentes especializados, permitiendo una separación clara de responsabilidades y extensibilidad.

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- Inspirado en el universo de Dune de Frank Herbert
- Arquitectura multi-agente basada en patrones de IA distribuida
- Construido con .NET 8.0 y C#

---

**Estado del Proyecto**: En desarrollo activo 🏗️

Para más información, visita la [documentación web](index.html) o el [diagrama de arquitectura](Documentacion/arquitectura-ai-zoo.html).