"""
Sistema de decisión multicriterio para evaluación de estrategias de control de dengue.

Utiliza scikit-criteria para realizar análisis MCDA (Multi-Criteria Decision Analysis)
combinando cumplimiento de indicadores y factores de aplicabilidad de estrategias.

Requisitos:
    pip install scikit-criteria numpy pandas openpyxl
"""

import numpy as np
import pandas as pd
import skcriteria as skc
from skcriteria.agg import simple
from pathlib import Path
import sys
import re
from datetime import datetime


def parse_threshold(umbral_str):
    """
    Extrae el operador y el valor del umbral desde una cadena.
    
    Ejemplos:
    - "< 70%" -> ("<", 70.0)
    - "> 3 casos/barrio" -> (">", 3.0)
    - "< 60% manzanas intervenidas" -> ("<", 60.0)
    - "Tipo II (≥ 6 semanas)" -> (">=", 6.0)
    - "≥ 50" -> (">=", 50.0)
    
    Args:
        umbral_str: Cadena con el umbral (puede contener operador y valor)
        
    Returns:
        Tupla (operador, valor) o (None, None) si no se puede parsear
    """
    if pd.isna(umbral_str) or not umbral_str:
        return None, None
    
    umbral_str = str(umbral_str).strip()
    
    # Normalizar símbolos unicode
    umbral_str = umbral_str.replace('≤', '<=').replace('≥', '>=')
    
    # Patrones para extraer operador y número (en orden de especificidad)
    patterns = [
        # Patrones con operadores compuestos primero
        (r'([<>])\s*=\s*(\d+\.?\d*)', lambda m: (m.group(1) + "=", float(m.group(2)))),
        # Patrones con operadores simples seguidos de número
        (r'([<>])\s*(\d+\.?\d*)', lambda m: (m.group(1), float(m.group(2)))),
        # Buscar dentro de paréntesis (ej: "Tipo II (≥ 6 semanas)")
        (r'\(([<>]=?)\s*(\d+\.?\d*)', lambda m: (m.group(1) + ("=" if "=" in m.group(1) else ""), float(m.group(2)))),
    ]
    
    for pattern, extractor in patterns:
        match = re.search(pattern, umbral_str)
        if match:
            op, val = extractor(match)
            # Normalizar operadores
            if op == '<=' or op == '≤':
                op = '<='
            elif op == '>=' or op == '≥':
                op = '>='
            elif len(op) == 1 and op in ['<', '>']:
                pass  # Ya está normalizado
            return op, val
    
    # Si no se encuentra patrón, intentar extraer solo el número
    number_match = re.search(r'(\d+\.?\d*)', umbral_str)
    if number_match:
        # Por defecto, usar >= si solo hay un número
        return '>=', float(number_match.group(1))
    
    return None, None


def load_strategies_from_xlsx(xlsx_path):
    """
    Lee un archivo XLSX con información de estrategias, indicadores, pesos y umbrales.
    
    El XLSX debe tener las columnas:
    - Estrategia: nombre de la estrategia
    - Indicador: nombre del indicador
    - Peso (Importancia): peso del indicador
    - Umbral Consensuado: umbral con operador (ej: "< 70%", "> 3 casos/barrio")
    - Dominio: dominio del indicador
    - Nivel Consenso (Umbral): nivel de consenso
    - N Expertos (Peso): número de expertos
    - N Respuestas (Umbral): número de respuestas
    
    Args:
        xlsx_path: Ruta al archivo XLSX
        
    Returns:
        Tupla (strategies_config, indicators, indicator_thresholds)
        - strategies_config: Diccionario con configuración de estrategias e indicadores con pesos
        - indicators: Lista de nombres únicos de indicadores
        - indicator_thresholds: Diccionario con umbrales y operadores por indicador
    """
    df = pd.read_excel(xlsx_path)
    
    # Normalizar nombres de columnas (eliminar espacios extra)
    df.columns = df.columns.str.strip()
    
    # Obtener lista única de indicadores
    indicators = sorted(df['Indicador'].unique().tolist())
    
    # Agrupar por estrategia
    strategies_config = {}
    indicator_thresholds = {}
    
    for estrategia in df['Estrategia'].unique():
        estrategia_df = df[df['Estrategia'] == estrategia]
        
        # Construir lista de indicadores con sus pesos
        indicators_list = []
        for _, row in estrategia_df.iterrows():
            indicador = row['Indicador']
            peso = float(row['Peso (Importancia)']) if pd.notna(row['Peso (Importancia)']) else 0.0
            
            indicators_list.append({
                "indicator": indicador,
                "weight": peso,
            })
            
            # Extraer umbral y operador del campo "Umbral Consensuado"
            umbral_str = row.get('Umbral Consensuado', '')
            op, threshold_val = parse_threshold(umbral_str)
            
            if op is not None and threshold_val is not None:
                indicator_thresholds[indicador] = {
                    "op": op,
                    "threshold": threshold_val,
                }
        
        strategies_config[estrategia] = indicators_list
    
    return strategies_config, indicators, indicator_thresholds


def normalize_strategy_weights(strategies_config):
    """
    Normaliza los pesos de cada estrategia para que sumen 1.0.
    
    Args:
        strategies_config: Diccionario con configuración de estrategias
    """
    for est, rules in strategies_config.items():
        total = sum(r["weight"] for r in rules)
        if total == 0:
            continue
        for r in rules:
            r["weight"] = r["weight"] / total


def check_condition(value, op, threshold):
    """
    Evalúa una condición comparativa entre un valor y un umbral.
    
    Args:
        value: Valor a evaluar
        op: Operador de comparación ("<", "<=", ">", ">=")
        threshold: Umbral de comparación
        
    Returns:
        True si la condición se cumple, False en caso contrario
        
    Raises:
        ValueError: Si el operador no es soportado
    """
    if value is None:
        return False
    if op == "<":
        return value < threshold
    if op == "<=":
        return value <= threshold
    if op == ">":
        return value > threshold
    if op == ">=":
        return value >= threshold
    raise ValueError(f"Operador no soportado: {op}")


def generate_smart_indicator_value(op, threshold):
    """
    Genera un valor aleatorio para un indicador basado en su umbral.
    El valor se genera en un rango alrededor del umbral para simular
    que puede cumplir o no con la condición.
    
    Ejemplos:
    - Si umbral es "< 60", genera un valor entre 55 y 65
    - Si umbral es "> 20", genera un valor entre 15 y 25
    - Si umbral es ">= 3", genera un valor entre -2 y 8
    
    Args:
        op: Operador de comparación ("<", "<=", ">", ">=")
        threshold: Valor del umbral
        
    Returns:
        Valor aleatorio en un rango alrededor del umbral
    """
    # Rango de variación: ±10 unidades alrededor del umbral
    variation = 10
    
    if op == "<" or op == "<=":
        # Para "< threshold", generar entre (threshold - variation) y (threshold + variation)
        # Esto permite que algunos valores cumplan y otros no
        min_val = threshold - variation
        max_val = threshold + variation
    elif op == ">" or op == ">=":
        # Para "> threshold", generar entre (threshold - variation) y (threshold + variation)
        min_val = threshold - variation
        max_val = threshold + variation
    else:
        # Si no hay operador válido, usar un rango por defecto
        min_val = threshold - variation
        max_val = threshold + variation
    
    return np.random.uniform(min_val, max_val)


def build_indicator_matrix(indicator_values, strategies_config, indicators, indicator_thresholds=None):
    """
    Construye una matriz de cumplimiento de indicadores por estrategia.
    
    Cada celda contiene el peso del indicador si la condición se cumple,
    o 0 si no se cumple o el indicador no está asociado a la estrategia.
    
    Args:
        indicator_values: Diccionario con valores de indicadores (clave: nombre indicador)
        strategies_config: Configuración de estrategias y sus indicadores con pesos
        indicators: Lista de nombres de indicadores
        indicator_thresholds: Diccionario opcional con umbrales y operadores por indicador.
                            Formato: {nombre_indicador: {"op": ">=", "threshold": 50}}
                            Si es None, se asume que todos los indicadores cumplen (sin validación)
        
    Returns:
        Tupla (matriz numpy, lista de nombres de estrategias)
    """
    strategy_names = list(strategies_config.keys())
    matrix = []

    for est in strategy_names:
        row = []
        rules = strategies_config[est]
        rule_by_ind = {r["indicator"]: r for r in rules}

        for ind in indicators:
            rule = rule_by_ind.get(ind)
            if rule is None:
                row.append(0.0)
            else:
                val = indicator_values.get(ind)
                if val is None:
                    row.append(0.0)
                else:
                    # Si hay umbrales definidos, verificar condición
                    if indicator_thresholds is not None and ind in indicator_thresholds:
                        threshold_config = indicator_thresholds[ind]
                        op = threshold_config.get("op", ">=")
                        threshold = threshold_config.get("threshold", 0)
                        ok = check_condition(val, op, threshold)
                        row.append(rule["weight"] if ok else 0.0)
                    else:
                        # Sin umbrales, usar el peso directamente (asume cumplimiento)
                        row.append(rule["weight"])
        matrix.append(row)

    return np.array(matrix), strategy_names


def normalize_criterion(values, maximize=True):
    """
    Normaliza un criterio al rango [0, 1] usando normalización min-max.
    
    Args:
        values: Array de valores a normalizar
        maximize: Si True, valores mayores son mejores. Si False, se invierte.
        
    Returns:
        Array normalizado en el rango [0, 1]
    """
    values = np.array(values)
    if len(values) == 0:
        return values
    min_val = values.min()
    max_val = values.max()
    if max_val == min_val:
        return np.ones_like(values)
    
    normalized = (values - min_val) / (max_val - min_val)
    
    if not maximize:
        normalized = 1.0 - normalized
    
    return normalized


# ============================================================================
# CLASIFICACIÓN DE ESTRATEGIAS POR TIPO DE RESPUESTA
# ============================================================================
# Cada estrategia se clasifica según su naturaleza de intervención:
# - inmediata: Control urgente, para emergencias (adulticidas, triage)
# - activa: Control activo de criaderos y vector (larvicidas, control físico)
# - preventiva: Educación y prevención sostenible (campañas, prácticas)
# - coordinacion: Articulación institucional y sostenibilidad
# - monitoreo: Vigilancia, alertas tempranas y tecnología

ESTRATEGIA_TIPO_RESPUESTA = {
    # INMEDIATA - Para emergencias y alto riesgo
    "Aplicar adulticidas químicos como malatión o deltametrina para el control rápido del vector adulto en espacios abiertos.": "inmediata",
    "Implementar rápidamente protocolos de triage y fortalecer la capacitación del personal de salud para el manejo clínico del dengue.": "inmediata",

    # ACTIVA - Control activo del vector
    "Aplicar larvicidas químicos en criaderos específicos de gran volumen donde no es viable el control físico, garantizando seguridad ambiental.": "activa",
    "Aplicar métodos biológicos para el control larvario del vector, incluyendo el uso de peces larvívoros y Bacillus thuringiensis.": "activa",
    "Implementar acciones de control físico en el entorno domiciliario y comunitario para reducir o eliminar criaderos del vector.": "activa",
    "Realizar identificación focalizada de criaderos mediante inspección directa y herramientas de georreferenciación.": "activa",
    "Fomentar el uso de medidas de protección individual, como repelente y barreras físicas, especialmente en grupos de riesgo.": "activa",

    # PREVENTIVA - Educación y sostenibilidad comunitaria
    "Promover prácticas preventivas sostenibles mediante campañas educativas, cambio de comportamiento social y vigilancia participativa.": "preventiva",
    "Difundir mensajes preventivos inmediatos a través de canales como SMS, redes sociales y altavoces en zonas de brote.": "preventiva",
    "Fortalecer la percepción de riesgo del dengue y promover prácticas preventivas comunitarias mediante información, educación y comunicación.": "preventiva",
    "Fortalecer la prevención individual frente al dengue mediante el uso de vacunas aprobadas en población objetivo según lineamientos nacionales.": "preventiva",

    # COORDINACION - Articulación institucional
    "Articular esfuerzos con los sectores de agua, saneamiento, educación y servicios públicos para acciones preventivas sostenibles.": "coordinacion",
    "Fortalecer la articulación institucional para asegurar la continuidad de las acciones de control y facilitar la entrada a predios.": "coordinacion",
    "Fortalecer la sostenibilidad del programa de control del dengue mediante inversión continua, alianzas y gestión de recursos.": "coordinacion",

    # MONITOREO - Vigilancia y tecnología
    "Utilizar datos meteorológicos y modelos de alerta temprana para anticipar condiciones favorables al vector.": "monitoreo",
    "Utilizar tecnologías innovadoras para el monitoreo y control focalizado del vector, como drones, sensores remotos o trampas inteligentes.": "monitoreo",
    "Monitorear condiciones climáticas y gestionar escorrentías o acumulaciones de agua que favorezcan criaderos.": "monitoreo",
    "Implementar estrategias de control vectorial basadas en biotecnología, como la liberación de mosquitos Wolbachia o técnica del insecto estéril.": "monitoreo",
    "Implementar programas de diagnóstico oportuno, tratamiento adecuado y acompañamiento a pacientes con dengue.": "monitoreo",
}

# ============================================================================
# MULTIPLICADORES DE URGENCIA POR NIVEL DE RIESGO
# ============================================================================
# Estos multiplicadores ajustan el score final de cada estrategia según
# el nivel de riesgo del escenario. Valores > 1 aumentan prioridad,
# valores < 1 reducen prioridad.

MULTIPLICADORES_URGENCIA = {
    # Nivel 1: Bajo riesgo - priorizar prevención y monitoreo
    "bajo_riesgo": {
        "inmediata": 0.2,      # Muy baja - no desperdiciar recursos químicos
        "activa": 0.5,         # Baja - control rutinario mínimo
        "preventiva": 1.8,     # Muy alta - momento ideal para educar
        "coordinacion": 1.5,   # Alta - fortalecer instituciones
        "monitoreo": 1.7,      # Alta - vigilancia activa
    },
    # Nivel 2: Riesgo moderado - control activo de criaderos, sin químicos fuertes
    "riesgo_moderado": {
        "inmediata": 0.4,      # Baja - reservar para crisis
        "activa": 1.6,         # Alta - controlar criaderos activamente
        "preventiva": 0.9,     # Normal - mantener educación
        "coordinacion": 1.2,   # Buena - preparar articulación
        "monitoreo": 1.3,      # Buena - intensificar vigilancia
    },
    # Nivel 3: Alto riesgo - TRANSICIÓN: inmediatas empiezan a dominar
    "alto_riesgo": {
        "inmediata": 1.8,      # Muy alta - adulticidas y triage son prioritarios
        "activa": 1.3,         # Alta pero menor que inmediata
        "preventiva": 0.4,     # Baja - ya no es momento de solo educar
        "coordinacion": 1.0,   # Normal - coordinar respuesta
        "monitoreo": 0.6,      # Baja - ya sabemos la situación
    },
    # Nivel 4: Emergencia - máxima prioridad a respuesta inmediata EXCLUSIVA
    "emergencia": {
        "inmediata": 2.5,      # Máxima - control químico urgente es LA prioridad
        "activa": 0.9,         # Moderada-baja - apoyo secundario
        "preventiva": 0.2,     # Mínima - no es momento de campañas
        "coordinacion": 0.7,   # Baja - ya debe estar coordinado
        "monitoreo": 0.3,      # Muy baja - acción sobre vigilancia
    },
}

# ============================================================================
# PRIORIZACIÓN POR CONTEXTO DE ESCENARIO
# ============================================================================
# Estos multiplicadores adicionales ajustan según el tipo de escenario
# específico (lluvias, intermitencia de agua, movilidad, saturación)

CONTEXTO_ESCENARIO = {
    # Escenario A: Lluvias intensas - priorizar control de sumideros y drenajes
    "lluvias_intensas": {
        "Monitorear condiciones climáticas y gestionar escorrentías": 1.8,
        "Realizar identificación focalizada de criaderos": 1.5,
        "Implementar acciones de control físico": 1.4,
        "Utilizar datos meteorológicos": 1.6,
        "Aplicar larvicidas químicos": 1.3,
    },
    # Escenario B: Intermitencia de agua - priorizar control de depósitos domésticos
    "intermitencia_agua": {
        "Implementar acciones de control físico": 1.7,  # Eliminar depósitos
        "Realizar identificación focalizada de criaderos": 1.6,
        "Promover prácticas preventivas": 1.4,  # Tapar tanques
        "Fortalecer la percepción de riesgo": 1.3,
        "Aplicar larvicidas químicos": 1.5,  # Tratar tanques
        "Articular esfuerzos con los sectores de agua": 1.6,
    },
    # Escenario C: Movilidad y eventos - priorizar vigilancia epidemiológica
    "movilidad_eventos": {
        "Implementar programas de diagnóstico oportuno": 1.7,
        "Implementar rápidamente protocolos de triage": 1.5,
        "Difundir mensajes preventivos inmediatos": 1.6,
        "Fomentar el uso de medidas de protección individual": 1.5,
        "Utilizar tecnologías innovadoras para el monitoreo": 1.4,
    },
    # Escenario D: Saturación operativa - priorizar eficiencia y coordinación
    "saturacion_operativa": {
        "Fortalecer la articulación institucional": 1.7,
        "Fortalecer la sostenibilidad del programa": 1.5,
        "Aplicar adulticidas químicos": 1.4,  # Rápido impacto con pocos recursos
        "Implementar rápidamente protocolos de triage": 1.6,
        "Articular esfuerzos con los sectores": 1.5,
    },

    # =========================================================================
    # CONTEXTOS PARA PERFILES CRÍTICOS (Escenario Todos Críticos)
    # Multiplicadores: >1 = priorizar, <1 = despriozar
    # =========================================================================

    # Perfil: Zona con intermitencia de agua - tanques y depósitos domésticos
    "agua_intermitente": {
        "Implementar acciones de control físico": 6.0,  # PRIORIDAD: Tanques
        "Aplicar larvicidas químicos": 5.0,  # Tratar tanques y albercas
        "Articular esfuerzos con los sectores de agua": 4.5,  # Coordinar acueducto
        "Promover prácticas preventivas": 4.0,  # Tapar recipientes
        "métodos biológicos": 0.3,  # Reducir - no aplica bien aquí
        "adulticidas": 0.4,  # Reducir - no es la prioridad
    },

    # Perfil: Zona de alta densidad - control rápido y protección individual
    "alta_densidad": {
        "Aplicar adulticidas químicos": 6.0,  # PRIORIDAD: Fumigación masiva
        "Fomentar el uso de medidas de protección individual": 5.5,  # Repelentes
        "Implementar rápidamente protocolos de triage": 5.0,  # Atención médica
        "Implementar programas de diagnóstico oportuno": 4.5,
        "métodos biológicos": 0.2,  # Reducir - muy lento para emergencia
        "control físico": 0.4,  # Reducir - muy lento
    },

    # Perfil: Zona de construcciones - sumideros y escorrentías
    "construcciones": {
        "Monitorear condiciones climáticas y gestionar escorrentías": 6.0,  # PRIORIDAD
        "Utilizar tecnologías innovadoras": 5.5,  # Drones para mapeo
        "Articular esfuerzos con los sectores": 5.0,  # Constructoras
        "Realizar identificación focalizada de criaderos": 4.5,  # Sumideros
        "métodos biológicos": 0.3,  # Reducir
        "adulticidas": 0.5,  # Reducir - no es foco principal
    },

    # Perfil: Zona de difícil acceso - tecnología y comunidad
    "dificil_acceso": {
        "Utilizar tecnologías innovadoras": 6.0,  # PRIORIDAD: Drones, sensores
        "Aplicar métodos biológicos": 5.5,  # SÍ aplica: Peces larvívoros
        "Fortalecer la articulación institucional": 5.0,  # Juntas comunales
        "Promover prácticas preventivas": 4.5,  # Autogestión
        "adulticidas": 0.3,  # Reducir - difícil aplicar sin acceso
        "larvicidas químicos": 0.4,  # Reducir
    },

    # Perfil: Zona con rechazo comunitario - educación y comunicación
    "rechazo_comunitario": {
        "Fortalecer la percepción de riesgo": 6.0,  # PRIORIDAD: Sensibilización
        "Difundir mensajes preventivos": 5.5,  # Comunicación masiva
        "Promover prácticas preventivas": 5.0,  # Educación
        "Fortalecer la articulación institucional": 4.5,  # Líderes locales
        "métodos biológicos": 0.3,  # Reducir - requiere acceso
        "adulticidas": 0.3,  # Reducir - generará más rechazo
        "larvicidas": 0.4,  # Reducir
    },

    # =========================================================================
    # CONTEXTOS PARA PERFILES VERDES (Escenario Todos Verdes)
    # =========================================================================

    # Perfil: Zona históricamente problemática - vigilancia intensiva
    "historicamente_problematica": {
        "Realizar identificación focalizada de criaderos": 6.0,  # PRIORIDAD
        "Utilizar tecnologías innovadoras": 5.5,  # Ovitrampas
        "Utilizar datos meteorológicos": 5.0,  # Alertas tempranas
        "métodos biológicos": 0.4,  # Reducir - no es vigilancia
        "adulticidas": 0.3,  # Reducir - no hay brote
    },

    # Perfil: Zona bien organizada - vigilancia participativa
    "bien_organizada": {
        "Promover prácticas preventivas": 6.0,  # PRIORIDAD: Comunidad activa
        "Fortalecer la percepción de riesgo": 5.5,  # Mantener alerta
        "Difundir mensajes preventivos": 5.0,  # Lideradas por comunidad
        "métodos biológicos": 0.4,  # Reducir
        "adulticidas": 0.2,  # Reducir - no hay brote
        "larvicidas": 0.3,  # Reducir
    },

    # Perfil: Zona con buena infraestructura - monitoreo tecnológico
    "buena_infraestructura": {
        "Utilizar tecnologías innovadoras": 6.0,  # PRIORIDAD: Sensores, IoT
        "Utilizar datos meteorológicos": 5.5,  # Modelos predictivos
        "Monitorear condiciones climáticas": 5.0,
        "métodos biológicos": 0.4,  # Reducir
        "adulticidas": 0.2,  # Reducir
        "larvicidas": 0.3,  # Reducir
    },

    # Perfil: Zona con cobertura de agua variable - educación en almacenamiento
    "cobertura_agua_variable": {
        "Promover prácticas preventivas": 6.0,  # PRIORIDAD: Almacenamiento seguro
        "Implementar acciones de control físico": 5.5,  # Tapar tanques
        "Articular esfuerzos con los sectores de agua": 5.0,  # Alertar cortes
        "métodos biológicos": 0.4,  # Reducir
        "adulticidas": 0.2,  # Reducir
    },

    # Perfil: Zona en transición - consolidar logros
    "transicion": {
        "Fortalecer la sostenibilidad del programa": 6.0,  # PRIORIDAD: Mantener
        "Promover prácticas preventivas": 5.5,  # Continuar educación
        "Realizar identificación focalizada de criaderos": 5.0,  # No bajar guardia
        "métodos biológicos": 0.4,  # Reducir
        "adulticidas": 0.2,  # Reducir
        "larvicidas": 0.3,  # Reducir
    },
}

def get_tipo_respuesta(estrategia):
    """
    Obtiene el tipo de respuesta de una estrategia.
    Busca coincidencia exacta o parcial.

    Args:
        estrategia: Nombre de la estrategia

    Returns:
        Tipo de respuesta ('inmediata', 'activa', 'preventiva', 'coordinacion', 'monitoreo')
        Por defecto retorna 'activa' si no encuentra coincidencia.
    """
    # Buscar coincidencia exacta
    if estrategia in ESTRATEGIA_TIPO_RESPUESTA:
        return ESTRATEGIA_TIPO_RESPUESTA[estrategia]

    # Buscar coincidencia parcial (primeros 50 caracteres)
    est_norm = estrategia.strip()[:50].lower()
    for est_key, tipo in ESTRATEGIA_TIPO_RESPUESTA.items():
        if est_key.strip()[:50].lower() == est_norm:
            return tipo

    # Por defecto, retornar 'activa' (intermedio)
    return "activa"


def aplicar_multiplicador_urgencia(scores, strategy_names, nivel_riesgo, contexto_escenario=None):
    """
    Aplica multiplicadores de urgencia a los scores según el nivel de riesgo
    y opcionalmente el contexto específico del escenario.

    Args:
        scores: Array de scores de las estrategias
        strategy_names: Lista de nombres de estrategias
        nivel_riesgo: Nivel de riesgo ('bajo_riesgo', 'riesgo_moderado', 'alto_riesgo', 'emergencia')
        contexto_escenario: Contexto opcional ('lluvias_intensas', 'intermitencia_agua', etc.)

    Returns:
        Array de scores ajustados
    """
    import numpy as np

    if nivel_riesgo not in MULTIPLICADORES_URGENCIA:
        return scores  # Sin cambios si el nivel no existe

    multiplicadores = MULTIPLICADORES_URGENCIA[nivel_riesgo]

    # Obtener multiplicadores de contexto si existe
    mult_contexto = {}
    if contexto_escenario and contexto_escenario in CONTEXTO_ESCENARIO:
        mult_contexto = CONTEXTO_ESCENARIO[contexto_escenario]

    scores_ajustados = np.zeros_like(scores)

    for i, (score, est_name) in enumerate(zip(scores, strategy_names)):
        tipo = get_tipo_respuesta(est_name)
        mult_nivel = multiplicadores.get(tipo, 1.0)

        # Buscar multiplicador de contexto (coincidencia parcial)
        mult_ctx = 1.0
        for ctx_key, ctx_mult in mult_contexto.items():
            if ctx_key.lower() in est_name.lower():
                mult_ctx = ctx_mult
                break

        # Aplicar ambos multiplicadores
        scores_ajustados[i] = score * mult_nivel * mult_ctx

    # Normalizar a rango [0, 1] para presentación
    if len(scores_ajustados) > 0:
        max_score = scores_ajustados.max()
        if max_score > 0:
            scores_ajustados = scores_ajustados / max_score

    return scores_ajustados


# Nombres de los 11 factores de aplicabilidad
FACTOR_NAMES = [
    "disponibilidad_recursos",
    "costo_operativo",
    "tiempo_cobertura",
    "dependencias_externas",
    "aceptacion_comunidad",
    "acceso_predios",
    "percepcion_riesgo",
    "resistencia_vector",
    "otros_vectores",
    "efectividad_esperada",
    "magnitud_brote",
]

FACTOR_DESCRIPTIONS = [
    "Disponibilidad de personal capacitado, equipos, vehículos e insumos",
    "Costo operativo",
    "Tiempo de alistamiento, ejecución o posibilidad de cubrir territorio",
    "Requerir activar otras dependencias",
    "Aceptación de la comunidad",
    "Posibilidad real de entrar a predios o edificaciones",
    "Percepción de riesgo de la comunidad",
    "Conocimiento de resistencia/susceptibilidad del vector",
    "Presencia de otros vectores o múltiples focos activos",
    "Efectividad esperada",
    "Magnitud del brote",
]

# ============================================================================
# VALORES DE EVALUACIÓN DE FACTORES (MODIFICABLE)
# ============================================================================
# Valores entre -1 y 1 que representan la evaluación del contexto actual.
#
# Escala:
#   +1.0 = Condición muy favorable / Máxima prioridad
#    0.0 = Condición neutra / Normal
#   -1.0 = Condición muy desfavorable / Baja prioridad
#
# Algunos factores son GENERALES (mismo valor para todas las estrategias)
# Otros factores son ESPECÍFICOS (varían según la estrategia)

# ID del pixel sobre el que se hace la prescripción
PIXEL_ID = 103

# Temporalidad de actualización de cada factor
FACTOR_TEMPORALITY = {
    "disponibilidad_recursos": "Mensual",
    "costo_operativo": "Semestral",
    "tiempo_cobertura": "Mensual",
    "dependencias_externas": "Mensual",
    "aceptacion_comunidad": "Anual",
    "acceso_predios": "Mensual",
    "percepcion_riesgo": "Anual",
    "resistencia_vector": "Semestral",
    "otros_vectores": "Trimestral",
    "efectividad_esperada": "Mensual",
    "magnitud_brote": "Semanal",
}

# Factores GENERALES (no varían entre estrategias)
FACTOR_VALUES_GENERAL = {
    "percepcion_riesgo": 0.8,        # Alto riesgo percibido (Anual)
    "resistencia_vector": 0.5,       # Resistencia moderada (Semestral)
    "otros_vectores": 0.3,           # Algunos otros vectores (Trimestral)
    "magnitud_brote": 0.7,           # Brote significativo (Semanal)
}

# Factores ESPECÍFICOS POR ESTRATEGIA (valores ejemplo para 19 estrategias)
# En producción, estos valores vendrían de una base de datos o sistema de monitoreo
# Aquí se definen valores específicos para algunas estrategias como ejemplo
FACTOR_VALUES_BY_STRATEGY = {
    # Estrategias con control químico (generalmente más costosas, rápidas)
    "Aplicar adulticidas químicos como malatión o deltametrina para el control rápido del vector adulto en espacios abiertos.": {
        "disponibilidad_recursos": 0.6,
        "costo_operativo": -0.4,      # Costoso
        "tiempo_cobertura": 0.9,       # Rápido
        "dependencias_externas": 0.2,
        "aceptacion_comunidad": 0.5,
        "acceso_predios": 0.7,
        "efectividad_esperada": 0.8,
    },
    "Aplicar larvicidas químicos en criaderos específicos de gran volumen donde el control físico no es posible.": {
        "disponibilidad_recursos": 0.7,
        "costo_operativo": -0.2,      # Moderadamente costoso
        "tiempo_cobertura": 0.7,
        "dependencias_externas": 0.1,
        "aceptacion_comunidad": 0.6,
        "acceso_predios": 0.6,
        "efectividad_esperada": 0.9,
    },
    
    # Estrategias biológicas (más económicas, mayor aceptación)
    "Aplicar métodos biológicos para el control larvario del vector, incluyendo el uso de peces larvívoros y Bacillus thuringiensis.": {
        "disponibilidad_recursos": 0.5,
        "costo_operativo": 0.3,       # Económico
        "tiempo_cobertura": 0.4,      # Más lento
        "dependencias_externas": 0.3,
        "aceptacion_comunidad": 0.8,
        "acceso_predios": 0.5,
        "efectividad_esperada": 0.7,
    },
    
    # Estrategias de coordinación (dependen de otros sectores)
    "Articular esfuerzos con los sectores de agua, saneamiento, educación y servicios públicos para acciones preventivas sostenibles.": {
        "disponibilidad_recursos": 0.4,
        "costo_operativo": 0.2,
        "tiempo_cobertura": 0.2,      # Lento (largo plazo)
        "dependencias_externas": -0.6, # Alta dependencia
        "aceptacion_comunidad": 0.7,
        "acceso_predios": 0.6,
        "efectividad_esperada": 0.6,
    },
    
    # Estrategias educativas (bajo costo, alta aceptación, largo plazo)
    "Promover prácticas preventivas sostenibles mediante campañas educativas, capacitación comunitaria y vigilancia participativa.": {
        "disponibilidad_recursos": 0.6,
        "costo_operativo": 0.5,       # Bajo costo
        "tiempo_cobertura": 0.3,      # Lento
        "dependencias_externas": 0.2,
        "aceptacion_comunidad": 0.9,
        "acceso_predios": 0.8,
        "efectividad_esperada": 0.5,
    },
    
    # Estrategias de control físico (moderado costo, acceso variable)
    "Implementar acciones de control físico en el entorno domiciliario y comunitario para reducir o eliminar criaderos del vector.": {
        "disponibilidad_recursos": 0.6,
        "costo_operativo": 0.1,
        "tiempo_cobertura": 0.6,
        "dependencias_externas": 0.1,
        "aceptacion_comunidad": 0.7,
        "acceso_predios": 0.4,        # Requiere acceso a viviendas
        "efectividad_esperada": 0.8,
    },
    
    # Valores por defecto para el resto de estrategias
    # Estos valores se usan cuando no hay configuración específica
    "_default": {
        "disponibilidad_recursos": 0.5,
        "costo_operativo": 0.0,
        "tiempo_cobertura": 0.5,
        "dependencias_externas": 0.0,
        "aceptacion_comunidad": 0.5,
        "acceso_predios": 0.5,
        "efectividad_esperada": 0.6,
    }
}


def build_mcda_matrix(indicator_matrix, strategy_names, strategy_factors, 
                      factor_values_by_strategy, factor_values_general, normalize=True):
    """
    Construye la matriz MCDA con 2 criterios:
    1. Cumplimiento de indicadores (50%)
    2. Score de factores (50%): suma de (factor_estrategia x factor_valor_contexto)
    
    Los factores de contexto pueden ser:
    - Generales: mismo valor para todas las estrategias
    - Específicos: valor único por estrategia
    
    Args:
        indicator_matrix: Matriz de cumplimiento de indicadores por estrategia
        strategy_names: Lista de nombres de estrategias
        strategy_factors: Diccionario con los 11 factores por estrategia (valores 0-10)
        factor_values_by_strategy: Diccionario con valores específicos por estrategia (-1 a 1)
        factor_values_general: Diccionario con valores generales (-1 a 1)
        normalize: Si True, normaliza todos los criterios a [0, 1]
        
    Returns:
        Tupla (matriz MCDA, nombres de criterios, scores_factores_raw)
    """
    # 1. Cumplimiento de indicadores
    compliance = indicator_matrix.sum(axis=1)

    # 2. Score de factores: suma de productos
    factor_scores = []
    for est in strategy_names:
        score_total = 0.0
        factors = strategy_factors.get(est, {})
        
        # Si no se encuentra la estrategia, buscar coincidencia parcial
        if not factors:
            for est_key in strategy_factors.keys():
                est_normalized = est.strip()
                est_key_normalized = str(est_key).strip()
                if (len(est_normalized) > 30 and len(est_key_normalized) > 30 and 
                    est_normalized[:30] == est_key_normalized[:30]):
                    factors = strategy_factors[est_key]
                    break
                elif est_normalized in est_key_normalized or est_key_normalized in est_normalized:
                    factors = strategy_factors[est_key]
                    break
        
        # Obtener valores de contexto para esta estrategia
        strategy_context_values = factor_values_by_strategy.get(est, 
                                   factor_values_by_strategy.get("_default", {}))
        
        # Calcular suma de productos
        for factor_name in FACTOR_NAMES:
            factor_estrategia = float(factors.get(factor_name, 0))
            
            # Usar valor general si existe, sino usar valor específico de estrategia
            if factor_name in factor_values_general:
                factor_contexto = factor_values_general[factor_name]
            else:
                factor_contexto = strategy_context_values.get(factor_name, 0)
            
            score_total += factor_estrategia * factor_contexto
        
        factor_scores.append(score_total)
    
    factor_scores = np.array(factor_scores)

    # Normalizar ambos criterios a [0, 1]
    if normalize:
        compliance_norm = normalize_criterion(compliance, maximize=True)
        factor_scores_norm = normalize_criterion(factor_scores, maximize=True)
        
        mcda_matrix = np.column_stack([compliance_norm, factor_scores_norm])
        criteria_names = ["cumplimiento_indicadores", "score_factores"]
    else:
        mcda_matrix = np.column_stack([compliance, factor_scores])
        criteria_names = ["cumplimiento_indicadores", "score_factores"]

    return mcda_matrix, criteria_names, factor_scores


def generate_markdown_report(
    xlsx_path,
    strategies_config,
    indicators,
    indicator_thresholds,
    indicator_values,
    strategy_names,
    strategy_factors,
    mcda_matrix,
    criteria_names,
    result,
    factor_scores_raw,
    output_path=None
):
    """
    Genera un reporte en formato Markdown con los resultados del análisis MCDA.
    
    Args:
        xlsx_path: Ruta del archivo XLSX de entrada
        strategies_config: Configuración de estrategias
        indicators: Lista de indicadores
        indicator_thresholds: Umbrales por indicador
        indicator_values: Valores de indicadores
        strategy_names: Nombres de estrategias
        strategy_factors: Factores por estrategia
        mcda_matrix: Matriz MCDA
        criteria_names: Nombres de criterios
        result: Resultado de la evaluación MCDA
        output_path: Ruta del archivo de salida (opcional)
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"reporte_mcda_{timestamp}.md"
    
    md_lines = []
    
    # Encabezado
    md_lines.append("# 📊 Reporte de Análisis MCDA - Estrategias de Control de Dengue\n")
    md_lines.append(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_lines.append(f"**Archivo de entrada:** `{xlsx_path}`\n")
    md_lines.append("---\n")
    
    # Resumen ejecutivo
    md_lines.append("## 📋 Resumen Ejecutivo\n")
    md_lines.append(f"- **Total de estrategias evaluadas:** {len(strategy_names)}")
    md_lines.append(f"- **Total de indicadores únicos:** {len(indicators)}")
    md_lines.append(f"- **Total de criterios MCDA:** 2 (Cumplimiento 50% + Factores 50%)")
    md_lines.append(f"- **Umbrales configurados:** {len(indicator_thresholds)}\n")
    md_lines.append("---\n")
    
    # Valores de evaluación de factores
    md_lines.append(f"## ⚙️ Valores de Evaluación de Factores (Contexto Actual)\n")
    md_lines.append(f"**ID Pixel:** `{PIXEL_ID}`\n")
    md_lines.append("### Factores GENERALES (mismo valor para todas las estrategias)\n")
    md_lines.append("| Factor | Temporalidad | Valor | Interpretación |")
    md_lines.append("|--------|--------------|-------|----------------|")
    
    for factor_name in FACTOR_NAMES:
        if factor_name in FACTOR_VALUES_GENERAL:
            valor = FACTOR_VALUES_GENERAL[factor_name]
            temporalidad = FACTOR_TEMPORALITY.get(factor_name, "N/A")
            
            if valor > 0.7:
                interp = "🟢 Muy favorable"
            elif valor > 0.3:
                interp = "🟢 Favorable"
            elif valor > -0.3:
                interp = "🟡 Neutro"
            elif valor > -0.7:
                interp = "🔴 Desfavorable"
            else:
                interp = "🔴 Muy desfavorable"
            
            idx = FACTOR_NAMES.index(factor_name)
            md_lines.append(f"| {FACTOR_DESCRIPTIONS[idx]} | {temporalidad} | {valor:+.2f} | {interp} |")
    
    md_lines.append("")
    md_lines.append("### Factores ESPECÍFICOS POR ESTRATEGIA\n")
    md_lines.append("Estos factores varían según la estrategia seleccionada:\n")
    
    # Lista de factores específicos
    specific_factors = [f for f in FACTOR_NAMES if f not in FACTOR_VALUES_GENERAL]
    md_lines.append("| Factor | Temporalidad |")
    md_lines.append("|--------|--------------|")
    for factor_name in specific_factors:
        temporalidad = FACTOR_TEMPORALITY.get(factor_name, "N/A")
        idx = FACTOR_NAMES.index(factor_name)
        md_lines.append(f"| {FACTOR_DESCRIPTIONS[idx]} | {temporalidad} |")
    md_lines.append("")
    
    # Mostrar valores por estrategia (primeras 3 estrategias como ejemplo)
    md_lines.append("#### Valores por Estrategia (muestra de 3 estrategias)\n")
    
    sample_strategies = list(strategy_names)[:3]
    for est in sample_strategies:
        est_short = est[:60] + "..." if len(est) > 60 else est
        md_lines.append(f"**{est_short}**\n")
        md_lines.append("| Factor | Valor | Interpretación |")
        md_lines.append("|--------|-------|----------------|")
        
        strategy_values = FACTOR_VALUES_BY_STRATEGY.get(est, 
                         FACTOR_VALUES_BY_STRATEGY.get("_default", {}))
        
        for factor_name in specific_factors:
            valor = strategy_values.get(factor_name, 0)
            
            if valor > 0.7:
                interp = "🟢 Muy favorable"
            elif valor > 0.3:
                interp = "🟢 Favorable"
            elif valor > -0.3:
                interp = "🟡 Neutro"
            elif valor > -0.7:
                interp = "🔴 Desfavorable"
            else:
                interp = "🔴 Muy desfavorable"
            
            idx = FACTOR_NAMES.index(factor_name)
            md_lines.append(f"| {FACTOR_DESCRIPTIONS[idx][:40]}... | {valor:+.2f} | {interp} |")
        md_lines.append("")
    
    md_lines.append("*Nota: Los valores mostrados son ejemplos. El resto de estrategias usa valores por defecto.*\n")
    md_lines.append("*Escala: +1.0 = Muy favorable, 0.0 = Neutro, -1.0 = Muy desfavorable*\n")
    md_lines.append("---\n")
    
    # Estrategias cargadas
    md_lines.append("## 🎯 Estrategias Evaluadas\n")
    md_lines.append("| # | Estrategia | # Indicadores |")
    md_lines.append("|---|------------|---------------|")
    for i, est in enumerate(strategy_names, 1):
        num_indicadores = len(strategies_config[est])
        est_short = est[:80] + "..." if len(est) > 80 else est
        # Escapar pipes en el texto
        est_short = est_short.replace("|", "\\|")
        md_lines.append(f"| {i} | {est_short} | {num_indicadores} |")
    md_lines.append("")
    
    # Indicadores y umbrales
    md_lines.append("## 📈 Indicadores y Umbrales\n")
    md_lines.append("| Indicador | Valor | Umbral | Estado |")
    md_lines.append("|-----------|-------|--------|--------|")
    
    compliance = mcda_matrix[:, 0]
    # Mostrar TODOS los indicadores
    for ind in indicators:
        val = indicator_values.get(ind, 0.0)
        threshold_info = indicator_thresholds.get(ind, {})
        
        if threshold_info:
            op = threshold_info.get('op', 'N/A')
            threshold = threshold_info.get('threshold', 'N/A')
            # Determinar estado
            if op != 'N/A' and threshold != 'N/A':
                ok = check_condition(val, op, threshold)
                estado = "✅ Cumple" if ok else "❌ No cumple"
                umbral_str = f"{op} {threshold}"
            else:
                estado = "⚠️ Sin umbral"
                umbral_str = "N/A"
        else:
            estado = "⚠️ Sin umbral"
            umbral_str = "N/A"
        
        # No truncar el nombre del indicador, mostrar completo
        ind_full = ind
        # Escapar pipes en el texto
        ind_full = ind_full.replace("|", "\\|")
        md_lines.append(f"| {ind_full} | {val:.2f} | {umbral_str} | {estado} |")
    
    md_lines.append("")
    
    # Cumplimiento por estrategia
    md_lines.append("## ✅ Cumplimiento de Indicadores por Estrategia\n")
    md_lines.append("| # | Estrategia | Cumplimiento (normalizado) |")
    md_lines.append("|---|------------|----------------------------|")
    
    ranking_compliance = sorted(
        zip(strategy_names, compliance),
        key=lambda x: x[1],
        reverse=True
    )
    
    for i, (est, c) in enumerate(ranking_compliance, 1):
        est_short = est[:70] + "..." if len(est) > 70 else est
        # Escapar pipes en el texto
        est_short = est_short.replace("|", "\\|")
        # Barra de progreso visual
        bar_length = int(c * 20)  # Escalar a 20 caracteres
        bar = "█" * bar_length + "░" * (20 - bar_length)
        md_lines.append(f"| {i} | {est_short} | {c:.3f} {bar} |")
    md_lines.append("")
    
    # Score de factores por estrategia
    md_lines.append("## 🔧 Score de Factores por Estrategia\n")
    md_lines.append("Score calculado como: Σ(factor_estrategia × factor_contexto)\n")
    md_lines.append("| # | Estrategia | Score Factores (raw) | Score Normalizado |")
    md_lines.append("|---|------------|----------------------|-------------------|")
    
    # Combinar scores raw y normalizados
    factor_scores_norm = mcda_matrix[:, 1]
    ranking_factors = sorted(
        zip(strategy_names, factor_scores_raw, factor_scores_norm),
        key=lambda x: x[2],
        reverse=True
    )
    
    for i, (est, score_raw, score_norm) in enumerate(ranking_factors, 1):
        est_short = est[:60] + "..." if len(est) > 60 else est
        # Escapar pipes en el texto
        est_short = est_short.replace("|", "\\|")
        # Barra de progreso visual
        bar_length = int(score_norm * 20)  # Escalar a 20 caracteres
        bar = "█" * bar_length + "░" * (20 - bar_length)
        md_lines.append(f"| {i} | {est_short} | {score_raw:.2f} | {score_norm:.3f} {bar} |")
    md_lines.append("")
    
    # Ranking final
    md_lines.append("## 🏆 Ranking Final de Estrategias\n")
    md_lines.append("Modelo MCDA: 50% Cumplimiento Indicadores + 50% Score Factores\n")
    md_lines.append("| Rank | Estrategia | Score Final | Score Indicadores (50%) | Score Factores (50%) |")
    md_lines.append("|------|------------|-------------|-------------------------|----------------------|")
    
    # Combinar todos los scores
    compliance_norm = mcda_matrix[:, 0]
    factor_scores_norm = mcda_matrix[:, 1]
    
    ranking = sorted(
        zip(result.alternatives, result.rank_, result.e_.score, compliance_norm, factor_scores_norm),
        key=lambda x: x[1],
    )
    
    for est, rank, score, comp_norm, fact_norm in ranking:
        est_short = est[:50] + "..." if len(est) > 50 else est
        # Escapar pipes en el texto
        est_short = est_short.replace("|", "\\|")
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
        # Calcular contribución de cada componente al score final
        contrib_indicadores = comp_norm * 0.5
        contrib_factores = fact_norm * 0.5
        md_lines.append(f"| {rank} {medal} | {est_short} | {score:.4f} | {contrib_indicadores:.4f} | {contrib_factores:.4f} |")
    md_lines.append("")
    
    # Top 3 estrategias detalladas
    md_lines.append("## 🌟 Top 3 Estrategias - Análisis Detallado\n")
    
    for rank_idx, (est, rank, score, comp_norm, fact_norm) in enumerate(ranking[:3], 1):
        md_lines.append(f"### {rank}. {est}\n")
        md_lines.append(f"- **Score Final:** `{score:.4f}`")
        md_lines.append(f"  - Cumplimiento Indicadores (50%): `{comp_norm:.3f}` → Contribución: `{comp_norm * 0.5:.4f}`")
        md_lines.append(f"  - Score Factores (50%): `{fact_norm:.3f}` → Contribución: `{fact_norm * 0.5:.4f}`")
        md_lines.append(f"- **Número de Indicadores:** {len(strategies_config[est])}\n")
        
        # Factores y cálculo del score
        md_lines.append("**Cálculo del Score de Factores:**\n")
        md_lines.append("Score = Σ(factor_estrategia × factor_contexto)\n")
        factors = strategy_factors.get(est, {})
        
        # Si no se encuentra la estrategia exacta, intentar búsqueda flexible
        if not factors:
            # Buscar por coincidencia parcial (primeros caracteres)
            est_normalized = est.strip()
            for est_key in strategy_factors.keys():
                est_key_normalized = str(est_key).strip()
                # Comparar primeros 30 caracteres o si uno contiene al otro
                if (len(est_normalized) > 30 and len(est_key_normalized) > 30 and 
                    est_normalized[:30] == est_key_normalized[:30]):
                    factors = strategy_factors.get(est_key, {})
                    break
                elif est_normalized in est_key_normalized or est_key_normalized in est_normalized:
                    factors = strategy_factors.get(est_key, {})
                    break
        
        # Obtener valores de contexto para esta estrategia
        strategy_context_values = FACTOR_VALUES_BY_STRATEGY.get(est, 
                                  FACTOR_VALUES_BY_STRATEGY.get("_default", {}))
        
        # Si aún no hay factores, mostrar advertencia
        if not factors:
            md_lines.append("⚠️ No se encontraron factores para esta estrategia en el archivo.\n")
            md_lines.append(f"   (Buscando: '{est[:50]}...')\n")
        else:
            score_total_calc = 0.0
            md_lines.append("| Factor | Temporalidad | Tipo | Valor Est. | Valor Ctx. | Producto |")
            md_lines.append("|--------|--------------|------|------------|------------|----------|")
            for i, factor_name in enumerate(FACTOR_NAMES):
                factor_val_est = factors.get(factor_name, 0)
                temporalidad = FACTOR_TEMPORALITY.get(factor_name, "N/A")
                
                # Determinar si es general o específico
                if factor_name in FACTOR_VALUES_GENERAL:
                    factor_val_ctx = FACTOR_VALUES_GENERAL[factor_name]
                    tipo = "General"
                else:
                    factor_val_ctx = strategy_context_values.get(factor_name, 0)
                    tipo = "Específico"
                
                try:
                    factor_val_est_float = float(factor_val_est) if factor_val_est is not None else 0.0
                    producto = factor_val_est_float * factor_val_ctx
                    score_total_calc += producto
                except (ValueError, TypeError):
                    factor_val_est_float = 0.0
                    producto = 0.0
                
                md_lines.append(f"| {FACTOR_DESCRIPTIONS[i][:35]}... | {temporalidad[:8]} | {tipo[:8]} | {factor_val_est_float:.2f} | {factor_val_ctx:+.2f} | {producto:+.2f} |")
            md_lines.append(f"| **TOTAL** | | | | | **{score_total_calc:+.2f}** |")
        md_lines.append("")
        
        # Indicadores asociados - mostrar TODOS
        md_lines.append("**Indicadores Asociados:**\n")
        indicators_est = [r["indicator"] for r in strategies_config[est]]
        for ind in indicators_est:
            val = indicator_values.get(ind, 0.0)
            threshold_info = indicator_thresholds.get(ind, {})
            if threshold_info:
                op = threshold_info.get('op', 'N/A')
                threshold = threshold_info.get('threshold', 'N/A')
                ok = check_condition(val, op, threshold) if op != 'N/A' and threshold != 'N/A' else None
                status = "✅" if ok else "❌" if ok is False else "⚠️"
                md_lines.append(f"- {ind}: {val:.2f} (umbral: {op} {threshold}) {status}")
            else:
                md_lines.append(f"- {ind}: {val:.2f} ⚠️ Sin umbral")
        md_lines.append("")
    
    # Métricas adicionales
    md_lines.append("## 📊 Métricas Adicionales\n")
    md_lines.append(f"- **Score promedio:** {np.mean(result.e_.score):.4f}")
    md_lines.append(f"- **Score máximo:** {np.max(result.e_.score):.4f}")
    md_lines.append(f"- **Score mínimo:** {np.min(result.e_.score):.4f}")
    md_lines.append(f"- **Desviación estándar:** {np.std(result.e_.score):.4f}\n")
    
    # Notas finales
    md_lines.append("---\n")
    md_lines.append("## 📝 Notas Metodológicas\n")
    md_lines.append("### Fuentes de Datos\n")
    md_lines.append("- Valores de indicadores: `indicadores_valores.xlsx`")
    md_lines.append("- Factores por estrategia: `factores_por_estrategia.xlsx`")
    md_lines.append("- Estrategias, indicadores, pesos y umbrales: `Reporte_Estrategias_Indicadores.xlsx`")
    md_lines.append("- Umbrales extraídos automáticamente del campo 'Umbral Consensuado'\n")
    
    md_lines.append("### Modelo MCDA\n")
    md_lines.append("- **Método:** Suma Ponderada (Weighted Sum Model)")
    md_lines.append("- **Criterios:** 2 (Cumplimiento de Indicadores + Score de Factores)")
    md_lines.append("- **Pesos:** 50% Indicadores + 50% Factores")
    md_lines.append("- **Normalización:** Min-Max a escala [0, 1]\n")
    
    md_lines.append("### Cálculo del Score de Factores\n")
    md_lines.append("Para cada estrategia:")
    md_lines.append("```")
    md_lines.append("Score_Factores = Σ(factor_estrategia_i × factor_contexto_i)")
    md_lines.append("                 para i = 1 hasta 11")
    md_lines.append("```")
    md_lines.append("Donde:")
    md_lines.append("- `factor_estrategia_i`: Valor del factor para la estrategia (0-10, del archivo)")
    md_lines.append("- `factor_contexto_i`: Evaluación del contexto actual (-1 a +1)")
    md_lines.append("  - **Factores generales**: Mismo valor para todas las estrategias")
    md_lines.append("  - **Factores específicos**: Valor único por estrategia")
    md_lines.append("- El score resultante se normaliza a [0, 1] para comparar estrategias\n")
    
    md_lines.append("### Granularidad de Factores\n")
    md_lines.append("Los factores tienen diferentes temporalidades de actualización:\n")
    md_lines.append("| Temporalidad | Factores |")
    md_lines.append("|--------------|----------|")
    
    # Agrupar por temporalidad
    by_temporality = {}
    for factor_name, temp in FACTOR_TEMPORALITY.items():
        if temp not in by_temporality:
            by_temporality[temp] = []
        idx = FACTOR_NAMES.index(factor_name)
        by_temporality[temp].append(FACTOR_DESCRIPTIONS[idx][:30] + "...")
    
    for temp in ["Semanal", "Mensual", "Trimestral", "Semestral", "Anual"]:
        if temp in by_temporality:
            factores_str = ", ".join(by_temporality[temp])
            md_lines.append(f"| {temp} | {factores_str} |")
    md_lines.append("")
    
    md_lines.append("### Factores por Tipo\n")
    md_lines.append(f"- **Generales** ({len(FACTOR_VALUES_GENERAL)}): {', '.join([FACTOR_DESCRIPTIONS[FACTOR_NAMES.index(f)][:25]+'...' for f in FACTOR_VALUES_GENERAL.keys()])}")
    specific_count = len(FACTOR_NAMES) - len(FACTOR_VALUES_GENERAL)
    md_lines.append(f"- **Específicos** ({specific_count}): Varían según la estrategia evaluada\n")
    
    md_lines.append("### Interpretación del Score Final\n")
    md_lines.append("```")
    md_lines.append("Score_Final = 0.5 × Score_Indicadores_Norm + 0.5 × Score_Factores_Norm")
    md_lines.append("```")
    md_lines.append("- **Score_Final ≥ 0.8:** Estrategia altamente recomendada")
    md_lines.append("- **Score_Final 0.6-0.8:** Estrategia recomendada")
    md_lines.append("- **Score_Final 0.4-0.6:** Estrategia viable")
    md_lines.append("- **Score_Final < 0.4:** Estrategia de baja prioridad\n")
    
    # Escribir archivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    
    print(f"\n✅ Reporte Markdown generado: {output_path}")
    return output_path


def load_indicator_values(xlsx_path="indicadores_valores.xlsx"):
    """
    Lee un archivo XLSX con valores de indicadores.
    
    El XLSX debe tener las columnas:
    - Indicador: nombre del indicador
    - Valor: valor numérico del indicador
    
    Args:
        xlsx_path: Ruta al archivo XLSX
        
    Returns:
        Diccionario con valores de indicadores {nombre_indicador: valor}
    """
    df = pd.read_excel(xlsx_path)
    df.columns = df.columns.str.strip()
    
    indicator_values = {}
    for _, row in df.iterrows():
        indicador = row['Indicador']
        valor = float(row['Valor']) if pd.notna(row['Valor']) else 0.0
        indicator_values[indicador] = valor
    
    return indicator_values


def load_strategy_factors(xlsx_path="factores_por_estrategia.xlsx"):
    """
    Lee un archivo XLSX con factores de aplicabilidad por estrategia.
    
    El XLSX puede tener las columnas de dos formas:
    1. Con nombres completos: Estrategia, disponibilidad_recursos, costo_operativo, etc.
    2. Con nombres abreviados: Estrategia, F1, F2, ..., F11
    
    Args:
        xlsx_path: Ruta al archivo XLSX
        
    Returns:
        Diccionario con factores por estrategia {estrategia: {factor_name: valor}}
    """
    df = pd.read_excel(xlsx_path)
    df.columns = df.columns.str.strip()
    
    strategy_factors = {}
    for _, row in df.iterrows():
        estrategia = str(row['Estrategia']).strip() if pd.notna(row['Estrategia']) else ""
        if not estrategia:
            continue
            
        factors = {}
        for i, factor_name in enumerate(FACTOR_NAMES):
            factor_val = 0.0
            
            # Intentar primero con el nombre completo del factor
            if factor_name in df.columns:
                try:
                    factor_val = float(row[factor_name]) if pd.notna(row[factor_name]) else 0.0
                except (ValueError, TypeError):
                    factor_val = 0.0
            # Si no está, intentar con F1, F2, etc.
            else:
                col_name = f'F{i+1}'
                if col_name in df.columns:
                    try:
                        factor_val = float(row[col_name]) if pd.notna(row[col_name]) else 0.0
                    except (ValueError, TypeError):
                        factor_val = 0.0
            
            # Mantener el valor como float (puede ser decimal)
            factors[factor_name] = factor_val
        
        strategy_factors[estrategia] = factors
    
    return strategy_factors


def main(
    xlsx_path="Reporte_Estrategias_Indicadores.xlsx",
    indicadores_valores_path="indicadores_valores.xlsx",
    factores_estrategia_path="factores_por_estrategia.xlsx",
    indicator_values=None,
    strategy_factors=None,
    output_md=True
):
    """
    Función principal que ejecuta el análisis MCDA completo.
    
    Construye la matriz de decisión, aplica el modelo de suma ponderada
    y muestra los resultados ordenados por ranking.
    
    Args:
        xlsx_path: Ruta al archivo XLSX con información de estrategias e indicadores
        indicadores_valores_path: Ruta al archivo XLSX con valores de indicadores
        factores_estrategia_path: Ruta al archivo XLSX con factores por estrategia
        indicator_values: Diccionario opcional con valores de indicadores (sobrescribe archivo)
        strategy_factors: Diccionario opcional con factores por estrategia (sobrescribe archivo)
        output_md: Si True, genera reporte Markdown
    """
    # Cargar configuración desde XLSX
    print(f"📂 Leyendo estrategias e indicadores desde: {xlsx_path}")
    strategies_config, indicators, indicator_thresholds = load_strategies_from_xlsx(xlsx_path)
    
    # Normalizar pesos de estrategias
    normalize_strategy_weights(strategies_config)
    
    # Cargar valores de indicadores desde XLSX
    if indicator_values is None:
        try:
            print(f"📂 Leyendo valores de indicadores desde: {indicadores_valores_path}")
            indicator_values = load_indicator_values(indicadores_valores_path)
            print(f"✅ Cargados {len(indicator_values)} valores de indicadores desde archivo.\n")
        except FileNotFoundError:
            print(f"⚠️  Archivo {indicadores_valores_path} no encontrado.")
            print("   Generando valores aleatorios basados en umbrales...\n")
            indicator_values = {}
            for ind in indicators:
                if ind in indicator_thresholds:
                    threshold_config = indicator_thresholds[ind]
                    op = threshold_config.get('op')
                    threshold = threshold_config.get('threshold')
                    indicator_values[ind] = generate_smart_indicator_value(op, threshold)
                else:
                    indicator_values[ind] = np.random.uniform(-5, 5)
        except Exception as e:
            print(f"⚠️  Error al leer {indicadores_valores_path}: {e}")
            print("   Generando valores aleatorios...\n")
            indicator_values = {}
            for ind in indicators:
                if ind in indicator_thresholds:
                    threshold_config = indicator_thresholds[ind]
                    op = threshold_config.get('op')
                    threshold = threshold_config.get('threshold')
                    indicator_values[ind] = generate_smart_indicator_value(op, threshold)
                else:
                    indicator_values[ind] = np.random.uniform(-5, 5)
    
    # Cargar factores de aplicabilidad desde XLSX
    strategy_names_list = list(strategies_config.keys())
    if strategy_factors is None:
        try:
            print(f"📂 Leyendo factores por estrategia desde: {factores_estrategia_path}")
            strategy_factors = load_strategy_factors(factores_estrategia_path)
            print(f"✅ Cargados factores para {len(strategy_factors)} estrategias desde archivo.\n")
            
            # Verificar que todas las estrategias tengan factores (búsqueda flexible)
            estrategias_sin_factores = []
            estrategias_encontradas = []
            
            for est in strategy_names_list:
                est_normalized = est.strip()
                encontrada = False
                
                # Buscar coincidencia exacta primero
                if est in strategy_factors:
                    encontrada = True
                    estrategias_encontradas.append(est)
                else:
                    # Buscar por coincidencia parcial
                    for est_key in strategy_factors.keys():
                        est_key_normalized = str(est_key).strip()
                        # Comparar primeros 30 caracteres
                        if (len(est_normalized) > 30 and len(est_key_normalized) > 30 and 
                            est_normalized[:30] == est_key_normalized[:30]):
                            # Copiar factores con el nombre correcto de la estrategia
                            strategy_factors[est] = strategy_factors[est_key].copy()
                            encontrada = True
                            estrategias_encontradas.append(est)
                            break
                        # O si uno contiene al otro
                        elif est_normalized in est_key_normalized or est_key_normalized in est_normalized:
                            strategy_factors[est] = strategy_factors[est_key].copy()
                            encontrada = True
                            estrategias_encontradas.append(est)
                            break
                
                if not encontrada:
                    estrategias_sin_factores.append(est)
                    # Generar factores aleatorios para estrategias faltantes
                    strategy_factors[est] = {
                        factor_name: np.random.randint(0, 11)
                        for factor_name in FACTOR_NAMES
                    }
            
            if estrategias_sin_factores:
                print(f"⚠️  {len(estrategias_sin_factores)} estrategias no encontradas en el archivo.")
                print("   Se generaron factores aleatorios para estas estrategias.\n")
            else:
                print(f"✅ Todas las estrategias tienen factores asignados.\n")
        except FileNotFoundError:
            print(f"⚠️  Archivo {factores_estrategia_path} no encontrado.")
            print("   Generando factores aleatorios...\n")
            strategy_factors = {}
            for est in strategy_names_list:
                strategy_factors[est] = {
                    factor_name: np.random.randint(0, 11)
                    for factor_name in FACTOR_NAMES
                }
        except Exception as e:
            print(f"⚠️  Error al leer {factores_estrategia_path}: {e}")
            print("   Generando factores aleatorios...\n")
            strategy_factors = {}
            for est in strategy_names_list:
                strategy_factors[est] = {
                    factor_name: np.random.randint(0, 11)
                    for factor_name in FACTOR_NAMES
                }
    
    # Mostrar umbrales extraídos
    print(f"ℹ️  Umbrales extraídos para {len(indicator_thresholds)} indicadores:")
    for ind, threshold_config in list(indicator_thresholds.items())[:5]:  # Mostrar primeros 5
        print(f"   {ind}: {threshold_config['op']} {threshold_config['threshold']}")
    if len(indicator_thresholds) > 5:
        print(f"   ... y {len(indicator_thresholds) - 5} más\n")
    else:
        print()
    
    # Construir matriz de indicadores
    indicator_matrix, strategy_names = build_indicator_matrix(
        indicator_values,
        strategies_config,
        indicators,
        indicator_thresholds=indicator_thresholds,
    )

    # Construir matriz MCDA
    mcda_matrix, criteria_names, factor_scores_raw = build_mcda_matrix(
        indicator_matrix,
        strategy_names,
        strategy_factors,
        FACTOR_VALUES_BY_STRATEGY,
        FACTOR_VALUES_GENERAL,
        normalize=True,
    )

    # Configurar objetivos y pesos para MCDA
    # 2 criterios: cumplimiento de indicadores (50%) + score de factores (50%)
    weights = [0.5, 0.5]
    objectives = [max, max]

    # Crear matriz de decisión
    dm = skc.mkdm(
        mcda_matrix,
        objectives,
        weights=weights,
        alternatives=strategy_names,
        criteria=criteria_names,
    )

    # Evaluar con modelo de suma ponderada
    dec = simple.WeightedSumModel()
    result = dec.evaluate(dm)

    # Mostrar resultados en consola (resumen)
    print("\n" + "="*80)
    print("RESUMEN DEL ANÁLISIS MCDA")
    print("="*80)
    print(f"\n✅ Estrategias evaluadas: {len(strategy_names)}")
    print(f"✅ Indicadores únicos: {len(indicators)}")
    print(f"✅ Umbrales configurados: {len(indicator_thresholds)}")
    print(f"✅ Modelo: 2 criterios (50% Indicadores + 50% Factores)")
    print(f"📍 Pixel ID: {PIXEL_ID}")
    
    # Mostrar factores generales
    print(f"\n⚙️ Factores GENERALES (mismo para todas las estrategias):")
    for name, val in FACTOR_VALUES_GENERAL.items():
        idx = FACTOR_NAMES.index(name)
        temporalidad = FACTOR_TEMPORALITY.get(name, "N/A")
        print(f"  - {FACTOR_DESCRIPTIONS[idx][:45]}: {val:+.2f} ({temporalidad})")
    
    # Mostrar factores específicos
    specific_factors = [f for f in FACTOR_NAMES if f not in FACTOR_VALUES_GENERAL]
    print(f"\n⚙️ Factores ESPECÍFICOS (varían por estrategia): {len(specific_factors)} factores")
    
    compliance_norm = mcda_matrix[:, 0]
    factor_scores_norm = mcda_matrix[:, 1]
    
    print(f"\n📊 Top 3 Estrategias por Cumplimiento de Indicadores:")
    ranking_compliance = sorted(
        zip(strategy_names, compliance_norm),
        key=lambda x: x[1],
        reverse=True
    )
    for i, (est, c) in enumerate(ranking_compliance[:3], 1):
        print(f"  {i}. {est[:60]}...: {c:.3f}")
    
    print(f"\n🔧 Top 3 Estrategias por Score de Factores:")
    ranking_factors = sorted(
        zip(strategy_names, factor_scores_norm),
        key=lambda x: x[1],
        reverse=True
    )
    for i, (est, f) in enumerate(ranking_factors[:3], 1):
        print(f"  {i}. {est[:60]}...: {f:.3f}")
    
    print(f"\n🏆 Top 3 Estrategias por Score Final (50% + 50%):")
    ranking = sorted(
        zip(result.alternatives, result.rank_, result.e_.score, compliance_norm, factor_scores_norm),
        key=lambda x: x[1],
    )
    for est, rank, score, comp, fact in ranking[:3]:
        print(f"  {rank}. {est[:60]}...")
        print(f"      Score Final: {score:.4f} = {comp:.3f}×0.5 + {fact:.3f}×0.5")
    
    print("\n" + "="*80)
    
    # Generar reporte Markdown
    if output_md:
        compliance = mcda_matrix[:, 0]
        md_path = generate_markdown_report(
            xlsx_path=xlsx_path,
            strategies_config=strategies_config,
            indicators=indicators,
            indicator_thresholds=indicator_thresholds,
            indicator_values=indicator_values,
            strategy_names=strategy_names,
            strategy_factors=strategy_factors,
            mcda_matrix=mcda_matrix,
            criteria_names=criteria_names,
            result=result,
            factor_scores_raw=factor_scores_raw,
        )
        print(f"📄 Reporte completo disponible en: {md_path}")
    
    return result


if __name__ == "__main__":
    # Permitir especificar los archivos XLSX como argumentos
    xlsx_path = sys.argv[1] if len(sys.argv) > 1 else "Reporte_Estrategias_Indicadores.xlsx"
    indicadores_path = sys.argv[2] if len(sys.argv) > 2 else "indicadores_valores.xlsx"
    factores_path = sys.argv[3] if len(sys.argv) > 3 else "factores_por_estrategia_detalle.xlsx"

    main(
        xlsx_path=xlsx_path,
        indicadores_valores_path=indicadores_path,
        factores_estrategia_path=factores_path
    )