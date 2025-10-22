from shiny import App, ui, render, reactive
import pandas as pd
from shinywidgets import output_widget, register_widget, render_widget
import ipyleaflet as L
from ipywidgets import HTML
import os
import base64
from dotenv import load_dotenv
from io import BytesIO
import requests
from faicons import icon_svg
from ipywidgets import Layout
import plotly.express as px

#Cargar variables de entorno
load_dotenv()

# Firebase configuration
class FirebaseStorage:
    def __init__(self, config, token=None):
        self.base_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/"
        self.token = token

    def get_image_url(self, image_path):
        encoded_path = image_path.replace('/', '%2F')
        token_param = f"&token={self.token}" if self.token else ""
        return f"{self.base_url}{encoded_path}?alt=media{token_param}"
    
    def get_image_data(self, image_path):
        """
        Fetch image data from Firebase Storage
        """
        url = self.get_image_url(image_path)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Error fetching image: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception in get_image_data: {e}")
            return None

# Initialize Firebase Storage
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}
firebase_storage = FirebaseStorage(firebase_config)

# Load CSV data from Firebase Storage
csv_path = "MapasPNG/HH_predeterminado.csv"
csv_url = firebase_storage.get_image_url(csv_path)
data = pd.read_csv(csv_url)

# Extraer categorías y años
categorias = data['txt_rango'].unique().tolist()
years = data['year'].unique().tolist()

# Load data
#data = pd.read_csv("MapasPNG/HH_predeterminado.csv")
#categorias = data['txt_rango'].unique().tolist()
#years = data['year'].unique().tolist()


# UI - All in one dashboard
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
            /* ESTILOS GENERALES EMBEBIDOS */
            @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');
            :root {
                --primary-lime: #C7F808;
                --dark-blue: #1D2331;
                --lime-hover: #B8E907;
                --light-background: #F8FFFE;
                --card-background: #FFFFFF;
                --text-primary: #1D2331;
                --text-secondary: #546E7A;
                --border-color: #E8F5E9;
                --shadow-light: rgba(199, 248, 8, 0.1);
                --shadow-medium: rgba(29, 35, 49, 0.08);
            }
            
            body {
                font-family: 'Poppins', sans-serif;
                background-color: var(--light-background);
                color: var(--text-primary);
                margin: 0;
                padding: 0;
            }
            
            /* CONTENEDOR PRINCIPAL */
            .container-fluid {
                padding: 20px !important;
                background-color: transparent;
            }
            
            /* TARJETAS */
            .card {
                border-radius: 12px;
                border: 1px solid rgba(199, 248, 8, 0.2);
                box-shadow: 0 4px 20px var(--shadow-medium);
                transition: all 0.3s ease;
                overflow: hidden;
                background: var(--card-background);
            }
            
            .card:hover {
                box-shadow: 0 8px 30px rgba(29, 35, 49, 0.12);
                transform: translateY(-3px);
                border-color: rgba(199, 248, 8, 0.4);
            }
            
            .card-header {
                background: linear-gradient(135deg, var(--primary-lime) 0%, #A8D404 100%);
                color: var(--dark-blue);
                font-weight: 700;
                border-bottom: none;
                padding: 18px 25px;
                font-size: 1.1em;
                font-family: 'Oswald', sans-serif;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .card-header i {
                margin-right: 10px;
                font-size: 1.2em;
            }
            
            /* PANEL DE CONTROL */
            .control-panel {
                padding: 25px;
                background-color: var(--card-background);
                border-radius: 12px;
                border: 1px solid rgba(199, 248, 8, 0.2);
                box-shadow: 0 4px 20px var(--shadow-medium);
                height: fit-content;
            }
            
            .control-panel h4 {
                color: var(--dark-blue);
                font-family: 'Oswald', sans-serif;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid var(--primary-lime);
            }
            
            /* BOTONES */
            .btn-primary {
                background: linear-gradient(135deg, var(--primary-lime) 0%, var(--lime-hover) 100%);
                border: none;
                color: var(--dark-blue);
                font-weight: 700;
                font-family: 'Oswald', sans-serif;
                letter-spacing: 0.5px;
                padding: 12px 20px;
                box-shadow: 0 4px 15px var(--shadow-light);
                transition: all 0.3s ease;
                text-transform: uppercase;
            }
            
            .btn-primary:hover {
                background: linear-gradient(135deg, var(--lime-hover) 0%, var(--primary-lime) 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(199, 248, 8, 0.3);
                color: var(--dark-blue);
            }
            
            .btn-success {
                background: linear-gradient(135deg, var(--dark-blue) 0%, #2A3441 100%);
                border: none;
                color: var(--primary-lime);
                font-weight: 700;
                font-family: 'Oswald', sans-serif;
                letter-spacing: 0.5px;
                padding: 12px 20px;
                box-shadow: 0 4px 15px rgba(29, 35, 49, 0.2);
                transition: all 0.3s ease;
                text-transform: uppercase;
            }
            
            .btn-success:hover {
                background: linear-gradient(135deg, #2A3441 0%, var(--dark-blue) 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(29, 35, 49, 0.3);
                color: var(--primary-lime);
            }
            
            /* ESTADÍSTICAS */
            .stats-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                gap: 20px;
                margin-bottom: 25px;
            }

            .stat-item {
                flex: 1;
                min-width: 200px;
                background: var(--card-background);
                padding: 25px 20px;
                border-radius: 12px;
                border: 1px solid rgba(199, 248, 8, 0.2);
                box-shadow: 0 4px 20px var(--shadow-medium);
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                transition: all 0.3s ease;
            }

            .stat-item:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 30px rgba(29, 35, 49, 0.15);
                border-color: rgba(199, 248, 8, 0.4);
            }

            .stat-item.primary {
                background: linear-gradient(135deg, #ffffff, rgba(199, 248, 8, 0.05));
                border-left: 4px solid var(--primary-lime);
            }

            .stat-item.secondary {
                background: linear-gradient(135deg, #ffffff, rgba(29, 35, 49, 0.03));
                border-left: 4px solid var(--dark-blue);
            }
            
            .stat-item.blue {
                background: linear-gradient(135deg, #ffffff, rgba(199, 248, 8, 0.05));
                border-left: 4px solid var(--primary-lime);
            }

            .stat-item.indigo {
                background: linear-gradient(135deg, #ffffff, rgba(29, 35, 49, 0.03));
                border-left: 4px solid var(--dark-blue);
            }

            .stat-item.green {
                background: linear-gradient(135deg, #ffffff, rgba(199, 248, 8, 0.05));
                border-left: 4px solid var(--primary-lime);
            }

            .stat-item.orange {
                background: linear-gradient(135deg, #ffffff, rgba(29, 35, 49, 0.03));
                border-left: 4px solid var(--dark-blue);
            }

            .stat-item.red {
                background: linear-gradient(135deg, #ffffff, rgba(199, 248, 8, 0.05));
                border-left: 4px solid var(--primary-lime);
            }

            .stat-label {
                font-size: 0.9rem;
                color: var(--text-secondary);
                margin-bottom: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-family: 'Oswald', sans-serif;
            }

            .stat-value {
                font-size: 1.8rem;
                font-weight: 700;
                color: var(--dark-blue);
                display: flex;
                align-items: center;
                margin-top: 5px;
                font-family: 'Oswald', sans-serif;
            }

            .stat-icon {
                position: absolute;
                top: 50%;
                right: 20px;
                transform: translateY(-50%);
                color: rgba(199, 248, 8, 0.1);
                font-size: 3rem;
                transition: all 0.3s ease;
            }
            
            /* SELECTORES */
            .selectize-input {
                border-radius: 8px !important;
                border: 2px solid rgba(199, 248, 8, 0.3) !important;
                padding: 12px !important;
                font-family: 'Poppins', sans-serif !important;
                transition: all 0.3s ease !important;
            }
            
            .selectize-input:focus {
                border-color: var(--primary-lime) !important;
                box-shadow: 0 0 0 3px rgba(199, 248, 8, 0.2) !important;
            }
            
            /* LABELS MEJORADOS */
            .form-label {
                color: var(--dark-blue);
                font-weight: 600;
                font-family: 'Oswald', sans-serif;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 8px;
                font-size: 0.9rem;
            }
            
            /* TABLA DE DATOS MEJORADA */
            .data-grid {
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 20px var(--shadow-medium);
                background: var(--card-background);
                border: 1px solid rgba(199, 248, 8, 0.2);
            }
            
            .data-grid th {
                background: linear-gradient(135deg, var(--primary-lime) 0%, #A8D404 100%) !important;
                color: var(--dark-blue) !important;
                font-weight: 700 !important;
                padding: 18px !important;
                text-align: center !important;
                font-size: 0.95rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
                border-bottom: none !important;
                font-family: 'Oswald', sans-serif !important;
            }
            
            .data-grid td {
                padding: 15px !important;
                text-align: center !important;
                border-bottom: 1px solid rgba(199, 248, 8, 0.1) !important;
                font-size: 0.9rem !important;
                color: var(--text-primary) !important;
                transition: all 0.2s ease !important;
                font-family: 'Poppins', sans-serif !important;
            }
            
            .data-grid tr:hover td {
                background-color: rgba(199, 248, 8, 0.05) !important;
                color: var(--dark-blue) !important;
            }
            
            /* Estilo para números en la tabla */
            .data-grid td:nth-child(2),
            .data-grid td:nth-child(3),
            .data-grid td:nth-child(4) {
                font-family: 'Roboto Mono', monospace !important;
                font-weight: 500 !important;
            }
            
            /* Estilo para el porcentaje */
            .data-grid td:nth-child(4) {
                color: var(--dark-blue) !important;
                font-weight: 700 !important;
            }
            
            /* Estilo para el año */
            .data-grid td:nth-child(1) {
                font-weight: 600 !important;
                color: var(--dark-blue) !important;
                font-family: 'Oswald', sans-serif !important;
            }
            
            /* Contenedor de la tabla */
            .card-body {
                padding: 25px !important;
            }
            
            /* Scrollbar personalizado */
            .data-grid::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            .data-grid::-webkit-scrollbar-track {
                background: rgba(199, 248, 8, 0.1);
                border-radius: 4px;
            }
            
            .data-grid::-webkit-scrollbar-thumb {
                background: var(--primary-lime);
                border-radius: 4px;
            }
            
            .data-grid::-webkit-scrollbar-thumb:hover {
                background: var(--lime-hover);
            }
            
            /* INFORMACIÓN PANEL */
            .info-panel {
                background: linear-gradient(135deg, rgba(199, 248, 8, 0.05), rgba(29, 35, 49, 0.02));
                border: 1px solid rgba(199, 248, 8, 0.2);
                border-radius: 12px;
                padding: 20px;
                margin-top: 20px;
            }
            
            .info-panel h5 {
                color: var(--dark-blue);
                font-family: 'Oswald', sans-serif;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 15px;
            }
            
            .info-panel p, .info-panel li {
                color: var(--text-secondary);
                font-size: 0.9rem;
                line-height: 1.6;
            }
            
            .info-panel ul {
                padding-left: 20px;
            }
            
            /* RESPONSIVE */
            @media (max-width: 768px) {
                .stats-container {
                    flex-direction: column;
                }
                
                .stat-item {
                    min-width: 100%;
                }
                
                .container-fluid {
                    padding: 15px !important;
                }
            }
        """),
        ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"),
    ),
    ui.row(
        # Left column - Controls
        ui.column(
            3,
            ui.div(
                ui.h4("Panel de Control", class_="mb-3"),
                ui.card(
                    ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-map"), " Controles del Mapa")),
                    ui.card_body(
                        ui.div(
                            ui.tags.div(ui.tags.i(class_="fas fa-filter"), " Año:", class_="form-label mb-2"),
                            ui.input_select("year", "", choices=years, width="100%"),
                            ui.tags.div(style="margin-bottom: 15px"),
                            ui.output_text_verbatim("diagnostico"),
                            ui.tags.div(style="margin-bottom: 15px"),
                            ui.tags.div(ui.tags.i(class_="fas fa-adjust"), " Opacidad:", class_="form-label mb-2"),
                            ui.input_slider("opacidad", "", min=0, max=1, value=0.8, step=0.1),
                        )
                    )
                ),
                ui.card(
                    ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-filter"), " Filtros")),
                    ui.card_body(
                        ui.tags.div(ui.tags.i(class_="fas fa-tags"), " Categorías:", class_="form-label mb-2"),
                        ui.input_selectize("categorias", "", 
                                         choices=categorias, 
                                         selected=[categorias[0]], 
                                         multiple=True,
                                         width="100%"),
                        ui.input_action_button("aplicar_filtro", 
                                              ui.tags.div(ui.tags.i(class_="fas fa-check"), " Aplicar Filtros"), 
                                              class_="btn-primary w-100"),
                        ui.tags.hr(),
                        ui.tags.div(ui.tags.i(class_="fas fa-table"), " Vista de Tabla:", class_="form-label mb-2"),
                        ui.input_switch("mostrar_todos_datos", "Mostrar todos los años y categorías", value=False),
                        # Botón para descargar datos
                        ui.download_button("descargar_datos", 
                                          ui.tags.div(ui.tags.i(class_="fas fa-download"), " Descargar Datos"), 
                                          class_="btn-success w-100")
                    )
                ),
                ui.div(
                    ui.h5("Acerca del Dashboard", class_="mb-3"),
                    ui.p("Este dashboard presenta información sobre el índice de Huella Humana en Ecuador, una herramienta para el monitoreo ambiental y la toma de decisiones."),
                    ui.p("El Índice de Huella Humana (HH) es una medida espacial que cuantifica el impacto acumulativo de las actividades humanas en los ecosistemas y la biodiversidad."),
                    ui.tags.p(ui.tags.strong("Clasificación por categorías:")),
                    ui.tags.ul(
                        ui.tags.li("Muy Baja: Áreas con mínima influencia humana"),
                        ui.tags.li("Baja: Áreas con influencia humana limitada"),
                        ui.tags.li("Media: Áreas con moderada influencia humana"),
                        ui.tags.li("Alta: Áreas con intensa influencia humana")
                    ),
                    class_="info-panel"
                ),
                class_="control-panel"
            )
        ),
        # Right column - Visualization
        ui.column(
            9,
            ui.div(
                ui.div(
                    ui.div(
                        # Stat card para Año
                        ui.div(
                            ui.div("Año", class_="stat-label"),
                            ui.div(ui.output_text("vb_anio"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-calendar"), class_="stat-icon"),
                            class_="stat-item primary"
                        ),
                        
                        # Stat card para Categoría
                        ui.div(
                            ui.div("Categoría", class_="stat-label"),
                            ui.div(ui.output_text("vb_categoria"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-map"), class_="stat-icon"),
                            class_="stat-item secondary"
                        ),
                        
                        # Stat card para Área
                        ui.div(
                            ui.div("Área (ha)", class_="stat-label"),
                            ui.div(ui.output_text("vb_area"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-chart-bar"), class_="stat-icon"),
                            class_="stat-item primary"
                        ),
                        
                        # Stat card para Porcentaje
                        ui.div(
                            ui.div("Porcentaje", class_="stat-label"),
                            ui.div(ui.output_text("vb_porcentaje"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-percent"), class_="stat-icon"),
                            class_="stat-item secondary"
                        ),
                        
                        class_="stats-container"
                    ),
                    class_="stat-card"
                ),
                class_="mb-4"
            ),
            ui.row(
                ui.column(
                    12,
                    ui.card(
                        ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-globe-americas"), " Mapa de Huella Humana")),
                        ui.card_body(
                            output_widget("map", height="600px"),
                        )
                    ),
                    class_="mb-4"
                )
            ),
            ui.row(
                ui.column(
                    6,
                    ui.card(
                        ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-chart-line"), " Evolución Temporal")),
                        ui.card_body(
                            output_widget("grafico_temporal", height="400px"),
                        )
                    ),
                ),
                ui.column(
                    6,
                    ui.card(
                        ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-table"), ui.output_text("titulo_tabla", inline=True))),
                        ui.card_body(
                            ui.div(
                                ui.output_data_frame("tabla"),
                                style="height:400px; overflow:auto;"
                            ),
                        )
                    ),
                )
            )
        )
    ),
    ui.tags.script(src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/js/all.min.js"),
    title="Huella Humana - Ecuador"
)

# Server logic - unchanged
def server(input, output, session):
    # Mapeo de categorías
    category_mapping = {
        "Muy baja": 1,
        "Baja": 2,
        "Media": 3,
        "Alta": 4
    }
    
    # Mapeo de colores
    color_mapping = {
        "Muy baja": "#228b22",
        "Baja": "#ffff00",
        "Media": "#ffa500",
        "Alta": "#ff0000"
    }
    
    # Estados reactivos
    filtered_data = reactive.Value(data)
    current_categories = reactive.Value([])
    map_obj = reactive.Value(None)
    layer_dict = reactive.Value({})
    legend_control = reactive.Value(None)
    
    # Método para calcular porcentajes por categoría y año
    def get_category_percentages(year):
        df_year = data[data['year'] == int(year)]
        if df_year.empty:
            return {cat: 0 for cat in category_mapping}
        
        total_area = df_year['area'].sum()
        percentages = {}
        for cat in category_mapping:
            cat_area = df_year[df_year['txt_rango'] == cat]['area'].sum()
            percentage = (cat_area / total_area * 100) if total_area > 0 else 0
            percentages[cat] = round(percentage, 2)
        return percentages
    
    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_anio():
        return str(input.year())

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_categoria():
        selected_year = str(input.year())
        # Load CSV data from Firebase Storage
        csv_path = "MapasPNG/HH_predeterminado.csv"
        csv_url = firebase_storage.get_image_url(csv_path)
        data = pd.read_csv(csv_url)
        data = data[data["year"] == int(selected_year)]

        if not data.empty:
            if selected_year == "2014":
                fila_max = data.loc[data["area"].idxmax()]
                return str(fila_max["txt_rango"])
            elif selected_year == "2016":
                fila_max = data.loc[data["area"].idxmax()]
                return str(fila_max["txt_rango"])
            elif selected_year == "2018":
                fila_max = data.loc[data["area"].idxmax()]
                return str(fila_max["txt_rango"])
            elif selected_year == "2020":
                fila_max = data.loc[data["area"].idxmax()]
                return str(fila_max["txt_rango"])
            elif selected_year == "2022":
                fila_max = data.loc[data["area"].idxmax()]
                return str(fila_max["txt_rango"])
        return "Sin datos"

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_area():
        selected_year = str(input.year())
        # Load CSV data from Firebase Storage
        csv_path = "MapasPNG/HH_predeterminado.csv"
        csv_url = firebase_storage.get_image_url(csv_path)
        data = pd.read_csv(csv_url)
        data = data[data["year"] == int(selected_year)]

        if not data.empty:
            if selected_year == "2014":
                fila_max = data.loc[data["area"].idxmax()]
                return str(round(fila_max["area"], 2))
            elif selected_year == "2016":
                fila_max = data.loc[data["area"].idxmax()]
                return str(round(fila_max["area"], 2))
            elif selected_year == "2018":
                fila_max = data.loc[data["area"].idxmax()]
                return str(round(fila_max["area"], 2))
            elif selected_year == "2020":
                fila_max = data.loc[data["area"].idxmax()]
                return str(round(fila_max["area"], 2))
            elif selected_year == "2022":
                fila_max = data.loc[data["area"].idxmax()]
                return str(round(fila_max["area"], 2))
        return "0.00"

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_porcentaje():
        selected_year = str(input.year())
        # Load CSV data from Firebase Storage
        csv_path = "MapasPNG/HH_predeterminado.csv"
        csv_url = firebase_storage.get_image_url(csv_path)
        data = pd.read_csv(csv_url)
        data = data[data["year"] == int(selected_year)]

        if not data.empty:
            if selected_year == "2014":
                fila_max = data.loc[data["area"].idxmax()]
                return f"{round(fila_max['percentage'], 2)}%"
            elif selected_year == "2016":
                fila_max = data.loc[data["area"].idxmax()]
                return f"{round(fila_max['percentage'], 2)}%"
            elif selected_year == "2018":
                fila_max = data.loc[data["area"].idxmax()]
                return f"{round(fila_max['percentage'], 2)}%"
            elif selected_year == "2020":
                fila_max = data.loc[data["area"].idxmax()]
                return f"{round(fila_max['percentage'], 2)}%"
            elif selected_year == "2022":
                fila_max = data.loc[data["area"].idxmax()]
                return f"{round(fila_max['percentage'], 2)}%"
        return "0.00%"
    
    # Inicialización del mapa
    @reactive.Effect
    def initialize_map():
        print("Inicializando mapa")
        m = L.Map(
            center=(-1.8, -78.5),
            zoom=7,
            scroll_wheel_zoom=True,
            layout=Layout(width="100%", height="600px")  # Cambia el tamaño aquí
        )
        m.add_layer(L.TileLayer(url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"))
        
        # Crear leyenda inicial
        year = str(input.year())
        percentages = get_category_percentages(year)
        legend_content = ""
        for cat in input.categorias():
            if cat in category_mapping:
                color = color_mapping[cat]
                percentage = percentages.get(cat, 0)
                legend_content += f'''
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                        <div style="width: 20px; height: 20px; background: {color}; border-radius: 50%; border: 1px solid rgba(0,0,0,0.2);"></div>
                        <span>{cat} ({percentage}%)</span>
                    </div>
                '''
        
        legend_html = HTML(f'''
            <div style="
                background: white;
                padding: 12px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                border: 1px solid rgba(0,0,0,0.05);
                max-width: 200px;
                font-family: 'Poppins', sans-serif;
            ">
                <h4 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px;">Leyenda HH ({year})</h4>
                <div style="display: flex; flex-direction: column;">
                    {legend_content}
                </div>
            </div>
        ''')
        legend_control = L.WidgetControl(widget=legend_html, position='bottomright')
        m.add_control(legend_control)
        
        map_obj.set(m)
        layer_dict.set({})
        register_widget("map", m)
        
        # Cargar capas para el año inicial
        load_layers_for_year(year)

    # Modificación de la función load_layers_for_year para usar la clase FirebaseStorage

    def load_layers_for_year(year):
        print(f"Cargando capas para el año {year}")
        m = map_obj.get()
        layers = layer_dict.get()

        if year not in layers:
            layers[year] = {}
            bounds = [[-5.01, -81.12], [1.45, -75.17]]  # Extensión geográfica de Ecuador
            
            # Cargar capa combinada
            firebase_path = f"MapasPNG/HH_predeterminado_{year}_cat_all.png"
            #firebase_path = f"https://firebasestorage.googleapis.com/v0/b/pry-tiendavino.appspot.com/o/MapasPNG%2FHH_predeterminado_{year}_cat_all.png?alt=media&token=da6b6902-ec4c-4c54-9ce3-5baaac52eb74"
            img_url = firebase_storage.get_image_url(firebase_path)
            
            if img_url:
                try:
                    image_layer = L.ImageOverlay(
                        url=img_url,
                        bounds=bounds,
                        opacity=1.0,
                        name=f"all_{year}"
                    )
                    layers[year]['all'] = image_layer
                    print(f"Capa 'todas' creada para el año {year}")
                except Exception as e:
                    print(f"Error cargando capa combinada para {year}: {str(e)}")
            
            # Cargar capas individuales
            for cat, cat_num in category_mapping.items():
                firebase_path = f"MapasPNG/HH_predeterminado_{year}_cat_{cat_num}.png"
                #firebase_path = f"https://firebasestorage.googleapis.com/v0/b/pry-tiendavino.appspot.com/o/MapasPNG%2FHH_predeterminado_{year}_cat_{cat_num}.png?alt=media&token=da6b6902-ec4c-4c54-9ce3-5baaac52eb74"
                img_url = firebase_storage.get_image_url(firebase_path)
                
                if img_url:
                    try:
                        image_layer = L.ImageOverlay(
                            url=img_url,
                            bounds=bounds,
                            opacity=0.8,
                            name=f"{cat}_{year}"
                        )
                        layers[year][cat] = image_layer
                        print(f"Capa '{cat}' creada para el año {year}")
                    except Exception as e:
                        print(f"Error cargando capa {cat} para {year}: {str(e)}")
        
        layer_dict.set(layers)
        return layers

    # Actualizar filtros y capas
    @reactive.Effect
    @reactive.event(input.aplicar_filtro)
    def actualizar_filtros():
        cats_validas = [c for c in input.categorias() if c in category_mapping]
        year = str(input.year())
        
        print(f"Actualizando filtros: Año={year}, Categorías={cats_validas}")
        current_categories.set(cats_validas)
        filtered_data.set(data[data['txt_rango'].isin(cats_validas)])
        
        layers = load_layers_for_year(year)
        m = map_obj.get()
        
        for layer in list(m.layers):
            if isinstance(layer, L.ImageOverlay):
                m.remove_layer(layer)
        
        if sorted(cats_validas) == sorted(categorias) and 'all' in layers[year]:
            layers[year]['all'].opacity = input.opacidad()
            m.add_layer(layers[year]['all'])
            print("Mostrando capa combinada")
        else:
            for cat in cats_validas:
                if cat in layers[year]:
                    layers[year][cat].opacity = input.opacidad()
                    m.add_layer(layers[year][cat])
                    print(f"Mostrando capa para categoría: {cat}")

    # Actualizar opacidad
    @reactive.Effect
    @reactive.event(input.opacidad)
    def actualizar_opacidad():
        m = map_obj.get()
        if m is None:
            return
        new_opacity = input.opacidad()
        for layer in m.layers:
            if isinstance(layer, L.ImageOverlay):
                layer.opacity = new_opacity
        print(f"Opacidad actualizada a {new_opacity}")

    # Gráfico temporal
    @output
    @render_widget
    def grafico_temporal():
        df = filtered_data.get()
        if df.empty:
            return px.scatter(title="Sin datos")
        
        df_grouped = df.groupby(['txt_rango', 'year'])['area'].sum().reset_index()
        color_discrete_map = {
            "Muy baja": "green",
            "Baja": "yellow",
            "Media": "orange",
            "Alta": "red"
        }
        
        fig = px.line(
            df_grouped,
            x="year",
            y="area",
            color="txt_rango",
            color_discrete_map=color_discrete_map,
            markers=True,
            title="Evolución Temporal de la Huella Humana",
            labels={"year": "Año", "area": "Área (km²)", "txt_rango": "Categoría"}
        )
        fig.update_traces(hovertemplate="<b>Año:</b> %{x}<br><b>Área:</b> %{y:.2f} km²<extra></extra>")
        fig.update_layout(hovermode="x unified", legend_title_text="Categorías", template="plotly_white", xaxis=dict(tickmode='linear', dtick=1))
        return fig    # Título dinámico para la tabla
    @output
    @render.text
    def titulo_tabla():
        if input.mostrar_todos_datos():
            return " Tabla Completa - Todos los Años y Categorías"
        else:
            return f" Tabla de Datos - Año {input.year()}"
    
    # Tabla de datos
    @output
    @render.data_frame
    def tabla():
        # Verificar si se debe mostrar todos los datos o solo los filtrados
        if input.mostrar_todos_datos():
            # Mostrar todos los datos sin filtrar
            df = data.copy()
        else:
            # Mostrar solo los datos del año seleccionado
            df = filtered_data.get()
            df = df[df['year'] == int(input.year())]
        
        # Calcular porcentajes por año
        result_data = []
        for year in df['year'].unique():
            df_year = df[df['year'] == year]
            total_area = df_year['area'].sum()
            
            for _, row in df_year.iterrows():
                percentage = (row['area'] / total_area * 100) if total_area > 0 else 0
                result_data.append({
                    'Año': int(row['year']),
                    'Categoría': row['txt_rango'],
                    'Área (km²)': round(row['area'], 2),
                    'Porcentaje (%)': round(percentage, 2)
                })
        
        # Crear DataFrame con los datos procesados
        df_display = pd.DataFrame(result_data)
        
        # Ordenar por año y luego por categoría
        category_order = ['Muy baja', 'Baja', 'Media', 'Alta']
        df_display['Categoria_orden'] = df_display['Categoría'].map({cat: i for i, cat in enumerate(category_order)})
        df_display = df_display.sort_values(['Año', 'Categoria_orden']).drop('Categoria_orden', axis=1)
        
        return render.DataGrid(
            df_display, 
            filters=False,  # Desactivar filtros integrados
            height="350px",
            width="100%"
        )
    
    # Diagnóstico
    @output
    @render.text
    def diagnostico():
        return f"Estado: Año {input.year()} | Categorías: {', '.join(current_categories.get())}"
      # Funcionalidad de descarga
    @session.download(filename="huella_humana_ecuador.csv")
    def descargar_datos():
        # Verificar si se debe descargar todos los datos o solo los filtrados
        if input.mostrar_todos_datos():
            # Descargar todos los datos
            df = data.copy()
        else:
            # Descargar solo los datos filtrados actuales
            df = filtered_data.get()
        
        # Calcular el porcentaje por categoría para cada año
        result_data = []
        for year in df['year'].unique():
            df_year = df[df['year'] == year]
            total_area = df_year['area'].sum()
            
            for _, row in df_year.iterrows():
                percentage = (row['area'] / total_area * 100) if total_area > 0 else 0
                result_data.append({
                    'Anio': int(row['year']),
                    'Categoria': row['txt_rango'],
                    'Area_km2': round(row['area'], 2),
                    'Porcentaje': round(percentage, 2)
                })
        
        # Crear DataFrame con los datos procesados
        result_df = pd.DataFrame(result_data)
        
        # Ordenar por año y luego por categoría
        category_order = ['Muy baja', 'Baja', 'Media', 'Alta']
        result_df['Categoria_orden'] = result_df['Categoria'].map({cat: i for i, cat in enumerate(category_order)})
        result_df = result_df.sort_values(['Anio', 'Categoria_orden']).drop('Categoria_orden', axis=1)
        
        # Crear un BytesIO buffer para guardar el CSV
        buffer = BytesIO()
        
        # Guardar los datos procesados en formato CSV
        result_df.to_csv(buffer, index=False, encoding='utf-8')
        
        # Mover el cursor al inicio del buffer
        buffer.seek(0)
        
        # Devolver el contenido del buffer
        return buffer

# Create app
app = App(app_ui, server)