# Environmental Indicators Dashboard: Riparian Forests and Human Footprint in Ecuador

## Executive Summary

This repository contains interactive dashboards for analyzing two critical environmental indicators for ecological monitoring in Ecuador: (1) **Riparian Forests (BR)** and (2) **Human Footprint (HH)**. Both applications implement modern data visualization and cloud computing technologies, enabling querying, analysis, and interpretation of geospatial data through responsive web interfaces.

---

## 1. Introduction

### 1.1 Environmental Context

Riparian forests constitute critical ecosystems that act as hydrological buffers and biological corridors. The Human Footprint, meanwhile, is an indicator that quantifies the intensity of anthropogenic impact on ecosystems. This project provides visualization and analysis tools to monitor the temporal and spatial evolution of both indicators across Ecuadorian territory.

### 1.2 Project Purpose

To facilitate access to environmental geospatial data through interactive dashboards that enable:
- Continuous monitoring of conservation indicators
- Analysis of temporal trends and spatial distribution
- Informed decision-making in environmental policy
- Scientific dissemination and environmental education

---

## 2. Technical Description

### 2.1 System Architecture

The project implements a containerized microservices architecture:

```
┌──────────────────────────────────────────────────────────────┐
│              Docker Compose Orchestrator                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐      ┌──────────────────────────┐  │
│  │  Riparian Forests    │      │    Human Footprint       │  │
│  │  (Dashboard BR)      │      │    (Dashboard HH)        │  │
│  │   Port: 8001         │      │     Port: 8002           │  │
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

### 2.2 Technology Stack

#### Backend
- **Python 3.13+**: Main programming language
- **Shiny for Python**: Reactive web framework for dashboards
- **Pandas**: Data processing and manipulation
- **Plotly**: Interactive data visualization
- **ipyleaflet**: Interactive maps based on Leaflet

#### Frontend
- **HTML5**: Web interface
- **CSS3**: Responsive design and animations
- **Chart.js**: Statistical graphics
- **Vanilla JavaScript**: Client-side interactivity

#### Infrastructure
- **Docker & Docker Compose**: Containerization and orchestration
- **Firebase Realtime Database**: Data storage
- **Firebase Storage**: File and CSV management
- **Firebase Authentication**: Access control

### 2.3 Main Modules

#### 2.3.1 Riparian Forests Dashboard (`br/br.py`)

**Features:**
- Data loading from Firebase Storage (compiled statistics CSV)
- Analysis at 30m and 100m buffer zones
- Temporal visualization of trends (pixels, proportions, percentages)
- Integration with georeferenced interactive maps
- Processed data export

**Processed Data:**
- `pixels_30m`: Total riparian pixels at 30m
- `pixels_bosque_30m`: Riparian forest pixels at 30m
- `proporcion_30m`: Forest coverage proportion at 30m
- `pixels_100m`: Total riparian pixels at 100m
- `pixels_bosque_100m`: Riparian forest pixels at 100m
- `proporcion_100m`: Forest coverage proportion at 100m

#### 2.3.2 Human Footprint Dashboard (`hh/hh.py`)

**Features:**
- Loading categorized data from Firebase Storage
- Classification by ranges of human impact intensity
- Temporal analysis of category changes
- Cartographic visualization of anthropogenic impact
- Interactive interface with dynamic filters

**Human Footprint Categories:**
- Based on IUCN classification of impact intensity
- Multi-temporal analysis from 1993-present

### 2.4 Firebase Integration

Both applications use Firebase as the data backend:

```python
# Configuration example
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

## 3. Installation and Configuration

### 3.1 Prerequisites

- Docker and Docker Compose (v3.8+)
- Python 3.13+ (for local development without Docker)
- Firebase environment variables configured
- Access to datasets in Firebase Storage

### 3.2 Environment Configuration

Create `.env` file in project root:

```bash
FIREBASE_API_KEY=<your_api_key>
FIREBASE_AUTH_DOMAIN=<your_auth_domain>
FIREBASE_DATABASE_URL=<your_database_url>
FIREBASE_PROJECT_ID=<your_project_id>
FIREBASE_STORAGE_BUCKET=<your_storage_bucket>
FIREBASE_MESSAGING_SENDER_ID=<your_messaging_sender_id>
FIREBASE_APP_ID=<your_app_id>
```

### 3.3 Deployment with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f bosques-riparios    # BR Dashboard (port 8001)
docker-compose logs -f huella-humana       # HH Dashboard (port 8002)
```

**Access URLs:**
- Riparian Forests Dashboard: `http://localhost:8001`
- Human Footprint Dashboard: `http://localhost:8002`
- Integration Portal: `http://localhost` (index.html)

### 3.4 Local Installation (Development)

```bash
# Clone repository
git clone https://github.com/USER/REPO
cd Indicadores

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run BR dashboard
cd br && python br.py

# Run HH dashboard (in another terminal)
cd hh && python hh.py
```

---

## 4. Repository Structure

```
Indicadores/
├── README.md                           # This file
├── docker-compose.yml                  # Services configuration
├── index.html                          # Integration portal
├── br/                                 # Riparian Forests Dashboard
│   ├── br.py                          # Main application
│   ├── Dockerfile                      # Container configuration
│   └── __pycache__/
├── hh/                                 # Human Footprint Dashboard
│   ├── hh.py                          # Main application
│   ├── Dockerfile                      # Container configuration
│   └── __pycache__/
└── __pycache__/
```

---

## 5. Methodology and Datasets

### 5.1 Riparian Forest Data

**Source:** Processing through remote sensing analysis
**Spatial Resolution:** 30m and 100m
**Period:** Multiple years (configurable)
**Format:** Compiled CSV hosted in Firebase Storage
**Path:** `MapasBosques/estadisticas_bosque_riparios_compiladas.csv`

**Main Variables:**
- Forest coverage in riparian zones
- Proportion of riparian forest relative to total riparian zone
- Comparative analysis between protection buffers

### 5.2 Human Footprint Data

**Source:** Calculation through anthropogenic pressure index
**Spatial Resolution:** Variable according to analysis
**Period:** 1993-present
**Format:** Categorized CSV
**Path:** `MapasPNG/HH_predeterminado.csv`

**Classification:**
- Impact intensity categories (txt_rango)
- Years of analysis (year)
- Spatial distribution statistics

---

## 6. Interface Features

### 6.1 Responsive Design

Both dashboards implement:
- Color palette: Lime (#C7F808) and Dark Blue (#1D2331)
- Responsive grid layout
- Custom fonts: Oswald and Poppins
- Smooth animations and CSS3 transitions

### 6.2 Interactive Components

- **Period Selectors:** Temporal data filtering
- **Interactive Maps:** Geospatial visualization with zoom and panning
- **Dynamic Graphs:** Reactive charting with Plotly
- **Control Panels:** Real-time parameter configuration
- **Downloads:** Processed data export

---

## 7. API and Endpoints

### 7.1 Port Configuration

| Service | Internal Port | External Port | Protocol |
|---------|---------------|---------------|----------|
| Riparian Forests | 8000 | 8001 | HTTP |
| Human Footprint | 8000 | 8002 | HTTP |

### 7.2 Environment Variables

All services share Firebase configuration through:
- `PYTHONUNBUFFERED=1`: Log streaming
- `FIREBASE_*`: Authentication and database credentials

---

## 8. Maintenance and Updates

### 8.1 Data Updates

Data is obtained directly from Firebase Storage. To update:

1. Upload new CSVs to corresponding paths in Firebase Storage
2. Applications will automatically load the data on next access

### 8.2 Monitoring

```bash
# Check service health
docker-compose ps

# Clean resources
docker-compose down -v

# Rebuild without cache
docker-compose build --no-cache
```

### 8.3 Troubleshooting

**Issue:** Firebase connection error
- **Solution:** Verify environment variables in `.env`

**Issue:** Port already in use
- **Solution:** Modify ports in `docker-compose.yml`

**Issue:** Data not loading
- **Solution:** Verify paths in Firebase Storage and access permissions

---

## 9. Contributions and License

This project is designed for scientific collaboration. Contributions should include:
- Documentation of changes
- Functionality tests
- Update of relevant documentation

**License:** See LICENSE.md for specific details

---

## 10. Code Availability

All dashboard and frontend code (Python/Shiny/React) is available at **https://github.com/andresalmeida/indigeo-dashboards-code.git** and archived at **https://doi.org/10.5281/**

---

## 11. Bibliographic References

- Shiny for Python Documentation. (https://shiny.posit.co/py/)
- Plotly Python Documentation. (https://plotly.com/python/)
- Firebase Documentation. (https://firebase.google.com/docs)
- ipyleaflet: Interactive Maps for Jupyter. (https://ipyleaflet.readthedocs.io/)

---

## 12. Contact and Support

For technical inquiries and support:
- Issues: Report in GitHub repository
- Email: [asalmeida4@espe.edu.ec]
- Institution: [Universidad de las Fuerzas Armadas ESPE]

---

**Last Update:** October 2025  
**Document Version:** 1.0  
**Code Version:** 1.0.0

---

## Appendix: Python Dependencies

### Main Dependencies

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
firebase-admin>=6.0.0 (optional)
```

### Installation of Dependencies

```bash
pip install -r requirements.txt
```

---

*This README has been prepared to meet the publishing standards for SNL EMAS repositories, ensuring reproducibility, traceability, and accessibility of the research.*
