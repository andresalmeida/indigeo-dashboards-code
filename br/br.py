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

# Obtener URL del CSV
firebase_path = "MapasBosques/estadisticas_bosque_riparios_compiladas.csv"
csv_url = firebase_storage.get_image_url(firebase_path)

# Leer y procesar el CSV
data = pd.read_csv(csv_url, sep=';', decimal=',')
data = data.rename(columns={
    'fecha': 'year',
    'pix_rip30m': 'pixels_30m',
    'pix_bosrip30m': 'pixels_bosque_30m',
    'propbosrip30m': 'proporcion_30m',
    'porcbosrip30m': 'porcentaje_30m',
    'pix_rip10m': 'pixels_100m',
    'pix_bosrip100m': 'pixels_bosque_100m',
    'propbosrip100m': 'proporcion_100m',
    'porcbosrip100m': 'porcentaje_100m'
})

# Variables para UI o análisis
years = data['year'].unique().tolist()
buffer_sizes = ['30m', '100m']

# UI - Dashboard embebido
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
                            ui.tags.div(style="margin-bottom: 20px"),
                            ui.tags.div(ui.tags.i(class_="fas fa-ruler"), " Buffer:", class_="form-label mb-2"),
                            ui.input_select("buffer_size", "", choices=buffer_sizes, width="100%"),
                            ui.tags.div(style="margin-bottom: 20px"),
                            ui.input_action_button("aplicar_filtro", 
                                                  ui.tags.div(ui.tags.i(class_="fas fa-check"), " Aplicar Filtros"), 
                                                  class_="btn-primary w-100"),
                            ui.tags.div(style="margin-bottom: 15px"),
                            ui.download_button("descargar_datos", 
                                              ui.tags.div(ui.tags.i(class_="fas fa-download"), " Descargar Datos"), 
                                              class_="btn-success w-100")
                        )
                    )
                ),
                ui.div(
                    ui.h5("Acerca del Dashboard", class_="mb-3"),
                    ui.p("Dashboard de monitoreo de bosques riparios en Ecuador, alineado con los Objetivos de Desarrollo Sostenible (ODS 15)."),
                    ui.p("Los bosques riparios son ecosistemas forestales ubicados en las riberas de ríos y quebradas, fundamentales para la conservación de la biodiversidad."),
                    ui.tags.p(ui.tags.strong("Características:")),
                    ui.tags.ul(
                        ui.tags.li("Visualización temporal (1990-2020)"),
                        ui.tags.li("Análisis de buffers: 30m y 100m"),
                        ui.tags.li("Estadísticas de cobertura forestal"),
                        ui.tags.li("Datos descargables en CSV")
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
                        # Stat card para Último Valor
                        ui.div(
                            ui.div("Último Valor", class_="stat-label"),
                            ui.div(ui.output_text("vb_ultimo_valor"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-chart-line"), class_="stat-icon"),
                            class_="stat-item primary"
                        ),
                        
                        # Stat card para Promedio Histórico
                        ui.div(
                            ui.div("Promedio Histórico", class_="stat-label"),
                            ui.div(ui.output_text("vb_promedio"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-calculator"), class_="stat-icon"),
                            class_="stat-item secondary"
                        ),
                        
                        # Stat card para Valor Máximo
                        ui.div(
                            ui.div("Valor Máximo", class_="stat-label"),
                            ui.div(ui.output_text("vb_maximo"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-arrow-up"), class_="stat-icon"),
                            class_="stat-item primary"
                        ),
                        
                        # Stat card para Valor Mínimo
                        ui.div(
                            ui.div("Valor Mínimo", class_="stat-label"),
                            ui.div(ui.output_text("vb_minimo"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-arrow-down"), class_="stat-icon"),
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
                        ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-tree"), " Mapa de Bosques Riparios")),
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
                        ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-table"), " Tabla de Datos")),
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
    title="Dashboard Bosques Riparios"
)

def server(input, output, session):
    # Estados reactivos
    filtered_data = reactive.Value(data)
    map_obj = reactive.Value(None)
    layer_dict = reactive.Value({})
    current_year = reactive.Value(None)
    current_buffer = reactive.Value(None)
    
    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_anio():
        current_year.set(input.year())
        return str(input.year())

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_buffer():
        current_buffer.set(input.buffer_size())
        return f"{input.buffer_size()}"

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_porcentaje():
        year = int(input.year())
        buffer_size = input.buffer_size()
        df_year = data[data['year'] == year]
        
        if not df_year.empty:
            if buffer_size == '30m':
                return f"{df_year['porcentaje_30m'].iloc[0]:.2f}%"
            else:
                return f"{df_year['porcentaje_100m'].iloc[0]:.2f}%"
        return "0.00%"
    
    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_ultimo_valor():
        buffer_size = input.buffer_size()
        df = data.copy()
        
        if buffer_size == '30m':
            col = 'porcentaje_30m'
        else:
            col = 'porcentaje_100m'
            
        ultimo_anio = df['year'].max()
        ultimo_valor = df[df['year'] == ultimo_anio][col].iloc[0]
        return f"{ultimo_valor:.2f}% ({ultimo_anio})"

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_promedio():
        buffer_size = input.buffer_size()
        df = data.copy()
        
        if buffer_size == '30m':
            col = 'porcentaje_30m'
        else:
            col = 'porcentaje_100m'
            
        promedio = df[col].mean()
        return f"{promedio:.2f}%"

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_maximo():
        buffer_size = input.buffer_size()
        df = data.copy()
        
        if buffer_size == '30m':
            col = 'porcentaje_30m'
        else:
            col = 'porcentaje_100m'
            
        max_valor = df[col].max()
        max_anio = df[df[col] == max_valor]['year'].iloc[0]
        return f"{max_valor:.2f}% ({max_anio})"

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_minimo():
        buffer_size = input.buffer_size()
        df = data.copy()
        
        if buffer_size == '30m':
            col = 'porcentaje_30m'
        else:
            col = 'porcentaje_100m'
            
        min_valor = df[col].min()
        min_anio = df[df[col] == min_valor]['year'].iloc[0]
        return f"{min_valor:.2f}% ({min_anio})"

    # Inicialización del mapa
    @reactive.Effect
    def initialize_map():
        m = L.Map(
            center=(-1.8, -78.5),
            zoom=7,
            scroll_wheel_zoom=True,
            layout=Layout(width="100%", height="600px")
        )
        m.add_layer(L.TileLayer(url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"))
        
        map_obj.set(m)
        layer_dict.set({})
        register_widget("map", m)
        
        # Cargar capa inicial
        load_layer_for_year(input.year(), input.buffer_size())

    def load_layer_for_year(year, buffer_size):
        print(f"Cargando capa para el año {year} y buffer {buffer_size}")
        m = map_obj.get()
        layers = layer_dict.get()
        
        key = f"{year}_{buffer_size}"
        if key not in layers:
            bounds = [[-5.01, -81.12], [1.45, -75.17]]  # Extensión geográfica de Ecuador
            
            # Construir el nombre del archivo
            file_name = f"bosque_ripario{buffer_size}_{year}.png"
            firebase_path = f"MapasBosques/{file_name}"
            img_url = firebase_storage.get_image_url(firebase_path)
            
            if img_url:
                try:
                    image_layer = L.ImageOverlay(
                        url=img_url,
                        bounds=bounds,
                        opacity=0.8,
                        name=f"bosque_{year}_{buffer_size}"
                    )
                    layers[key] = image_layer
                    print(f"Capa creada para {year} {buffer_size}")
                except Exception as e:
                    print(f"Error cargando capa para {year} {buffer_size}: {str(e)}")
        
        layer_dict.set(layers)
        return layers

    # Actualizar capa
    @reactive.Effect
    @reactive.event(input.aplicar_filtro)
    def actualizar_capa():
        year = input.year()
        buffer_size = input.buffer_size()
        
        m = map_obj.get()
        if m is None:
            return
            
        # Remover capas existentes
        for layer in list(m.layers):
            if isinstance(layer, L.ImageOverlay):
                m.remove_layer(layer)
        
        # Cargar nueva capa
        layers = load_layer_for_year(year, buffer_size)
        key = f"{year}_{buffer_size}"
        if key in layers:
            layers[key].opacity = 0.8
            m.add_layer(layers[key])


    # Gráfico temporal
    @output
    @render_widget
    def grafico_temporal():
        buffer_size = input.buffer_size()
        df = data.copy()
        
        if buffer_size == '30m':
            y_col = 'porcentaje_30m'
        else:
            y_col = 'porcentaje_100m'
        
        fig = px.line(
            df,
            x="year",
            y=y_col,
            markers=True,
            title=f"Evolución Temporal de Bosques Riparios ({buffer_size})",
            labels={"year": "Año", y_col: "Porcentaje (%)"}
        )
        
        # Actualizar el estilo del gráfico
        fig.update_traces(
            line=dict(color='#C7F808', width=3),
            marker=dict(size=8, color='#C7F808', line=dict(width=2, color='#1D2331'))
        )
        
        fig.update_layout(
            hovermode="x unified",
            template="plotly_white",
            plot_bgcolor='white',
            paper_bgcolor='white',
            title=dict(
                font=dict(size=20, color='#1D2331', family='Oswald'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                tickmode='array',
                tickvals=df['year'].unique(),
                ticktext=[str(year) for year in df['year'].unique()],
                gridcolor='rgba(199, 248, 8, 0.1)',
                zerolinecolor='rgba(199, 248, 8, 0.1)',
                title=dict(font=dict(color='#1D2331', family='Poppins'))
            ),
            yaxis=dict(
                title=dict(
                    text="Porcentaje (%)",
                    font=dict(size=14, color='#1D2331', family='Poppins')
                ),
                gridcolor='rgba(199, 248, 8, 0.1)',
                zerolinecolor='rgba(199, 248, 8, 0.1)'
            ),
            margin=dict(t=50, l=50, r=50, b=50),
            showlegend=False
        )
        
        # Agregar anotaciones para valores máximos y mínimos
        max_val = df[y_col].max()
        min_val = df[y_col].min()
        max_year = df[df[y_col] == max_val]['year'].iloc[0]
        min_year = df[df[y_col] == min_val]['year'].iloc[0]
        
        fig.add_annotation(
            x=max_year,
            y=max_val,
            text=f"Máximo: {max_val:.1f}%",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#C7F808",
            ax=0,
            ay=-40,
            font=dict(size=12, color="#1D2331", family="Oswald")
        )
        
        fig.add_annotation(
            x=min_year,
            y=min_val,
            text=f"Mínimo: {min_val:.1f}%",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#C7F808",
            ax=0,
            ay=40,
            font=dict(size=12, color="#1D2331", family="Oswald")
        )
        
        return fig

    # Tabla de datos
    @output
    @render.data_frame
    def tabla():
        buffer_size = input.buffer_size()
        df = data.copy()
        
        if buffer_size == '30m':
            columns = ['year', 'pixels_30m', 'pixels_bosque_30m', 'porcentaje_30m']
            rename_dict = {
                'year': 'Año',
                'pixels_30m': 'Píxeles Totales',
                'pixels_bosque_30m': 'Píxeles Bosque',
                'porcentaje_30m': 'Porcentaje (%)'
            }
        else:
            columns = ['year', 'pixels_100m', 'pixels_bosque_100m', 'porcentaje_100m']
            rename_dict = {
                'year': 'Año',
                'pixels_100m': 'Píxeles Totales',
                'pixels_bosque_100m': 'Píxeles Bosque',
                'porcentaje_100m': 'Porcentaje (%)'
            }
        
        df_display = df[columns].rename(columns=rename_dict)
        df_display['Porcentaje (%)'] = df_display['Porcentaje (%)'].round(2)
        df_display['Píxeles Totales'] = df_display['Píxeles Totales'].astype(int)
        df_display['Píxeles Bosque'] = df_display['Píxeles Bosque'].astype(int)
        
        return render.DataGrid(
            df_display,
            filters=False,
            height="350px",
            width="100%"
        )
    
    # Funcionalidad de descarga
    @session.download(filename="bosques_riparios_ecuador.csv")
    def descargar_datos():
        df = data.copy()
        
        # Crear un BytesIO buffer para guardar el CSV
        buffer = BytesIO()
        
        # Guardar los datos en formato CSV
        df.to_csv(buffer, index=False, encoding='utf-8')
        
        # Mover el cursor al inicio del buffer
        buffer.seek(0)
        
        # Devolver el contenido del buffer
        return buffer

# Create app
app = App(app_ui, server) 