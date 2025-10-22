# Dashboard de Indicadores Ambientales: Bosques Riparios y Huella Humana en Ecuador

## Resumen Ejecutivo

Este repositorio contiene los dashboards interactivos de análisis de dos indicadores ambientales críticos para el monitoreo ecológico en Ecuador: (1) **Bosques Riparios (BR)** y (2) **Huella Humana (HH)**. Ambas aplicaciones implementan tecnologías modernas de visualización de datos y computación en la nube, permitiendo la consulta, análisis e interpretación de datos geoespaciales mediante interfaces web responsivas.

---

## 1. Introducción

### 1.1 Contexto Ambiental

Los bosques riparios constituyen ecosistemas críticos que actúan como amortiguadores hidrológicos y corredores biológicos. La Huella Humana, por su parte, es un indicador que cuantifica la intensidad del impacto antropogénico en los ecosistemas. Este proyecto proporciona herramientas de visualización y análisis para monitorear la evolución temporal y espacial de ambos indicadores en el territorio ecuatoriano.

### 1.2 Propósito del Proyecto

Facilitar el acceso a datos geoespaciales ambientales a través de dashboards interactivos que permitan:
- Monitoreo continuo de indicadores de conservación
- Análisis de tendencias temporales y distribución espacial
- Toma de decisiones informadas en política ambiental
- Divulgación científica y educación ambiental

---

## 2. Descripción Técnica

### 2.1 Arquitectura del Sistema

El proyecto implementa una arquitectura de microservicios containerizada:

```
┌──────────────────────────────────────────────────────────────┐
│                    Docker Compose Orquestador                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐      ┌──────────────────────────┐  │
│  │   Bosques Riparios   │      │    Huella Humana         │  │
│  │   (Dashboard BR)     │      │    (Dashboard HH)        │  │
│  │   Puerto: 8001       │      │    Puerto: 8002          │  │
│  └──────────────────────┘      └──────────────────────────┘  │
│           │                              │                   │
│           └──────────┬──────────────────┘                    │
│                      │                                       │
│              ┌───────▼────────┐                              │
│              │ Firebase Cloud │                              │
│              │  (Auth, DB)    │                              │
│              └────────────────┘                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Stack Tecnológico

#### Backend
- **Python 3.13+**: Lenguaje de programación principal
- **Shiny for Python**: Framework web reactivo para dashboards
- **Pandas**: Procesamiento y manipulación de datos
- **Plotly**: Visualización interactiva de datos
- **ipyleaflet**: Mapas interactivos basados en Leaflet

#### Frontend
- **HTML5**: Interfaz web
- **CSS3**: Diseño responsivo y animaciones
- **Chart.js**: Gráficas estadísticas
- **JavaScript (Vanilla)**: Interactividad del lado del cliente

#### Infraestructura
- **Docker & Docker Compose**: Containerización y orquestación
- **Firebase Realtime Database**: Almacenamiento de datos
- **Firebase Storage**: Gestión de archivos y CSV
- **Firebase Authentication**: Control de acceso

### 2.3 Módulos Principales

#### 2.3.1 Dashboard de Bosques Riparios (`br/br.py`)

**Funcionalidades:**
- Carga de datos desde Firebase Storage (CSV compilado de estadísticas)
- Análisis por buffers de 30m y 100m
- Visualización temporal de tendencias (píxeles, proporciones, porcentajes)
- Integración con mapas interactivos georreferenciados
- Exportación de datos procesados

**Datos procesados:**
- `pixels_30m`: Número total de píxeles de riparios a 30m
- `pixels_bosque_30m`: Píxeles de bosque ripario a 30m
- `proporcion_30m`: Proporción de cobertura forestal a 30m
- `pixels_100m`: Número total de píxeles de riparios a 100m
- `pixels_bosque_100m`: Píxeles de bosque ripario a 100m
- `proporcion_100m`: Proporción de cobertura forestal a 100m

#### 2.3.2 Dashboard de Huella Humana (`hh/hh.py`)

**Funcionalidades:**
- Carga de datos categorizados desde Firebase Storage
- Clasificación por rangos de intensidad de impacto humano
- Análisis temporal de cambios en categorías
- Visualización cartográfica del impacto antropogénico
- Interfaz interactiva con filtros dinámicos

**Categorías de Huella Humana:**
- Basadas en clasificación IUCN de intensidad de impacto
- Análisis multi-temporal desde 1993-presente

### 2.4 Integración con Firebase

Ambas aplicaciones utilizan Firebase como backend de datos:

```python
# Ejemplo de configuración
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}
```

---

## 3. Instalación y Configuración

### 3.1 Requisitos Previos

- Docker y Docker Compose (v3.8+)
- Python 3.13+ (para desarrollo local sin Docker)
- Variables de entorno Firebase configuradas
- Acceso a los datasets en Firebase Storage

### 3.2 Configuración del Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
FIREBASE_API_KEY=<tu_api_key>
FIREBASE_AUTH_DOMAIN=<tu_auth_domain>
FIREBASE_DATABASE_URL=<tu_database_url>
FIREBASE_PROJECT_ID=<tu_project_id>
FIREBASE_STORAGE_BUCKET=<tu_storage_bucket>
FIREBASE_MESSAGING_SENDER_ID=<tu_messaging_sender_id>
FIREBASE_APP_ID=<tu_app_id>
```

### 3.3 Despliegue con Docker Compose

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f bosques-riparios    # Dashboard BR (puerto 8001)
docker-compose logs -f huella-humana       # Dashboard HH (puerto 8002)
```

**URLs de acceso:**
- Dashboard Bosques Riparios: `http://localhost:8001`
- Dashboard Huella Humana: `http://localhost:8002`
- Portal de integración: `http://localhost` (index.html)

### 3.4 Instalación Local (Desarrollo)

```bash
# Clonar repositorio
git clone https://github.com/USER/REPO
cd Indicadores

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar dashboard BR
cd br && python br.py

# Ejecutar dashboard HH (en otra terminal)
cd hh && python hh.py
```

---

## 4. Estructura del Repositorio

```
Indicadores/
├── README.md                           # Este archivo
├── docker-compose.yml                  # Configuración de servicios
├── index.html                          # Portal de integración
├── br/                                 # Dashboard Bosques Riparios
│   ├── br.py                          # Aplicación principal
│   ├── Dockerfile                      # Configuración de contenedor
│   └── __pycache__/
├── hh/                                 # Dashboard Huella Humana
│   ├── hh.py                          # Aplicación principal
│   ├── Dockerfile                      # Configuración de contenedor
│   └── __pycache__/
└── __pycache__/
```

---

## 5. Metodología y Datasets

### 5.1 Datos de Bosques Riparios

**Fuente:** Procesamiento mediante análisis de detección remota
**Resolución espacial:** 30m y 100m
**Período:** Múltiples años (configurable)
**Formato:** CSV compilado alojado en Firebase Storage
**Ruta:** `MapasBosques/estadisticas_bosque_riparios_compiladas.csv`

**Variables principales:**
- Cobertura forestal en zonas riparias
- Proporción de bosque ripario respecto a zona riparia total
- Análisis comparativo entre buffers de protección

### 5.2 Datos de Huella Humana

**Fuente:** Cálculo mediante índice de presión antropogénica
**Resolución espacial:** Variable según análisis
**Período:** 1993-presente
**Formato:** CSV categorizado
**Ruta:** `MapasPNG/HH_predeterminado.csv`

**Clasificación:**
- Categorías de intensidad de impacto (txt_rango)
- Años de análisis (year)
- Estadísticas de distribución espacial

---

## 6. Características de Interfaz

### 6.1 Diseño Responsivo

Ambos dashboards implementan:
- Paleta de colores: Lime (#C7F808) y Azul Oscuro (#1D2331)
- Grid layout responsivo
- Fuentes personalizadas: Oswald y Poppins
- Animaciones suaves y transiciones CSS3

### 6.2 Componentes Interactivos

- **Selectores de período:** Filtrado temporal de datos
- **Mapas interactivos:** Visualización geoespacial con zoom y panning
- **Gráficos dinámicos:** Charting reactivo con Plotly
- **Paneles de control:** Configuración de parámetros en tiempo real
- **Descargas:** Exportación de datos procesados

---

## 7. API y Endpoints

### 7.1 Configuración de Puertos

| Servicio | Puerto Interno | Puerto Externo | Protocolo |
|----------|----------------|----------------|-----------|
| Bosques Riparios | 8000 | 8001 | HTTP |
| Huella Humana | 8000 | 8002 | HTTP |

### 7.2 Variables de Entorno

Todos los servicios comparten configuración de Firebase mediante:
- `PYTHONUNBUFFERED=1`: Streaming de logs
- `FIREBASE_*`: Credenciales de autenticación y bases de datos

---

## 8. Mantenimiento y Actualizaciones

### 8.1 Actualización de Datos

Los datos se obtienen directamente desde Firebase Storage. Para actualizar:

1. Subir nuevos CSV a las rutas correspondientes en Firebase Storage
2. Las aplicaciones cargarán automáticamente los datos en el siguiente acceso

### 8.2 Monitoreo

```bash
# Verificar salud de servicios
docker-compose ps

# Limpiar recursos
docker-compose down -v

# Reconstruir sin caché
docker-compose build --no-cache
```

### 8.3 Troubleshooting

**Problema:** Error de conexión a Firebase
- **Solución:** Verificar variables de entorno en `.env`

**Problema:** Puerto ya en uso
- **Solución:** Modificar puertos en `docker-compose.yml`

**Problema:** Datos no se cargan
- **Solución:** Verificar rutas en Firebase Storage y permisos de acceso

---

## 9. Contribuciones y Licencia

Este proyecto está diseñado para colaboración científica. Las contribuciones deben incluir:
- Documentación de cambios
- Pruebas de funcionalidad
- Actualización de documentación relevante

**Licencia:** Verificar LICENSE.md para detalles específicos

---

## 10. Disponibilidad de Código

All dashboard and frontend code (Python/Shiny/React) is available at **https://github.com/USER/REPO** and archived at **https://doi.org/10.5281/**

---

## 11. Referencias Bibliográficas

- Shiny for Python Documentation. (https://shiny.posit.co/py/)
- Plotly Python Documentation. (https://plotly.com/python/)
- Firebase Documentation. (https://firebase.google.com/docs)
- ipyleaflet: Interactive Maps for Jupyter. (https://ipyleaflet.readthedocs.io/)

---

## 12. Contacto y Soporte

Para consultas técnicas y soporte:
- Issues: Reportar en el repositorio de GitHub
- Email: [asalmeida4@espe.edu.ec]
- Institución: [Universidad de las Fuerzas Armadas ESPE]

---

**Fecha de última actualización:** Octubre 2025  
**Versión del documento:** 1.0  
**Versión de código:** 1.0.0

---

## Apéndice: Dependencias de Python

### Dependencias Principales

```
python==3.13
shiny>=1.0.0
pandas>=2.0.0
plotly>=5.0.0
ipyleaflet>=0.17.0
ipywidgets>=8.0.0
shinywidgets>=0.3.0
faicons>=0.4.0
requests>=2.31.0
python-dotenv>=1.0.0
firebase-admin>=6.0.0 (opcional)
```

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

---

*Este README ha sido preparado para cumplir con los estándares de publicación en repositorios de SNL EMAS, asegurando reproducibilidad, trazabilidad y accesibilidad de la investigación.*
