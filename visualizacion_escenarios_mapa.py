"""
Visualización de Escenarios Prescriptivos en Mapa de Cali

Genera un archivo HTML interactivo con el mapa de Cali mostrando
los escenarios de riesgo por barrio/comuna y las recomendaciones
del modelo prescriptivo MCDA.

Requisitos:
    pip install geopandas folium branca
"""

import geopandas as gpd
import folium
from folium import plugins
import json
from pathlib import Path
from datetime import datetime
import branca.colormap as cm

# Importar escenarios y funciones del módulo de escenarios
from escenarios_prescriptivos import ESCENARIOS, cargar_modelo_mcda, ejecutar_escenario
import pandas as pd

# ============================================================================
# CARGAR FACTORES POR ESTRATEGIA
# ============================================================================

FACTORES_XLSX_PATH = "factores_por_estrategia.xlsx"

# Nombres legibles para los factores
NOMBRES_FACTORES = {
    'disponibilidad_recursos': 'Disponibilidad de recursos',
    'costo_operativo': 'Costo operativo',
    'tiempo_cobertura': 'Tiempo y cobertura',
    'dependencias_externas': 'Dependencias externas',
    'aceptacion_comunidad': 'Aceptación comunidad',
    'acceso_predios': 'Acceso a predios',
    'percepcion_riesgo': 'Percepción de riesgo',
    'resistencia_vector': 'Resistencia del vector',
    'otros_vectores': 'Otros vectores/focos',
    'efectividad_esperada': 'Efectividad esperada',
    'magnitud_brote': 'Magnitud del brote',
}

def cargar_factores_estrategia(xlsx_path=None):
    """
    Carga los factores por estrategia desde el Excel.
    Retorna un diccionario: {estrategia: [{factor, valor}, ...]}
    """
    if xlsx_path is None:
        xlsx_path = FACTORES_XLSX_PATH

    try:
        df = pd.read_excel(xlsx_path)

        # Columnas de factores (todas excepto 'Estrategia')
        factor_cols = [col for col in df.columns if col != 'Estrategia']

        factores_por_estrategia = {}
        for _, row in df.iterrows():
            estrategia = row['Estrategia']
            factores = []
            for col in factor_cols:
                valor = row[col]
                if pd.notna(valor):
                    factores.append({
                        'Factor': NOMBRES_FACTORES.get(col, col),
                        'Valor Est.': float(valor)
                    })
            factores_por_estrategia[estrategia] = factores

        return factores_por_estrategia
    except Exception as e:
        print(f"   ⚠️ No se pudieron cargar factores: {e}")
        return {}


def set_factores_xlsx_path(xlsx_path):
    """Configura el path del archivo de factores y recarga los datos."""
    global FACTORES_XLSX_PATH, FACTORES_POR_ESTRATEGIA
    FACTORES_XLSX_PATH = xlsx_path
    FACTORES_POR_ESTRATEGIA = cargar_factores_estrategia(xlsx_path)


# Cargar factores al inicio
FACTORES_POR_ESTRATEGIA = cargar_factores_estrategia()


def obtener_factores_para_estrategia(nombre_estrategia):
    """
    Busca los factores para una estrategia dada.
    Hace match parcial porque los nombres pueden estar truncados.
    """
    if not FACTORES_POR_ESTRATEGIA:
        return []

    # Primero intenta match exacto
    if nombre_estrategia in FACTORES_POR_ESTRATEGIA:
        return FACTORES_POR_ESTRATEGIA[nombre_estrategia]

    # Si no, intenta match parcial (los primeros 50 caracteres)
    nombre_corto = nombre_estrategia[:50].lower()
    for key, factores in FACTORES_POR_ESTRATEGIA.items():
        if key[:50].lower() == nombre_corto:
            return factores

    # Match más flexible: busca si contiene las primeras palabras
    palabras = nombre_estrategia.split()[:5]
    for key, factores in FACTORES_POR_ESTRATEGIA.items():
        if all(palabra.lower() in key.lower() for palabra in palabras[:3]):
            return factores

    return []


def generar_html_factores(factores, color, factor_id):
    """
    Genera el HTML para mostrar los factores de una estrategia.
    """
    if not factores:
        return ""

    html = f"""
        <div id="{factor_id}_factores" style="display: none; margin-top: 8px; padding: 8px; background: #fff; border-radius: 4px; border: 1px solid #ddd;">
            <div style="font-size: 11px; font-weight: bold; color: #333; margin-bottom: 6px;">📊 Escala de Factores:</div>
            <div style="max-height: 150px; overflow-y: auto;">
    """

    for f in factores:
        valor = f.get('Valor Est.', 0)
        factor_name = f.get('Factor', 'N/A')
        temporalidad = f.get('Temporalidad', '')
        tipo = f.get('Tipo', '')

        # Calcular color del indicador de barra según valor (escala 1-10)
        if valor >= 8:
            bar_color = "#22c55e"  # Verde - alto
        elif valor >= 6:
            bar_color = "#eab308"  # Amarillo - medio
        elif valor >= 4:
            bar_color = "#f97316"  # Naranja - bajo-medio
        else:
            bar_color = "#ef4444"  # Rojo - bajo

        width_pct = min(100, max(0, (valor / 10) * 100))

        html += f"""
                <div style="margin-bottom: 6px; padding: 4px; background: #f8f9fa; border-radius: 3px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 10px; color: #555; flex: 1; margin-right: 8px;" title="{factor_name}">{factor_name[:35]}{'...' if len(factor_name) > 35 else ''}</span>
                        <span style="font-size: 10px; font-weight: bold; color: {bar_color}; min-width: 30px; text-align: right;">{valor:.1f}</span>
                    </div>
                    <div style="height: 4px; background: #e5e7eb; border-radius: 2px; margin-top: 2px;">
                        <div style="height: 100%; width: {width_pct:.0f}%; background: {bar_color}; border-radius: 2px;"></div>
                    </div>
                </div>
        """

    html += """
            </div>
        </div>
    """

    return html

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

SHAPEFILE_PATH = "/Users/juanjose/juan/dengue/data_to_inserts/shapefiles/barrios/cali.shp"
OUTPUT_HTML = "mapa_escenarios_dengue.html"

# Colores para cada nivel de riesgo
COLORES_RIESGO = {
    "bajo_riesgo": "#22c55e",      # Verde
    "riesgo_moderado": "#eab308",   # Amarillo
    "alto_riesgo": "#f97316",       # Naranja
    "emergencia": "#ef4444",        # Rojo
}

# Asignación de escenarios por comuna (simulación de situación epidemiológica)
# Esto simula una situación donde:
# - Comunas del oriente (13-15, 21) tienen mayor riesgo
# - Centro y sur tienen riesgo moderado
# - Zonas residenciales tienen bajo riesgo
ESCENARIOS_POR_COMUNA = {
    # Comunas con BAJO RIESGO (zonas residenciales del oeste/sur)
    "02": "bajo_riesgo",   # Comuna 2
    "17": "bajo_riesgo",   # Comuna 17
    "19": "bajo_riesgo",   # Comuna 19
    "22": "bajo_riesgo",   # Comuna 22
    "05": "bajo_riesgo",   # Comuna 5

    # Comunas con RIESGO MODERADO (centro y transición)
    "03": "riesgo_moderado",   # Comuna 3
    "04": "riesgo_moderado",   # Comuna 4
    "08": "riesgo_moderado",   # Comuna 8
    "09": "riesgo_moderado",   # Comuna 9
    "10": "riesgo_moderado",   # Comuna 10
    "11": "riesgo_moderado",   # Comuna 11
    "12": "riesgo_moderado",   # Comuna 12
    "18": "riesgo_moderado",   # Comuna 18
    "19": "riesgo_moderado",   # Comuna 19
    "01": "riesgo_moderado",   # Comuna 1
    "06": "riesgo_moderado",   # Comuna 6
    "07": "riesgo_moderado",   # Comuna 7

    # Comunas con ALTO RIESGO (oriente - mayor vulnerabilidad)
    "13": "alto_riesgo",   # Comuna 13 - Aguablanca
    "14": "alto_riesgo",   # Comuna 14 - Aguablanca
    "15": "alto_riesgo",   # Comuna 15 - Aguablanca
    "16": "alto_riesgo",   # Comuna 16
    "20": "alto_riesgo",   # Comuna 20 - Siloé
    "21": "alto_riesgo",   # Comuna 21 - Aguablanca

    # Zonas rurales
    "81": "riesgo_moderado",  # Rural
}

# Barrios específicos en EMERGENCIA (simulación de focos activos)
BARRIOS_EMERGENCIA = [
    "Marroquin I",
    "Potrero Grande",
    "El Retiro",
    "Charco Azul",
    "Sardi",
]


def cargar_shapefile():
    """Carga y prepara el shapefile de barrios de Cali."""
    print("📂 Cargando shapefile de barrios...")
    gdf = gpd.read_file(SHAPEFILE_PATH)

    # Extraer comuna de id_sector
    gdf['comuna'] = gdf['id_sector'].astype(str).str.zfill(4).str[:2]

    # Reproyectar a WGS84 para Folium
    gdf = gdf.to_crs(epsg=4326)

    print(f"   ✅ {len(gdf)} barrios cargados")
    print(f"   ✅ {gdf['comuna'].nunique()} comunas identificadas")

    return gdf


def asignar_escenarios(gdf, escenarios_por_comuna=None, barrios_emergencia=None, escenarios_def=None):
    """Asigna escenarios de riesgo a cada barrio."""
    print("\n🎯 Asignando escenarios de riesgo...")

    if escenarios_por_comuna is None:
        escenarios_por_comuna = ESCENARIOS_POR_COMUNA
    if barrios_emergencia is None:
        barrios_emergencia = BARRIOS_EMERGENCIA
    if escenarios_def is None:
        escenarios_def = ESCENARIOS

    def get_escenario(row):
        # Primero verificar si es un barrio en emergencia
        if row['nombre'] in barrios_emergencia:
            return "emergencia"
        # Si no, asignar por comuna
        return escenarios_por_comuna.get(row['comuna'], "bajo_riesgo")

    gdf['escenario'] = gdf.apply(get_escenario, axis=1)

    # Estadísticas
    conteo = gdf['escenario'].value_counts()
    print("   Distribución de escenarios:")
    for esc, count in conteo.items():
        emoji = escenarios_def[esc]['color']
        print(f"   {emoji} {escenarios_def[esc]['nombre']}: {count} barrios")

    return gdf


def ejecutar_modelo_escenarios(escenarios_def=None, contexto_escenario=None):
    """Ejecuta el modelo MCDA para cada escenario y obtiene las recomendaciones."""
    print("\n🔬 Ejecutando modelo MCDA para cada escenario...")

    if escenarios_def is None:
        escenarios_def = ESCENARIOS

    mcda_module = cargar_modelo_mcda()
    resultados = {}

    for escenario_id in escenarios_def.keys():
        try:
            resultado = ejecutar_escenario(
                escenario_id,
                mcda_module,
                escenarios_def=escenarios_def,
                contexto_escenario=contexto_escenario
            )
            resultados[escenario_id] = resultado
            print(f"   ✅ {escenarios_def[escenario_id]['color']} {escenario_id}")
        except Exception as e:
            print(f"   ❌ Error en {escenario_id}: {e}")

    return resultados


def generar_popup_contenido(row, resultados_mcda, escenarios_def=None):
    """Genera el contenido HTML del popup para un barrio."""
    import random

    if escenarios_def is None:
        escenarios_def = ESCENARIOS

    escenario_id = row['escenario']
    escenario = escenarios_def[escenario_id]
    resultado = resultados_mcda.get(escenario_id, {})

    # Color de fondo según nivel de riesgo
    color = COLORES_RIESGO[escenario_id]

    # Obtener top 5 estrategias
    ranking = resultado.get('ranking', [])[:5]
    indicadores_criticos = resultado.get('indicadores_criticos', 0)
    indicadores_normales = resultado.get('indicadores_normales', 0)
    total = indicadores_criticos + indicadores_normales
    pct_criticos = (indicadores_criticos / total * 100) if total > 0 else 0

    # ID único para este popup (para el JavaScript)
    popup_id = f"popup_{row['id_sector']}_{random.randint(1000, 9999)}"

    # Construir HTML del popup
    html = f"""
    <div style="width: 450px; max-height: 600px; font-family: 'Segoe UI', Arial, sans-serif; overflow-y: auto;">
        <div style="background: {color}; color: white; padding: 12px; border-radius: 8px 8px 0 0; position: sticky; top: 0; z-index: 10;">
            <h3 style="margin: 0; font-size: 16px;">{escenario['color']} {row['nombre']}</h3>
            <p style="margin: 4px 0 0 0; font-size: 12px; opacity: 0.9;">
                Comuna {row['comuna']} | Sector {row['id_sector']}
            </p>
        </div>

        <div style="padding: 12px; background: #f8f9fa; border: 1px solid #dee2e6;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div>
                    <strong style="font-size: 14px;">Nivel de Alerta</strong><br>
                    <span style="font-size: 24px; font-weight: bold; color: {color};">
                        {escenario['nivel_alerta']}/4
                    </span>
                </div>
                <div style="text-align: right;">
                    <strong style="font-size: 14px;">Indicadores Críticos</strong><br>
                    <span style="font-size: 24px; font-weight: bold; color: {color};">
                        {pct_criticos:.0f}%
                    </span>
                    <span style="font-size: 12px; color: #666;">({indicadores_criticos}/{total})</span>
                </div>
            </div>

            <div style="background: white; padding: 10px; border-radius: 6px; margin-bottom: 10px;">
                <strong style="font-size: 13px; color: #333;">Estado: {escenario['nombre']}</strong>
                <p style="font-size: 11px; color: #666; margin: 5px 0 0 0;">
                    {escenario['descripcion'].strip()}
                </p>
            </div>

            <div style="background: white; padding: 10px; border-radius: 6px;">
                <strong style="font-size: 13px; color: #333;">
                    📋 Top 5 Estrategias Recomendadas
                </strong>
                <div style="margin-top: 10px;">
    """

    for i, (est, rank, score, comp) in enumerate(ranking):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
        item_id = f"{popup_id}_item_{i}"

        # Versión corta y larga
        est_short = est[:60] + "..." if len(est) > 60 else est
        needs_expand = len(est) > 60

        # Obtener factores para esta estrategia
        factores = obtener_factores_para_estrategia(est)
        factores_html = generar_html_factores(factores, color, item_id) if factores else ""
        has_factores = len(factores) > 0

        html += f"""
                    <div style="background: #f8f9fa; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid {color};">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <span style="font-size: 18px; margin-right: 8px;">{medal}</span>
                            <div style="flex: 1;">
                                <div id="{item_id}_short" style="font-size: 12px; color: #333; {'display: block;' if needs_expand else 'display: none;'}">
                                    {est_short}
                                    <button onclick="document.getElementById('{item_id}_short').style.display='none'; document.getElementById('{item_id}_full').style.display='block';"
                                            style="background: none; border: none; color: {color}; cursor: pointer; font-size: 11px; padding: 0; margin-left: 4px; text-decoration: underline;">
                                        Ver más
                                    </button>
                                </div>
                                <div id="{item_id}_full" style="font-size: 12px; color: #333; {'display: none;' if needs_expand else 'display: block;'}">
                                    {est}
                                    {'<button onclick="document.getElementById(' + chr(39) + item_id + '_full' + chr(39) + ').style.display=' + chr(39) + 'none' + chr(39) + '; document.getElementById(' + chr(39) + item_id + '_short' + chr(39) + ').style.display=' + chr(39) + 'block' + chr(39) + ';" style="background: none; border: none; color: ' + color + '; cursor: pointer; font-size: 11px; padding: 0; margin-left: 4px; text-decoration: underline;">Ver menos</button>' if needs_expand else ''}
                                </div>
                                <div style="margin-top: 4px;">
                                    <span style="font-size: 10px; color: #888; background: #e9ecef; padding: 2px 6px; border-radius: 3px;">
                                        Score: {score:.4f}
                                    </span>
                                    <span style="font-size: 10px; color: #888; background: #e9ecef; padding: 2px 6px; border-radius: 3px; margin-left: 4px;">
                                        Cumplimiento: {comp:.1%}
                                    </span>
                                    {'<button onclick="var el=document.getElementById(' + chr(39) + item_id + '_factores' + chr(39) + '); el.style.display = el.style.display === ' + chr(39) + 'none' + chr(39) + ' ? ' + chr(39) + 'block' + chr(39) + ' : ' + chr(39) + 'none' + chr(39) + ';" style="font-size: 10px; color: #fff; background: ' + color + '; padding: 2px 6px; border-radius: 3px; margin-left: 4px; border: none; cursor: pointer;">📊 Factores</button>' if has_factores else ''}
                                </div>
                                {factores_html}
                            </div>
                        </div>
                    </div>
        """

    html += """
                </div>
            </div>
        </div>

        <div style="background: #e9ecef; padding: 8px 12px; border-radius: 0 0 8px 8px;
                    font-size: 10px; color: #666; text-align: center;">
            Sistema de Soporte a Decisiones - Control de Dengue | Modelo MCDA
        </div>
    </div>
    """

    return html


def generar_tooltip(row, escenarios_def=None):
    """Genera el tooltip simple para un barrio."""
    if escenarios_def is None:
        escenarios_def = ESCENARIOS
    escenario_id = row['escenario']
    escenario = escenarios_def[escenario_id]
    return f"{escenario['color']} {row['nombre']} - {escenario['nombre']}"


def crear_mapa(gdf, resultados_mcda, escenarios_def=None, mapa_titulo=None, mapa_subtitulo=None):
    """Crea el mapa interactivo con Folium."""
    print("\n🗺️ Generando mapa interactivo...")

    if escenarios_def is None:
        escenarios_def = ESCENARIOS

    # Calcular centro del mapa
    bounds = gdf.total_bounds
    center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

    # Crear mapa base
    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles=None,
    )

    # Agregar capas base
    folium.TileLayer(
        tiles='CartoDB positron',
        name='Mapa Claro',
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='Mapa Oscuro',
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        control=True
    ).add_to(m)

    # Crear grupos de capas por escenario
    grupos = {}
    for escenario_id in escenarios_def.keys():
        escenario = escenarios_def[escenario_id]
        grupos[escenario_id] = folium.FeatureGroup(
            name=f"{escenario['color']} {escenario['nombre']}"
        )

    # Agregar barrios al mapa
    print("   Agregando barrios al mapa...")
    for idx, row in gdf.iterrows():
        escenario_id = row['escenario']
        color = COLORES_RIESGO[escenario_id]

        # Crear GeoJSON para el polígono
        geo_json = folium.GeoJson(
            row['geometry'].__geo_interface__,
            style_function=lambda x, color=color: {
                'fillColor': color,
                'color': '#333',
                'weight': 1,
                'fillOpacity': 0.6,
            },
            highlight_function=lambda x: {
                'weight': 3,
                'color': '#000',
                'fillOpacity': 0.8,
            },
            tooltip=generar_tooltip(row, escenarios_def=escenarios_def),
        )

        # Agregar popup con información detallada
        popup_html = generar_popup_contenido(row, resultados_mcda, escenarios_def=escenarios_def)
        popup = folium.Popup(popup_html, max_width=450)
        geo_json.add_child(popup)

        # Agregar al grupo correspondiente
        geo_json.add_to(grupos[escenario_id])

    # Agregar grupos al mapa
    for grupo in grupos.values():
        grupo.add_to(m)

    # Agregar leyenda personalizada
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                background: white; padding: 15px; border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2); font-family: Arial, sans-serif;">
        <h4 style="margin: 0 0 10px 0; font-size: 14px;">Niveles de Riesgo</h4>
        <div style="display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background: #22c55e; border-radius: 4px;"></div>
                <span style="font-size: 12px;">🟢 Bajo Riesgo - Vigilancia Rutinaria</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background: #eab308; border-radius: 4px;"></div>
                <span style="font-size: 12px;">🟡 Riesgo Moderado - Alerta Epidemiológica</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background: #f97316; border-radius: 4px;"></div>
                <span style="font-size: 12px;">🟠 Alto Riesgo - Brote Activo</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background: #ef4444; border-radius: 4px;"></div>
                <span style="font-size: 12px;">🔴 Emergencia - Crisis Sanitaria</span>
            </div>
        </div>
        <p style="margin: 10px 0 0 0; font-size: 10px; color: #666;">
            Click en un barrio para ver recomendaciones
        </p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Agregar título
    if mapa_titulo is None:
        mapa_titulo = "🦟 Sistema de Soporte a Decisiones - Control de Dengue"
    if mapa_subtitulo is None:
        mapa_subtitulo = "Escenarios Prescriptivos por Barrio - Cali, Colombia |"

    title_html = f"""
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                z-index: 1000; background: white; padding: 12px 24px; border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2); font-family: Arial, sans-serif;
                text-align: center;">
        <h2 style="margin: 0; font-size: 18px; color: #333;">
            {mapa_titulo}
        </h2>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">
            {mapa_subtitulo}
            Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # Agregar panel de estadísticas
    stats = gdf['escenario'].value_counts()
    stats_html = f"""
    <div style="position: fixed; top: 80px; right: 10px; z-index: 1000;
                background: white; padding: 15px; border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2); font-family: Arial, sans-serif;
                min-width: 200px;">
        <h4 style="margin: 0 0 10px 0; font-size: 14px;">📊 Resumen</h4>
        <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 4px 0;">🟢 Bajo Riesgo</td>
                <td style="text-align: right; font-weight: bold;">{stats.get('bajo_riesgo', 0)} barrios</td>
            </tr>
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 4px 0;">🟡 Riesgo Moderado</td>
                <td style="text-align: right; font-weight: bold;">{stats.get('riesgo_moderado', 0)} barrios</td>
            </tr>
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 4px 0;">🟠 Alto Riesgo</td>
                <td style="text-align: right; font-weight: bold;">{stats.get('alto_riesgo', 0)} barrios</td>
            </tr>
            <tr>
                <td style="padding: 4px 0;">🔴 Emergencia</td>
                <td style="text-align: right; font-weight: bold;">{stats.get('emergencia', 0)} barrios</td>
            </tr>
        </table>
        <hr style="margin: 10px 0; border: none; border-top: 1px solid #eee;">
        <div style="font-size: 11px; color: #666;">
            <strong>Total:</strong> {len(gdf)} barrios<br>
            <strong>Comunas:</strong> {gdf['comuna'].nunique()}
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(stats_html))

    # Agregar control de capas
    folium.LayerControl(collapsed=False).add_to(m)

    # Agregar herramientas adicionales
    plugins.Fullscreen().add_to(m)
    plugins.MiniMap(toggle_display=True).add_to(m)

    return m


def main():
    """Función principal."""
    print("=" * 70)
    print("GENERADOR DE MAPA DE ESCENARIOS PRESCRIPTIVOS - CONTROL DE DENGUE")
    print("=" * 70)

    # 1. Cargar shapefile
    gdf = cargar_shapefile()

    # 2. Asignar escenarios
    gdf = asignar_escenarios(gdf)

    # 3. Ejecutar modelo MCDA
    resultados_mcda = ejecutar_modelo_escenarios()

    # 4. Crear mapa
    mapa = crear_mapa(gdf, resultados_mcda)

    # 5. Guardar HTML
    print(f"\n💾 Guardando mapa en {OUTPUT_HTML}...")
    mapa.save(OUTPUT_HTML)

    print("\n" + "=" * 70)
    print("✅ MAPA GENERADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\n📍 Archivo: {OUTPUT_HTML}")
    print("   Abrir en navegador para visualizar el mapa interactivo")
    print("\n   Instrucciones:")
    print("   - Click en un barrio para ver las recomendaciones del modelo")
    print("   - Use los controles de capa para filtrar por nivel de riesgo")
    print("   - Use el minimapa para navegar rápidamente")

    return mapa


if __name__ == "__main__":
    main()
