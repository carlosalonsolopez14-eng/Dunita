# 🚀 DUNITA - Guía de Despliegue

## ¿Qué se ha implementado?

### 1. **DeploymentAgent** (Nueva Arquitectura Multi-Agente)
   - Módulo: `DuneDominion.Deployment`
   - Métodos principales:
     - `StartServicesAsync()`: Levanta automáticamente todos los servicios
     - `StopServicesAsync()`: Detiene los servicios
     - `CheckStatusAsync()`: Verifica estado
     - `OpenBrowser()`: Abre automáticamente en el navegador

### 2. **Dockerfile**
   - Build multi-stage para optimización
   - SDK .NET 8.0 para compilación
   - Runtime ASP.NET Core para ejecución
   - Compila en Release automáticamente
   - Expone puerto 5000

### 3. **Docker Compose**
   - Servicio principal: `dunita-app` (aplicación web)
   - Servicio documentación: `dunita-docs` (servidor web en puerto 8080)
   - Auto-reinicio de servicios
   - Health checks automáticos
   - Volúmenes para persistencia

### 4. **Scripts de Inicio Automático**

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

Ambos scripts:
- Verifican que Docker esté instalado
- Construyen las imágenes
- Levantan los servicios
- Abren automáticamente el navegador en http://localhost:5000

## 📂 Estructura de Archivos

```
Dunita/
├── Dockerfile                 # Configuración de contenedor
├── docker-compose.yml         # Orquestación de servicios
├── start.sh                   # Script automático (Linux/macOS)
├── start.bat                  # Script automático (Windows)
├── DuneDominion.Deployment/   # Nuevo módulo de despliegue
│   ├── DeploymentAgent.cs     # Agente de despliegue
│   └── DuneDominion.Deployment.csproj
├── DuneDominion.Client/       # Aplicación web
├── DuneDominion.Simulation/   # Lógica de simulación
├── DuneDominion.Persistence/  # Persistencia de datos
└── DuneDominion.Shared/       # Modelos compartidos
```

## 🎯 Opciones de Ejecución

### Opción 1: Inicio Automático (Recomendado)
```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

### Opción 2: Docker Compose Manual
```bash
docker-compose up -d
docker-compose logs -f dunita-app
docker-compose down
```

### Opción 3: Ejecución Local sin Docker
```bash
cd DuneDominion.Client
dotnet run
```

## 📊 Servicios Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Aplicación Web | http://localhost:5000 | Juego interactivo |
| Documentación | http://localhost:8080 | Diagramas y guías |

## ✨ Arquitectura Multi-Agente Completa

```
🏛️ ORQUESTADOR PRINCIPAL (Client)
├── 🐾 AGENTE DE ANIMALES (Simulation)
├── 🏗️ AGENTE DE CONSTRUCCIÓN (Simulation)
├── 🗺️ AGENTE DE MAPAS (Simulation)
├── 💾 AGENTE DE PERSISTENCIA (Persistence)
└── 🚀 AGENTE DE DESPLIEGUE (Deployment) ← NUEVO
```

## 🔧 Comandos Útiles Docker

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Reconstruir sin caché
docker-compose build --no-cache

# Limpiar todo
docker-compose down -v

# Ejecutar comando en contenedor
docker-compose exec dunita-app bash
```

## 📝 Próximas Mejoras

- [ ] Database service (PostgreSQL)
- [ ] Redis para caché
- [ ] Nginx como reverse proxy
- [ ] Health checks más avanzados
- [ ] Logs centralizados
- [ ] Monitoring con Prometheus

---

**Estado**: ✅ Proyecto completamente containerizado y listo para desplegar

Ejecuta `./start.sh` (Linux/macOS) o `start.bat` (Windows) para comenzar 🎮