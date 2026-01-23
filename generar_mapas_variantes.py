"""
Genera 4 mapas HTML adicionales con escenarios prescriptivos alternativos,
con valores basados en umbrales del Excel y situaciones realistas.
"""

from copy import deepcopy
from datetime import datetime
import importlib.util
import pandas as pd

from escenarios_prescriptivos import ESCENARIOS
from visualizacion_escenarios_mapa import (
    cargar_shapefile,
    asignar_escenarios,
    ejecutar_modelo_escenarios,
    crear_mapa,
    COLORES_RIESGO,
    set_factores_xlsx_path,
)
from escenaries import (
    ESCENARIO_TODOS_CRITICOS_BASE,
    ESCENARIO_TODOS_VERDES_BASE,
    PERFILES_CRITICOS,
    PERFILES_VERDES,
    obtener_perfil_por_comuna,
)

XLSX_PATH = "Reporte_Estrategias_Indicadores.xlsx"

INTEGER_INDICATORS = {
    "Número de casos por semana epidemiológica",
    "Muertes probables",
    "Serotipos circulantes",
    "Zona del canal endémico (situación)",
    "Tipo de brote",
    "Inicio y mantenimiento de brote histórico",
    "Número de organizaciones sociales",
    "Frecuencia de recolección de residuos sólidos",
}

LEVELS = ["bajo_riesgo", "riesgo_moderado", "alto_riesgo", "emergencia"]

# Porcentaje objetivo de indicadores críticos por nivel
# Estos valores definen qué tan grave es cada escenario
PORCENTAJE_CRITICOS_OBJETIVO = {
    "bajo_riesgo": 0.10,        # ~10% de indicadores críticos
    "riesgo_moderado": 0.35,    # ~35% de indicadores críticos
    "alto_riesgo": 0.60,        # ~60% de indicadores críticos
    "emergencia": 0.90,         # ~90% de indicadores críticos
}

# Multiplicadores para indicadores que SÍ deben ser críticos en cada nivel
# Para op ">" : valor = umbral × multiplicador (si >1, cruza el umbral)
# Para op "<" : valor = umbral × multiplicador (si <1, cruza el umbral)
MULT_CRITICO_GT = 1.3    # Valor por encima del umbral
MULT_NO_CRITICO_GT = 0.7  # Valor por debajo del umbral
MULT_CRITICO_LT = 0.7    # Valor por debajo del umbral
MULT_NO_CRITICO_LT = 1.3  # Valor por encima del umbral

# Mantener compatibilidad (ya no se usan directamente, pero por si acaso)
MULTIPLIERS_GT = {
    "bajo_riesgo": 0.6,
    "riesgo_moderado": 0.85,
    "alto_riesgo": 1.2,
    "emergencia": 1.6,
}

MULTIPLIERS_LT = {
    "bajo_riesgo": 1.4,
    "riesgo_moderado": 1.15,
    "alto_riesgo": 0.8,
    "emergencia": 0.6,
}


def cargar_modulo_mcda():
    spec = importlib.util.spec_from_file_location("mcda_model", "scikit-criteria-demo.py")
    mcda_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcda_module)
    return mcda_module


def cargar_umbral_y_dominios(xlsx_path=XLSX_PATH):
    mcda_module = cargar_modulo_mcda()
    _, _, indicator_thresholds = mcda_module.load_strategies_from_xlsx(xlsx_path)

    df = pd.read_excel(xlsx_path)
    df.columns = df.columns.str.strip()
    domains = (
        df.dropna(subset=["Indicador", "Dominio"])
        .groupby("Indicador")["Dominio"]
        .first()
        .to_dict()
    )

    return indicator_thresholds, domains


def value_for_level(op, threshold, level):
    if threshold is None:
        return None

    if op in (">", ">="):
        multiplier = MULTIPLIERS_GT[level]
        value = threshold * multiplier
    elif op in ("<", "<="):
        multiplier = MULTIPLIERS_LT[level]
        value = threshold * multiplier
    else:
        value = threshold

    return max(value, 0)


def coerce_value(indicator, value, base_value=None):
    if indicator in INTEGER_INDICATORS:
        return int(round(value))
    if base_value is not None and isinstance(base_value, int):
        return int(round(value))
    return round(float(value), 2)


def construir_escenarios_base(thresholds, escenarios_base):
    """
    Construye escenarios con porcentajes graduales de indicadores críticos.

    En lugar de que todos los indicadores crucen o no crucen el umbral,
    seleccionamos cuáles indicadores serán críticos según el nivel de alerta.
    """
    import random
    random.seed(42)  # Reproducibilidad

    escenarios = deepcopy(escenarios_base)

    # Ordenar indicadores por "prioridad de activación"
    # Los indicadores epidemiológicos y entomológicos se activan primero
    indicadores_ordenados = list(thresholds.keys())

    # Priorizar ciertos indicadores para que se activen primero
    prioridad_alta = [
        "Número de casos por semana epidemiológica",
        "Tasa de incidencia semanal",
        "Índice de Breteau (IB)",
        "Índice de vivienda (IV)",
        "Porcentaje de hospitalización por dengue",
        "Muertes probables",
        "Índice de depósito (ID)",
        "Índice pupal",
        "Número de ovitrampas positivas",
        "Razón de crecimiento epidémico",
        "Variación porcentual",
        "Serotipos circulantes",
    ]

    # Ordenar: primero los de alta prioridad, luego el resto
    def sort_key(ind):
        for i, p in enumerate(prioridad_alta):
            if p.lower() in ind.lower():
                return i
        return len(prioridad_alta) + random.random()

    indicadores_ordenados.sort(key=sort_key)
    total_indicadores = len(indicadores_ordenados)

    for level_id in escenarios:
        pct_criticos = PORCENTAJE_CRITICOS_OBJETIVO.get(level_id, 0.5)
        n_criticos = int(total_indicadores * pct_criticos)

        # Los primeros n_criticos indicadores serán críticos
        indicadores_criticos = set(indicadores_ordenados[:n_criticos])

        for indicador, cfg in thresholds.items():
            op = cfg.get("op")
            threshold = cfg.get("threshold")

            if threshold is None:
                continue

            es_critico = indicador in indicadores_criticos

            # Calcular valor según si debe ser crítico o no
            if op in (">", ">="):
                if es_critico:
                    # Valor por ENCIMA del umbral (crítico)
                    val = threshold * MULT_CRITICO_GT
                else:
                    # Valor por DEBAJO del umbral (no crítico)
                    val = threshold * MULT_NO_CRITICO_GT
            elif op in ("<", "<="):
                if es_critico:
                    # Valor por DEBAJO del umbral (crítico)
                    val = threshold * MULT_CRITICO_LT
                else:
                    # Valor por ENCIMA del umbral (no crítico)
                    val = threshold * MULT_NO_CRITICO_LT
            else:
                val = threshold

            val = max(val, 0)
            base_val = escenarios[level_id]["indicadores"].get(indicador)
            escenarios[level_id]["indicadores"][indicador] = coerce_value(indicador, val, base_val)

    return escenarios


def apply_indicator_overrides(escenarios, overrides):
    for level_id, ind_overrides in overrides.items():
        for indicador, override in ind_overrides.items():
            if indicador not in escenarios[level_id]["indicadores"]:
                continue
            current = escenarios[level_id]["indicadores"][indicador]
            if callable(override):
                new_val = override(current)
            else:
                new_val = override
            escenarios[level_id]["indicadores"][indicador] = coerce_value(indicador, new_val, current)


def apply_factor_overrides(escenarios, overrides):
    for level_id, factor_overrides in overrides.items():
        for factor, value in factor_overrides.items():
            escenarios[level_id]["factores_estrategia"][factor] = value


def mult(factor):
    return lambda v: v * factor


def build_mapping(low, moderate, high):
    mapping = {c: "bajo_riesgo" for c in low}
    mapping.update({c: "riesgo_moderado" for c in moderate})
    mapping.update({c: "alto_riesgo" for c in high})
    mapping["81"] = "riesgo_moderado"  # zona rural
    return mapping


def pick_emergency_barrios(gdf, comunas, n=5):
    subset = gdf[gdf["comuna"].isin(comunas)].sort_values("nombre")
    return subset["nombre"].head(n).tolist()


def construir_variantes():
    low = ["02", "05", "17", "19", "22"]

    variantes = [
        {
            "id": "lluvias_intensas",
            "titulo": "🌧️ Escenario A: Lluvias intensas y drenajes colapsados",
            "subtitulo": "Escenarios por barrio - presión climática y entomológica |",
            "escenarios_por_comuna": build_mapping(
                low=low,
                moderate=["13", "14", "15", "16", "21"],
                high=["06", "07", "08", "09", "10", "11", "12"],
            ),
            "emergencia_comunas": ["07", "08", "09"],
            "indicator_overrides": {
                "riesgo_moderado": {
                    "Índice de pluviosidad (días previos)": mult(1.3),
                    "Estado de sumideros (limpios / obstruidos)": mult(1.25),
                    "Estado de canales de aguas lluvias (limpios / obstruidos)": mult(1.25),
                    "Índice de Breteau (IB)": mult(1.2),
                    "Índice de vivienda (IV)": mult(1.2),
                    "Índice de depósito (ID)": mult(1.2),
                    "Índice pupal": mult(1.15),
                    "Número de ovitrampas positivas": mult(1.2),
                },
                "alto_riesgo": {
                    "Índice de pluviosidad (días previos)": mult(1.45),
                    "Estado de sumideros (limpios / obstruidos)": mult(1.35),
                    "Estado de canales de aguas lluvias (limpios / obstruidos)": mult(1.35),
                    "Índice de Breteau (IB)": mult(1.3),
                    "Índice de vivienda (IV)": mult(1.3),
                    "Índice de depósito (ID)": mult(1.3),
                    "Índice pupal": mult(1.2),
                    "Número de ovitrampas positivas": mult(1.3),
                    "Tiempo de respuesta de control vectorial desde la notificación": mult(1.1),
                },
                "emergencia": {
                    "Índice de pluviosidad (días previos)": mult(1.6),
                    "Estado de sumideros (limpios / obstruidos)": mult(1.45),
                    "Estado de canales de aguas lluvias (limpios / obstruidos)": mult(1.45),
                    "Índice de Breteau (IB)": mult(1.4),
                    "Índice de vivienda (IV)": mult(1.4),
                    "Índice de depósito (ID)": mult(1.4),
                    "Índice pupal": mult(1.3),
                    "Número de ovitrampas positivas": mult(1.4),
                    "Tiempo promedio de ejecución": mult(1.15),
                },
            },
        },
        {
            "id": "intermitencia_agua",
            "titulo": "🚰 Escenario B: Intermitencia de agua y almacenamiento doméstico",
            "subtitulo": "Escenarios por barrio - criaderos intradomiciliarios |",
            "escenarios_por_comuna": build_mapping(
                low=low,
                moderate=["06", "07", "08", "11", "12"],
                high=["13", "14", "15", "16", "21"],
            ),
            "emergencia_comunas": ["13", "14", "15"],
            "indicator_overrides": {
                "riesgo_moderado": {
                    "Continuidad en el servicio de acueducto": mult(0.85),
                    "Cobertura de agua potable": mult(0.92),
                    "Índice de depósito (ID)": mult(1.2),
                    "Tipo de depósito positivo dominante": mult(1.2),
                    "Índice de depósito en concentraciones humanas": mult(1.15),
                    "Prácticas preventivas": mult(0.9),
                    "Cobertura de hogares alcanzados con mensajes de riesgo": mult(0.9),
                    "Presencia de basureros ilegales o puntos críticos de residuos": mult(1.15),
                },
                "alto_riesgo": {
                    "Continuidad en el servicio de acueducto": mult(0.75),
                    "Cobertura de agua potable": mult(0.88),
                    "Índice de depósito (ID)": mult(1.35),
                    "Tipo de depósito positivo dominante": mult(1.3),
                    "Índice de depósito en concentraciones humanas": mult(1.25),
                    "Prácticas preventivas": mult(0.85),
                    "Cobertura de hogares alcanzados con mensajes de riesgo": mult(0.85),
                    "Presencia de basureros ilegales o puntos críticos de residuos": mult(1.25),
                },
                "emergencia": {
                    "Continuidad en el servicio de acueducto": mult(0.65),
                    "Cobertura de agua potable": mult(0.82),
                    "Índice de depósito (ID)": mult(1.5),
                    "Tipo de depósito positivo dominante": mult(1.45),
                    "Índice de depósito en concentraciones humanas": mult(1.35),
                    "Prácticas preventivas": mult(0.8),
                    "Cobertura de hogares alcanzados con mensajes de riesgo": mult(0.8),
                    "Presencia de basureros ilegales o puntos críticos de residuos": mult(1.35),
                },
            },
        },
        {
            "id": "movilidad_eventos",
            "titulo": "🧳 Escenario C: Movilidad y eventos masivos",
            "subtitulo": "Escenarios por barrio - presión epidemiológica con entomología moderada |",
            "escenarios_por_comuna": build_mapping(
                low=low,
                moderate=["01", "06", "07", "08", "13"],
                high=["03", "04", "09", "10", "11", "12"],
            ),
            "emergencia_comunas": ["03", "04"],
            "indicator_overrides": {
                "riesgo_moderado": {
                    "Número de casos por semana epidemiológica": mult(1.25),
                    "Tasa de incidencia semanal": mult(1.2),
                    "Razón de crecimiento epidémico frente al año anterior": mult(1.15),
                    "Serotipos circulantes": mult(1.15),
                    "Densidad poblacional": mult(1.1),
                    "Percepción de riesgo comunitario": mult(0.92),
                    "Tiempo entre síntoma y consulta": mult(1.05),
                    "Tiempo entre consulta y notificación": mult(1.05),
                },
                "alto_riesgo": {
                    "Número de casos por semana epidemiológica": mult(1.4),
                    "Tasa de incidencia semanal": mult(1.3),
                    "Razón de crecimiento epidémico frente al año anterior": mult(1.2),
                    "Serotipos circulantes": mult(1.2),
                    "Densidad poblacional": mult(1.2),
                    "Percepción de riesgo comunitario": mult(0.9),
                    "Tiempo entre síntoma y consulta": mult(1.1),
                    "Tiempo entre consulta y notificación": mult(1.1),
                },
                "emergencia": {
                    "Número de casos por semana epidemiológica": mult(1.6),
                    "Tasa de incidencia semanal": mult(1.45),
                    "Razón de crecimiento epidémico frente al año anterior": mult(1.3),
                    "Serotipos circulantes": mult(1.3),
                    "Densidad poblacional": mult(1.25),
                    "Percepción de riesgo comunitario": mult(0.88),
                    "Tiempo entre síntoma y consulta": mult(1.15),
                    "Tiempo entre consulta y notificación": mult(1.15),
                },
            },
        },
        {
            "id": "saturacion_operativa",
            "titulo": "🏥 Escenario D: Saturación operativa y hospitalaria",
            "subtitulo": "Escenarios por barrio - limitaciones de capacidad de respuesta |",
            "escenarios_por_comuna": build_mapping(
                low=low,
                moderate=["11", "12", "13", "21"],
                high=["14", "15", "16", "18", "20"],
            ),
            "emergencia_comunas": ["16", "20"],
            "indicator_overrides": {
                "riesgo_moderado": {
                    "Disponibilidad de insumos": mult(0.85),
                    "Disponibilidad de equipos": mult(0.85),
                    "Personal en terreno": mult(0.9),
                    "Disponibilidad logística semanal": mult(0.85),
                    "Tiempo de alistamiento de brigadas": mult(1.1),
                    "Tiempo de respuesta de control vectorial desde la notificación": mult(1.2),
                    "Tiempo promedio de ejecución": mult(1.1),
                    "Disponibilidad de camas hospitalarias/UCI para dengue grave": mult(0.85),
                    "Capacidad máxima por comuna": mult(1.1),
                },
                "alto_riesgo": {
                    "Disponibilidad de insumos": mult(0.75),
                    "Disponibilidad de equipos": mult(0.75),
                    "Personal en terreno": mult(0.8),
                    "Disponibilidad logística semanal": mult(0.8),
                    "Tiempo de alistamiento de brigadas": mult(1.2),
                    "Tiempo de respuesta de control vectorial desde la notificación": mult(1.3),
                    "Tiempo promedio de ejecución": mult(1.2),
                    "Disponibilidad de camas hospitalarias/UCI para dengue grave": mult(0.75),
                    "Capacidad máxima por comuna": mult(1.2),
                    "Cobertura de eliminación de criaderos o control químico en zonas de brote": mult(0.85),
                    "Inspección y control en viviendas": mult(0.85),
                },
                "emergencia": {
                    "Disponibilidad de insumos": mult(0.65),
                    "Disponibilidad de equipos": mult(0.65),
                    "Personal en terreno": mult(0.7),
                    "Disponibilidad logística semanal": mult(0.7),
                    "Tiempo de alistamiento de brigadas": mult(1.3),
                    "Tiempo de respuesta de control vectorial desde la notificación": mult(1.4),
                    "Tiempo promedio de ejecución": mult(1.3),
                    "Disponibilidad de camas hospitalarias/UCI para dengue grave": mult(0.65),
                    "Capacidad máxima por comuna": mult(1.3),
                    "Cobertura de eliminación de criaderos o control químico en zonas de brote": mult(0.8),
                    "Inspección y control en viviendas": mult(0.8),
                },
            },
            "factor_overrides": {
                "riesgo_moderado": {
                    "disponibilidad_recursos": 4,
                    "costo_operativo": 6,
                    "tiempo_cobertura": 4,
                },
                "alto_riesgo": {
                    "disponibilidad_recursos": 3,
                    "costo_operativo": 7,
                    "tiempo_cobertura": 3,
                },
                "emergencia": {
                    "disponibilidad_recursos": 2,
                    "costo_operativo": 8,
                    "tiempo_cobertura": 2,
                },
            },
        },
    ]

    return variantes


def construir_escenarios_criticos_diferenciados():
    """
    Construye escenarios donde todos los barrios están en emergencia,
    pero con estrategias diferenciadas según el perfil de cada zona.
    """
    escenarios = {}

    for perfil_id, perfil_data in PERFILES_CRITICOS.items():
        indicadores = ESCENARIO_TODOS_CRITICOS_BASE.copy()
        indicadores.update(perfil_data.get("indicadores_especificos", {}))

        escenarios[perfil_id] = {
            "nombre": perfil_data["nombre"],
            "descripcion": perfil_data["descripcion"],
            "color": "🔴",
            "nivel_alerta": 4,
            "indicadores": indicadores,
            "factores_estrategia": perfil_data["factores_estrategia"],
            "estrategias_esperadas": perfil_data["estrategias_prioritarias"],
        }

    return escenarios


def construir_escenarios_verdes_diferenciados():
    """
    Construye escenarios donde todos los barrios están en bajo riesgo,
    pero con estrategias diferenciadas según el perfil de cada zona.
    """
    escenarios = {}

    for perfil_id, perfil_data in PERFILES_VERDES.items():
        indicadores = ESCENARIO_TODOS_VERDES_BASE.copy()
        indicadores.update(perfil_data.get("indicadores_especificos", {}))

        escenarios[perfil_id] = {
            "nombre": perfil_data["nombre"],
            "descripcion": perfil_data["descripcion"],
            "color": "🟢",
            "nivel_alerta": 1,
            "indicadores": indicadores,
            "factores_estrategia": perfil_data["factores_estrategia"],
            "estrategias_esperadas": perfil_data["estrategias_prioritarias"],
        }

    return escenarios


def asignar_escenarios_por_perfil(gdf, escenario_tipo="critico"):
    """Asigna a cada barrio su perfil de zona según la comuna."""
    def get_perfil(row):
        return obtener_perfil_por_comuna(row['comuna'], escenario_tipo)

    gdf = gdf.copy()
    gdf['escenario'] = gdf.apply(get_perfil, axis=1)
    return gdf


def ejecutar_modelo_por_perfil(escenarios, xlsx_path=XLSX_PATH):
    """
    Ejecuta el modelo MCDA para cada perfil usando su contexto específico.
    Cada perfil usa su propio contexto para generar estrategias diferenciadas.
    """
    from escenarios_prescriptivos import cargar_modelo_mcda, ejecutar_escenario

    print("\n🔬 Ejecutando modelo MCDA por perfil (con contextos diferenciados)...")
    mcda_module = cargar_modelo_mcda()
    resultados = {}

    for perfil_id in escenarios.keys():
        try:
            # Cada perfil usa su propio ID como contexto
            resultado = ejecutar_escenario(
                perfil_id,
                mcda_module,
                xlsx_path,
                escenarios_def=escenarios,
                contexto_escenario=perfil_id  # Usa el perfil como contexto
            )
            resultados[perfil_id] = resultado
            print(f"   ✅ {escenarios[perfil_id]['color']} {perfil_id}")
        except Exception as e:
            print(f"   ❌ Error en {perfil_id}: {e}")

    return resultados


def generar_mapa_todos_criticos(gdf, xlsx_path=XLSX_PATH):
    """
    Genera el mapa con todos los barrios en estado crítico,
    con estrategias DIFERENCIADAS por perfil de zona.
    """
    print("\n🔴 Generando mapa: TODOS CRÍTICOS con estrategias diferenciadas...")

    # Construir escenarios diferenciados
    escenarios = construir_escenarios_criticos_diferenciados()

    # Asignar perfil a cada barrio
    gdf_esc = asignar_escenarios_por_perfil(gdf.copy(), "critico")

    # Mostrar distribución
    conteo = gdf_esc['escenario'].value_counts()
    print("   Distribución por perfil de zona:")
    for perfil, count in conteo.items():
        nombre = PERFILES_CRITICOS[perfil]["nombre"]
        print(f"   🔴 {nombre}: {count} barrios")

    # Agregar colores diferenciados (tonos de rojo)
    colores_criticos = {
        "agua_intermitente": "#dc2626",      # Rojo
        "alta_densidad": "#b91c1c",          # Rojo oscuro
        "construcciones": "#ef4444",         # Rojo claro
        "dificil_acceso": "#7f1d1d",         # Rojo muy oscuro
        "rechazo_comunitario": "#f87171",    # Rojo suave
    }
    COLORES_RIESGO.update(colores_criticos)

    # Ejecutar modelo con contexto específico por perfil
    resultados = ejecutar_modelo_por_perfil(escenarios, xlsx_path)

    mapa = crear_mapa(
        gdf_esc,
        resultados,
        escenarios_def=escenarios,
        mapa_titulo="🔴 Escenario: EMERGENCIA TOTAL - Estrategias diferenciadas por zona",
        mapa_subtitulo="Cada zona tiene estrategias específicas según sus características |",
    )

    return mapa


def generar_mapa_todos_verdes(gdf, xlsx_path=XLSX_PATH):
    """
    Genera el mapa con todos los barrios en bajo riesgo,
    con estrategias de mantenimiento DIFERENCIADAS por perfil de zona.
    """
    print("\n🟢 Generando mapa: TODOS VERDES con estrategias diferenciadas...")

    # Construir escenarios diferenciados
    escenarios = construir_escenarios_verdes_diferenciados()

    # Asignar perfil a cada barrio
    gdf_esc = asignar_escenarios_por_perfil(gdf.copy(), "verde")

    # Mostrar distribución
    conteo = gdf_esc['escenario'].value_counts()
    print("   Distribución por perfil de zona:")
    for perfil, count in conteo.items():
        nombre = PERFILES_VERDES[perfil]["nombre"]
        print(f"   🟢 {nombre}: {count} barrios")

    # Agregar colores diferenciados (tonos de verde)
    colores_verdes = {
        "historicamente_problematica": "#16a34a",  # Verde
        "bien_organizada": "#15803d",              # Verde oscuro
        "buena_infraestructura": "#22c55e",        # Verde claro
        "cobertura_agua_variable": "#166534",      # Verde muy oscuro
        "transicion": "#4ade80",                   # Verde suave
    }
    COLORES_RIESGO.update(colores_verdes)

    # Ejecutar modelo con contexto específico por perfil
    resultados = ejecutar_modelo_por_perfil(escenarios, xlsx_path)

    mapa = crear_mapa(
        gdf_esc,
        resultados,
        escenarios_def=escenarios,
        mapa_titulo="🟢 Escenario: BAJO RIESGO TOTAL - Estrategias diferenciadas por zona",
        mapa_subtitulo="Cada zona tiene estrategias de mantenimiento según sus características |",
    )

    return mapa


def generar_mapas_extremos(xlsx_path=XLSX_PATH):
    """
    Genera los mapas de los escenarios extremos:
    - Todos los barrios en crítico
    - Todos los barrios en verde
    """
    gdf = cargar_shapefile()
    outputs = []

    # Mapa todos críticos
    mapa_criticos = generar_mapa_todos_criticos(gdf, xlsx_path)
    output_criticos = "mapa_escenarios_dengue_todos_criticos.html"
    mapa_criticos.save(output_criticos)
    outputs.append(output_criticos)
    print(f"   ✅ Guardado: {output_criticos}")

    # Mapa todos verdes
    mapa_verdes = generar_mapa_todos_verdes(gdf, xlsx_path)
    output_verdes = "mapa_escenarios_dengue_todos_verdes.html"
    mapa_verdes.save(output_verdes)
    outputs.append(output_verdes)
    print(f"   ✅ Guardado: {output_verdes}")

    return outputs


def generar_mapas_variantes(xlsx_path=XLSX_PATH):
    thresholds, _ = cargar_umbral_y_dominios(xlsx_path)
    escenarios_base = construir_escenarios_base(thresholds, ESCENARIOS)

    gdf = cargar_shapefile()

    variantes = construir_variantes()
    outputs = []

    for variante in variantes:
        escenarios = deepcopy(escenarios_base)
        apply_indicator_overrides(escenarios, variante.get("indicator_overrides", {}))
        apply_factor_overrides(escenarios, variante.get("factor_overrides", {}))

        barrios_emergencia = pick_emergency_barrios(
            gdf,
            variante["emergencia_comunas"],
            n=5,
        )

        gdf_esc = asignar_escenarios(
            gdf.copy(),
            escenarios_por_comuna=variante["escenarios_por_comuna"],
            barrios_emergencia=barrios_emergencia,
            escenarios_def=escenarios,
        )

        resultados = ejecutar_modelo_escenarios(
            escenarios_def=escenarios,
            contexto_escenario=variante["id"]  # 'lluvias_intensas', 'intermitencia_agua', etc.
        )

        mapa = crear_mapa(
            gdf_esc,
            resultados,
            escenarios_def=escenarios,
            mapa_titulo=variante["titulo"],
            mapa_subtitulo=variante["subtitulo"],
        )

        output = f"mapa_escenarios_dengue_{variante['id']}.html"
        mapa.save(output)
        outputs.append(output)

    return outputs


def generar_mapas_variantes_con_factores(factores_xlsx_path, sufijo="_medias", xlsx_path=XLSX_PATH):
    """
    Genera todos los mapas de variantes usando un archivo de factores específico.
    Los archivos se guardan con el sufijo indicado.
    """
    # Configurar el archivo de factores
    set_factores_xlsx_path(factores_xlsx_path)
    print(f"\n📊 Usando factores desde: {factores_xlsx_path}")

    thresholds, _ = cargar_umbral_y_dominios(xlsx_path)
    escenarios_base = construir_escenarios_base(thresholds, ESCENARIOS)

    gdf = cargar_shapefile()

    variantes = construir_variantes()
    outputs = []

    for variante in variantes:
        escenarios = deepcopy(escenarios_base)
        apply_indicator_overrides(escenarios, variante.get("indicator_overrides", {}))
        apply_factor_overrides(escenarios, variante.get("factor_overrides", {}))

        barrios_emergencia = pick_emergency_barrios(
            gdf,
            variante["emergencia_comunas"],
            n=5,
        )

        gdf_esc = asignar_escenarios(
            gdf.copy(),
            escenarios_por_comuna=variante["escenarios_por_comuna"],
            barrios_emergencia=barrios_emergencia,
            escenarios_def=escenarios,
        )

        resultados = ejecutar_modelo_escenarios(
            escenarios_def=escenarios,
            contexto_escenario=variante["id"]
        )

        mapa = crear_mapa(
            gdf_esc,
            resultados,
            escenarios_def=escenarios,
            mapa_titulo=variante["titulo"],
            mapa_subtitulo=variante["subtitulo"],
        )

        output = f"mapa_escenarios_dengue_{variante['id']}{sufijo}.html"
        mapa.save(output)
        outputs.append(output)

    return outputs


def generar_mapas_extremos_con_factores(factores_xlsx_path, sufijo="_medias", xlsx_path=XLSX_PATH):
    """
    Genera los mapas de escenarios extremos usando un archivo de factores específico.
    """
    # Configurar el archivo de factores
    set_factores_xlsx_path(factores_xlsx_path)

    gdf = cargar_shapefile()
    outputs = []

    # Mapa todos críticos
    mapa_criticos = generar_mapa_todos_criticos(gdf, xlsx_path)
    output_criticos = f"mapa_escenarios_dengue_todos_criticos{sufijo}.html"
    mapa_criticos.save(output_criticos)
    outputs.append(output_criticos)
    print(f"   ✅ Guardado: {output_criticos}")

    # Mapa todos verdes
    mapa_verdes = generar_mapa_todos_verdes(gdf, xlsx_path)
    output_verdes = f"mapa_escenarios_dengue_todos_verdes{sufijo}.html"
    mapa_verdes.save(output_verdes)
    outputs.append(output_verdes)
    print(f"   ✅ Guardado: {output_verdes}")

    return outputs


def generar_mapa_base_con_factores(factores_xlsx_path, sufijo="_medias"):
    """
    Genera el mapa base usando un archivo de factores específico.
    """
    from visualizacion_escenarios_mapa import main as vis_main, OUTPUT_HTML
    import visualizacion_escenarios_mapa as vis_module

    # Configurar el archivo de factores
    set_factores_xlsx_path(factores_xlsx_path)
    print(f"\n📊 Usando factores desde: {factores_xlsx_path}")

    # Cargar shapefile
    gdf = cargar_shapefile()

    # Asignar escenarios
    gdf = asignar_escenarios(gdf)

    # Ejecutar modelo MCDA
    resultados_mcda = ejecutar_modelo_escenarios()

    # Crear mapa
    mapa = crear_mapa(gdf, resultados_mcda)

    # Guardar con sufijo
    output = f"mapa_escenarios_dengue{sufijo}.html"
    mapa.save(output)
    print(f"   ✅ Guardado: {output}")

    return [output]


def main_medias():
    """Genera todos los mapas usando el archivo de medias."""
    print("=" * 80)
    print("GENERADOR DE MAPAS DE ESCENARIOS (MEDIAS)")
    print("=" * 80)

    factores_medias = "factores_por_estrategia-1.xlsx"
    sufijo = "_medias"

    # Generar mapa base con medias
    print("\n📍 Generando mapa base con medias...")
    outputs = generar_mapa_base_con_factores(factores_medias, sufijo)

    # Generar los 4 mapas de variantes contextuales con medias
    print("\n📍 Generando mapas de variantes contextuales con medias...")
    outputs_variantes = generar_mapas_variantes_con_factores(factores_medias, sufijo)
    outputs.extend(outputs_variantes)

    # Generar los 2 mapas de escenarios extremos con medias
    print("\n📍 Generando mapas de escenarios extremos con medias...")
    outputs_extremos = generar_mapas_extremos_con_factores(factores_medias, sufijo)
    outputs.extend(outputs_extremos)

    print("\n" + "=" * 80)
    print("✅ TODOS LOS MAPAS CON MEDIAS GENERADOS:")
    print("=" * 80)
    for out in outputs:
        print(f"   - {out}")

    return outputs


def main():
    print("=" * 80)
    print("GENERADOR DE MAPAS DE ESCENARIOS")
    print("=" * 80)

    # Generar los 4 mapas de variantes contextuales
    print("\n📍 Generando mapas de variantes contextuales...")
    outputs = generar_mapas_variantes()

    # Generar los 2 mapas de escenarios extremos
    print("\n📍 Generando mapas de escenarios extremos...")
    outputs_extremos = generar_mapas_extremos()
    outputs.extend(outputs_extremos)

    print("\n" + "=" * 80)
    print("✅ TODOS LOS MAPAS GENERADOS:")
    print("=" * 80)
    for out in outputs:
        print(f"   - {out}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--medias":
        main_medias()
    else:
        main()
