"""
Sistema de Escenarios Prescriptivos para Control de Dengue

Este módulo define 4 escenarios de activación basados en los indicadores
y umbrales consensuados por expertos. Cada escenario representa un nivel
de gravedad diferente y genera recomendaciones específicas de estrategias.

Escenarios:
1. Bajo Riesgo - Situación controlada, vigilancia rutinaria
2. Riesgo Moderado - Alerta epidemiológica, intervención preventiva
3. Alto Riesgo - Brote activo, intervención intensiva
4. Emergencia/Crisis - Brote severo, respuesta de emergencia

Autor: Sistema de Soporte a Decisiones - Control de Dengue
"""

import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

# Importar funciones del modelo MCDA existente
from importlib import import_module
import sys

# ============================================================================
# DEFINICIÓN DE ESCENARIOS
# ============================================================================

# Los escenarios están diseñados en base a los umbrales consensuados.
# Cada valor se establece para cumplir o no cumplir las condiciones de activación.

ESCENARIOS = {
    # =========================================================================
    # ESCENARIO 1: BAJO RIESGO
    # Descripción: Situación epidemiológica controlada. Los indicadores están
    # dentro de los límites aceptables. Se recomienda mantener vigilancia
    # rutinaria y actividades preventivas de bajo perfil.
    # =========================================================================
    "bajo_riesgo": {
        "nombre": "Bajo Riesgo - Vigilancia Rutinaria",
        "descripcion": """
        Situación epidemiológica controlada. Los indicadores epidemiológicos
        y entomológicos están dentro de límites aceptables. Se recomienda
        mantener vigilancia rutinaria y fortalecer acciones preventivas
        sostenibles de bajo perfil.
        """,
        "color": "🟢",
        "nivel_alerta": 1,
        "indicadores": {
            # Indicadores epidemiológicos - BAJOS
            "Número de casos por semana epidemiológica": 1.0,  # Umbral > 3 casos/barrio
            "Tasa de incidencia semanal": 8.0,  # Umbral > 20/100,000 hab
            "Porcentaje de hospitalización por dengue": 3.0,  # Umbral > 10%
            "Muertes probables": 0,  # Umbral ≥ 1
            "Letalidad": 0.01,  # Umbral > 0.05%
            "Casos según clasificación clínica": 5.0,  # Umbral > 20% signos alarma
            "Porcentaje de hospitalización por tipo": 8.0,  # Umbral > 20% signos alarma
            "Zona del canal endémico (situación)": 1,  # Bajo nivel
            "Razón de crecimiento epidémico frente al año anterior": 0.8,  # Umbral > 1.3
            "Variación porcentual": 2.0,  # Umbral > +10%
            "Variación promedio vs. años anteriores": 5.0,  # Umbral > +15%
            "Serotipos circulantes": 1,  # Umbral ≥ 2

            # Indicadores entomológicos - CONTROLADOS
            "Índice de vivienda (IV)": 4.0,  # Umbral > 10%
            "Índice de Breteau (IB)": 8.0,  # Umbral > 20%
            "Índice de depósito (ID)": 2.0,  # Umbral > 5%
            "Índice Aédico en sumidero": 2.0,  # Umbral > 5%
            "Índice pupal": 0.3,  # Umbral > 1 pupa/persona
            "Número de ovitrampas positivas": 25.0,  # Umbral > 60%
            "Tasa de reinfestación": 8.0,  # Umbral < 4 semanas
            "Índice de depósito en concentraciones humanas": 0.8,  # Umbral > 2%
            "Índice de predio en concentraciones humanas": 0.5,  # Umbral > 1%
            "Nivel de infestación crítica": 5.0,  # IB > 20% o IV > 10%

            # Recursos y capacidad operativa - DISPONIBLES
            "Disponibilidad de insumos": 85.0,  # Umbral < 70%
            "Disponibilidad de equipos": 90.0,  # Umbral < 80%
            "Personal en terreno": 88.0,  # Umbral < 75%
            "Disponibilidad logística semanal": 82.0,  # Umbral < 70%
            "Cobertura territorial por brigada": 1.5,  # Umbral < 1 barrio/día
            "Tiempo de alistamiento de brigadas": 24.0,  # Umbral > 48 horas
            "Disponibilidad de camas hospitalarias/UCI para dengue grave": 25.0,  # Umbral < 10%
            "Capacidad máxima por comuna": 60.0,  # Umbral > 90%

            # Cobertura de intervenciones - ADECUADA
            "Cobertura de eliminación de criaderos o control químico en zonas de brote": 75.0,  # Umbral < 60%
            "Inspección y control en viviendas": 80.0,  # Umbral < 70%
            "Inspección y control de sumideros": 85.0,  # Umbral < 80%
            "Inspección y control en lugares de concentración humana": 85.0,  # Umbral < 80%
            "Inspección y control en cuerpos de agua (control biológico)": 85.0,  # Umbral < 80%
            "Reducción de índice de Breteau tras control larvario": 35.0,  # Umbral < 20%

            # Tiempos de respuesta - ÓPTIMOS
            "Tiempo de respuesta de control vectorial desde la notificación": 36.0,  # Umbral > 72 h
            "Tiempo entre síntoma y consulta": 1.5,  # Umbral > 3 días
            "Tiempo entre consulta y notificación": 1.0,  # Umbral > 2 días
            "Tiempo de notificación y confirmación de casos": 48.0,  # Umbral > 72 h
            "Tiempo promedio de ejecución": 3.0,  # Umbral > 5 días/barrio

            # Factores ambientales - FAVORABLES
            "Índice de pluviosidad (días previos)": 25.0,  # Umbral > 50 mm/7d
            "Temperatura máxima (días previos)": 25.0,  # Umbral > 27°C
            "Estado de sumideros (limpios / obstruidos)": 10.0,  # Umbral > 20%
            "Estado de canales de aguas lluvias (limpios / obstruidos)": 15.0,  # Umbral > 30%
            "Continuidad en el servicio de acueducto": 22.0,  # Umbral < 20 h/día
            "Cobertura de agua potable": 95.0,  # Umbral < 90%

            # Factores sociales - FAVORABLES
            "Percepción de riesgo comunitario": 65.0,  # Umbral < 50%
            "Rechazo comunitario a intervención": 3.0,  # Umbral > 10%
            "Cobertura de educación preventiva": 70.0,  # Umbral < 60%
            "Prácticas preventivas": 60.0,  # Umbral < 50%
            "Retención de aprendizaje comunitario": 75.0,  # Umbral < 70%
            "Cobertura de hogares alcanzados con mensajes de riesgo": 70.0,  # Umbral < 60%

            # Otros
            "Tipo de brote": 2.0,  # Umbral Tipo II (≥ 6 semanas)
            "Costos unitarios por intervención": 1500000.0,  # Umbral > $3M
            "Probabilidad de reducción de casos": 80.0,  # Umbral < 70%
            "Inicio y mantenimiento de brote histórico": 1.0,  # Umbral ≥ 4 semanas
            "% de casos confirmados por laboratorio": 75.0,  # Umbral < 60%
            "Edad (moda, mediana, promedio) de hospitalización": 28.0,  # Umbral < 15 años
            "Densidad poblacional": 6000.0,  # Umbral > 10,000
            "Índice de Vulnerabilidad Socioeconómica": 0.4,  # Umbral > 0.6
            "Número de organizaciones sociales": 4,  # Umbral < 2
            "Frecuencia de recolección de residuos sólidos": 3,  # Umbral < 2
            "Presencia de basureros ilegales o puntos críticos de residuos": 0.5,  # Umbral > 1
            "Tipo de depósito positivo dominante": 20.0,  # Umbral ≥ 40%
            "Cobertura de zonas verdes y árboles por barrio": 20.0,  # Umbral > 30%
            "Sector económico": 1.0,  # Umbral > 3 obras/km²
            "Cobertura en instituciones educativas": 85.0,  # Umbral < 80%
            "Establecimiento de Wolbachia": 40.0,  # Umbral > 60%
        },
        "factores_estrategia": {
            # Factores bajos porque la situación no requiere intervención intensa
            "disponibilidad_recursos": 8,
            "costo_operativo": 3,
            "tiempo_cobertura": 7,
            "dependencias_externas": 2,
            "aceptacion_comunidad": 8,
            "acceso_predios": 8,
            "percepcion_riesgo": 6,
            "resistencia_vector": 2,
            "otros_vectores": 2,
            "efectividad_esperada": 7,
            "magnitud_brote": 2,
        },
        "estrategias_esperadas": [
            "Promover prácticas preventivas sostenibles",
            "Fortalecer la percepción de riesgo",
            "Monitorear condiciones climáticas",
        ],
    },

    # =========================================================================
    # ESCENARIO 2: RIESGO MODERADO
    # Descripción: Alerta epidemiológica. Algunos indicadores cruzan umbrales.
    # Se requiere intensificar vigilancia y acciones preventivas focalizadas.
    # =========================================================================
    "riesgo_moderado": {
        "nombre": "Riesgo Moderado - Alerta Epidemiológica",
        "descripcion": """
        Situación de alerta epidemiológica. Algunos indicadores entomológicos
        y epidemiológicos cruzan los umbrales de activación. Se requiere
        intensificar la vigilancia, fortalecer las intervenciones preventivas
        focalizadas y preparar recursos para una posible escalada.
        """,
        "color": "🟡",
        "nivel_alerta": 2,
        "indicadores": {
            # Indicadores epidemiológicos - EN ASCENSO
            "Número de casos por semana epidemiológica": 4.0,  # Umbral > 3 casos/barrio ⚠️
            "Tasa de incidencia semanal": 22.0,  # Umbral > 20/100,000 hab ⚠️
            "Porcentaje de hospitalización por dengue": 8.0,  # Cercano al umbral
            "Muertes probables": 0,  # Aún sin muertes
            "Letalidad": 0.03,  # Bajo el umbral
            "Casos según clasificación clínica": 15.0,  # Cercano al umbral
            "Porcentaje de hospitalización por tipo": 18.0,  # Cercano al umbral
            "Zona del canal endémico (situación)": 2,  # Zona de alerta
            "Razón de crecimiento epidémico frente al año anterior": 1.2,  # Cercano al umbral
            "Variación porcentual": 12.0,  # Umbral > +10% ⚠️
            "Variación promedio vs. años anteriores": 18.0,  # Umbral > +15% ⚠️
            "Serotipos circulantes": 1,  # Un serotipo activo

            # Indicadores entomológicos - ELEVADOS
            "Índice de vivienda (IV)": 12.0,  # Umbral > 10% ⚠️
            "Índice de Breteau (IB)": 22.0,  # Umbral > 20% ⚠️
            "Índice de depósito (ID)": 6.0,  # Umbral > 5% ⚠️
            "Índice Aédico en sumidero": 4.0,  # Cercano al umbral
            "Índice pupal": 0.8,  # Cercano al umbral
            "Número de ovitrampas positivas": 55.0,  # Cercano al umbral
            "Tasa de reinfestación": 5.0,  # Cercano al umbral
            "Índice de depósito en concentraciones humanas": 2.5,  # Umbral > 2% ⚠️
            "Índice de predio en concentraciones humanas": 0.8,  # Cercano al umbral
            "Nivel de infestación crítica": 15.0,  # Elevado

            # Recursos y capacidad - TENSIONADOS
            "Disponibilidad de insumos": 72.0,  # Cercano al umbral
            "Disponibilidad de equipos": 78.0,  # Cercano al umbral < 80% ⚠️
            "Personal en terreno": 76.0,  # Cercano al umbral
            "Disponibilidad logística semanal": 68.0,  # Umbral < 70% ⚠️
            "Cobertura territorial por brigada": 1.0,  # Justo en el umbral
            "Tiempo de alistamiento de brigadas": 44.0,  # Cercano al umbral
            "Disponibilidad de camas hospitalarias/UCI para dengue grave": 15.0,
            "Capacidad máxima por comuna": 75.0,

            # Cobertura de intervenciones - INSUFICIENTE
            "Cobertura de eliminación de criaderos o control químico en zonas de brote": 58.0,  # Umbral < 60% ⚠️
            "Inspección y control en viviendas": 68.0,  # Umbral < 70% ⚠️
            "Inspección y control de sumideros": 78.0,  # Umbral < 80% ⚠️
            "Inspección y control en lugares de concentración humana": 78.0,  # Umbral < 80% ⚠️
            "Inspección y control en cuerpos de agua (control biológico)": 78.0,  # Umbral < 80% ⚠️
            "Reducción de índice de Breteau tras control larvario": 18.0,  # Umbral < 20% ⚠️

            # Tiempos de respuesta - RETRASADOS
            "Tiempo de respuesta de control vectorial desde la notificación": 68.0,  # Cercano al umbral
            "Tiempo entre síntoma y consulta": 2.5,  # Cercano al umbral
            "Tiempo entre consulta y notificación": 1.8,  # Cercano al umbral
            "Tiempo de notificación y confirmación de casos": 65.0,  # Cercano al umbral
            "Tiempo promedio de ejecución": 4.5,  # Cercano al umbral

            # Factores ambientales - DESFAVORABLES
            "Índice de pluviosidad (días previos)": 55.0,  # Umbral > 50 mm/7d ⚠️
            "Temperatura máxima (días previos)": 28.0,  # Umbral > 27°C ⚠️
            "Estado de sumideros (limpios / obstruidos)": 22.0,  # Umbral > 20% ⚠️
            "Estado de canales de aguas lluvias (limpios / obstruidos)": 28.0,  # Cercano al umbral
            "Continuidad en el servicio de acueducto": 19.0,  # Umbral < 20 h/día ⚠️
            "Cobertura de agua potable": 88.0,  # Umbral < 90% ⚠️

            # Factores sociales - DEFICIENTES
            "Percepción de riesgo comunitario": 48.0,  # Umbral < 50% ⚠️
            "Rechazo comunitario a intervención": 8.0,  # Cercano al umbral
            "Cobertura de educación preventiva": 58.0,  # Umbral < 60% ⚠️
            "Prácticas preventivas": 48.0,  # Umbral < 50% ⚠️
            "Retención de aprendizaje comunitario": 68.0,  # Umbral < 70% ⚠️
            "Cobertura de hogares alcanzados con mensajes de riesgo": 55.0,  # Umbral < 60% ⚠️

            # Otros
            "Tipo de brote": 4.0,  # Cercano a Tipo II
            "Costos unitarios por intervención": 2500000.0,  # Cercano al umbral
            "Probabilidad de reducción de casos": 72.0,
            "Inicio y mantenimiento de brote histórico": 2.0,
            "% de casos confirmados por laboratorio": 62.0,
            "Edad (moda, mediana, promedio) de hospitalización": 22.0,
            "Densidad poblacional": 9000.0,  # Cercano al umbral
            "Índice de Vulnerabilidad Socioeconómica": 0.55,  # Cercano al umbral
            "Número de organizaciones sociales": 2,  # En el umbral
            "Frecuencia de recolección de residuos sólidos": 2,  # En el umbral
            "Presencia de basureros ilegales o puntos críticos de residuos": 0.9,  # Cercano al umbral
            "Tipo de depósito positivo dominante": 35.0,  # Cercano al umbral
            "Cobertura de zonas verdes y árboles por barrio": 28.0,  # Cercano al umbral
            "Sector económico": 2.5,  # Cercano al umbral
            "Cobertura en instituciones educativas": 78.0,  # Umbral < 80% ⚠️
            "Establecimiento de Wolbachia": 50.0,  # Cercano al umbral
        },
        "factores_estrategia": {
            "disponibilidad_recursos": 6,
            "costo_operativo": 5,
            "tiempo_cobertura": 5,
            "dependencias_externas": 4,
            "aceptacion_comunidad": 6,
            "acceso_predios": 6,
            "percepcion_riesgo": 5,
            "resistencia_vector": 4,
            "otros_vectores": 3,
            "efectividad_esperada": 6,
            "magnitud_brote": 5,
        },
        "estrategias_esperadas": [
            "Realizar identificación focalizada de criaderos",
            "Aplicar larvicidas químicos en criaderos específicos",
            "Difundir mensajes preventivos inmediatos",
            "Implementar acciones de control físico",
        ],
    },

    # =========================================================================
    # ESCENARIO 3: ALTO RIESGO
    # Descripción: Brote activo confirmado. Múltiples indicadores en niveles
    # críticos. Se requiere intervención intensiva y coordinación sectorial.
    # =========================================================================
    "alto_riesgo": {
        "nombre": "Alto Riesgo - Brote Activo",
        "descripcion": """
        Brote activo confirmado. Múltiples indicadores epidemiológicos y
        entomológicos superan los umbrales críticos. Se requiere intervención
        intensiva con control vectorial adulticida, fortalecimiento de la
        atención médica y coordinación multisectorial.
        """,
        "color": "🟠",
        "nivel_alerta": 3,
        "indicadores": {
            # Indicadores epidemiológicos - CRÍTICOS (todos activados)
            "Número de casos por semana epidemiológica": 8.0,  # Umbral > 3 ⚠️
            "Tasa de incidencia semanal": 45.0,  # Umbral > 20/100,000 ⚠️
            "Porcentaje de hospitalización por dengue": 15.0,  # Umbral > 10% ⚠️
            "Muertes probables": 1,  # Umbral ≥ 1 ⚠️
            "Letalidad": 0.06,  # Umbral > 0.05% ⚠️
            "Casos según clasificación clínica": 28.0,  # Umbral > 20% ⚠️
            "Porcentaje de hospitalización por tipo": 25.0,  # Umbral > 20% ⚠️
            "Zona del canal endémico (situación)": 3,  # Zona de brote
            "Razón de crecimiento epidémico frente al año anterior": 1.5,  # Umbral > 1.3 ⚠️
            "Variación porcentual": 25.0,  # Umbral > +10% ⚠️
            "Variación promedio vs. años anteriores": 35.0,  # Umbral > +15% ⚠️
            "Serotipos circulantes": 2,  # Umbral ≥ 2 ⚠️

            # Indicadores entomológicos - CRÍTICOS (todos activados)
            "Índice de vivienda (IV)": 18.0,  # Umbral > 10% ⚠️
            "Índice de Breteau (IB)": 35.0,  # Umbral > 20% ⚠️
            "Índice de depósito (ID)": 12.0,  # Umbral > 5% ⚠️
            "Índice Aédico en sumidero": 8.0,  # Umbral > 5% ⚠️
            "Índice pupal": 1.5,  # Umbral > 1 ⚠️
            "Número de ovitrampas positivas": 75.0,  # Umbral > 60% ⚠️
            "Tasa de reinfestación": 3.0,  # Umbral < 4 semanas ⚠️
            "Índice de depósito en concentraciones humanas": 4.0,  # Umbral > 2% ⚠️
            "Índice de predio en concentraciones humanas": 2.0,  # Umbral > 1% ⚠️
            "Nivel de infestación crítica": 25.0,  # Muy alto

            # Recursos y capacidad - PARCIALMENTE DISPONIBLES (algunos NO críticos)
            "Disponibilidad de insumos": 72.0,  # Umbral < 70% - NORMAL ✓
            "Disponibilidad de equipos": 82.0,  # Umbral < 80% - NORMAL ✓
            "Personal en terreno": 76.0,  # Umbral < 75% - NORMAL ✓
            "Disponibilidad logística semanal": 71.0,  # Umbral < 70% - NORMAL ✓
            "Cobertura territorial por brigada": 1.1,  # Umbral < 1 - NORMAL ✓
            "Tiempo de alistamiento de brigadas": 46.0,  # Umbral > 48 h - NORMAL ✓
            "Disponibilidad de camas hospitalarias/UCI para dengue grave": 12.0,  # Umbral < 10% - NORMAL ✓
            "Capacidad máxima por comuna": 85.0,  # Umbral > 90% - NORMAL ✓

            # Cobertura de intervenciones - MIXTO (algunos críticos, otros no)
            "Cobertura de eliminación de criaderos o control químico en zonas de brote": 55.0,  # Umbral < 60% ⚠️
            "Inspección y control en viviendas": 65.0,  # Umbral < 70% ⚠️
            "Inspección y control de sumideros": 82.0,  # Umbral < 80% - NORMAL ✓
            "Inspección y control en lugares de concentración humana": 81.0,  # Umbral < 80% - NORMAL ✓
            "Inspección y control en cuerpos de agua (control biológico)": 78.0,  # Umbral < 80% ⚠️
            "Reducción de índice de Breteau tras control larvario": 18.0,  # Umbral < 20% ⚠️

            # Tiempos de respuesta - MIXTO (algunos críticos)
            "Tiempo de respuesta de control vectorial desde la notificación": 85.0,  # Umbral > 72 h ⚠️
            "Tiempo entre síntoma y consulta": 2.8,  # Umbral > 3 días - NORMAL ✓
            "Tiempo entre consulta y notificación": 1.9,  # Umbral > 2 días - NORMAL ✓
            "Tiempo de notificación y confirmación de casos": 80.0,  # Umbral > 72 h ⚠️
            "Tiempo promedio de ejecución": 6.0,  # Umbral > 5 días ⚠️

            # Factores ambientales - CRÍTICOS (temporada de lluvias)
            "Índice de pluviosidad (días previos)": 75.0,  # Umbral > 50 mm ⚠️
            "Temperatura máxima (días previos)": 30.0,  # Umbral > 27°C ⚠️
            "Estado de sumideros (limpios / obstruidos)": 35.0,  # Umbral > 20% ⚠️
            "Estado de canales de aguas lluvias (limpios / obstruidos)": 40.0,  # Umbral > 30% ⚠️
            "Continuidad en el servicio de acueducto": 21.0,  # Umbral < 20 h - NORMAL ✓
            "Cobertura de agua potable": 91.0,  # Umbral < 90% - NORMAL ✓

            # Factores sociales - MIXTO (la comunidad aún responde)
            "Percepción de riesgo comunitario": 52.0,  # Umbral < 50% - NORMAL ✓
            "Rechazo comunitario a intervención": 8.0,  # Umbral > 10% - NORMAL ✓
            "Cobertura de educación preventiva": 55.0,  # Umbral < 60% ⚠️
            "Prácticas preventivas": 48.0,  # Umbral < 50% ⚠️
            "Retención de aprendizaje comunitario": 68.0,  # Umbral < 70% ⚠️
            "Cobertura de hogares alcanzados con mensajes de riesgo": 58.0,  # Umbral < 60% ⚠️

            # Otros - MIXTO
            "Tipo de brote": 7.0,  # Tipo II (≥ 6 semanas) ⚠️
            "Costos unitarios por intervención": 2800000.0,  # Umbral > $3M - NORMAL ✓
            "Probabilidad de reducción de casos": 72.0,  # Umbral < 70% - NORMAL ✓
            "Inicio y mantenimiento de brote histórico": 5.0,  # Umbral ≥ 4 semanas ⚠️
            "% de casos confirmados por laboratorio": 62.0,  # Umbral < 60% - NORMAL ✓
            "Edad (moda, mediana, promedio) de hospitalización": 12.0,  # Umbral < 15 años ⚠️
            "Densidad poblacional": 12000.0,  # Umbral > 10,000 ⚠️
            "Índice de Vulnerabilidad Socioeconómica": 0.58,  # Umbral > 0.6 - NORMAL ✓
            "Número de organizaciones sociales": 3,  # Umbral < 2 - NORMAL ✓
            "Frecuencia de recolección de residuos sólidos": 2,  # Umbral < 2 - NORMAL ✓
            "Presencia de basureros ilegales o puntos críticos de residuos": 1.5,  # Umbral > 1 ⚠️
            "Tipo de depósito positivo dominante": 45.0,  # Umbral ≥ 40% ⚠️
            "Cobertura de zonas verdes y árboles por barrio": 28.0,  # Umbral > 30% - NORMAL ✓
            "Sector económico": 4.0,  # Umbral > 3 ⚠️
            "Cobertura en instituciones educativas": 82.0,  # Umbral < 80% - NORMAL ✓
            "Establecimiento de Wolbachia": 55.0,  # No tiene umbral activo
        },
        "factores_estrategia": {
            "disponibilidad_recursos": 4,
            "costo_operativo": 7,
            "tiempo_cobertura": 4,
            "dependencias_externas": 6,
            "aceptacion_comunidad": 5,
            "acceso_predios": 5,
            "percepcion_riesgo": 7,
            "resistencia_vector": 5,
            "otros_vectores": 5,
            "efectividad_esperada": 6,
            "magnitud_brote": 8,
        },
        "estrategias_esperadas": [
            "Aplicar adulticidas químicos (malatión/deltametrina)",
            "Implementar protocolos de triage",
            "Articular esfuerzos multisectoriales",
            "Aplicar larvicidas químicos en criaderos",
            "Fomentar uso de protección individual",
        ],
    },

    # =========================================================================
    # ESCENARIO 4: EMERGENCIA/CRISIS
    # Descripción: Brote severo con alta morbimortalidad. Todos los sistemas
    # están al límite. Se requiere respuesta de emergencia coordinada.
    # =========================================================================
    "emergencia": {
        "nombre": "Emergencia - Crisis Sanitaria",
        "descripcion": """
        Brote severo con alta morbimortalidad. La capacidad de respuesta está
        sobrepasada. Todos los indicadores están en niveles críticos. Se
        requiere respuesta de emergencia con movilización total de recursos,
        apoyo externo y medidas extraordinarias de control.
        """,
        "color": "🔴",
        "nivel_alerta": 4,
        "indicadores": {
            # Indicadores epidemiológicos - EXTREMOS
            "Número de casos por semana epidemiológica": 18.0,  # Muy por encima del umbral
            "Tasa de incidencia semanal": 85.0,  # Muy por encima del umbral
            "Porcentaje de hospitalización por dengue": 28.0,  # Muy por encima del umbral
            "Muertes probables": 4,  # Múltiples muertes
            "Letalidad": 0.12,  # Muy por encima del umbral
            "Casos según clasificación clínica": 42.0,  # Muchos casos graves
            "Porcentaje de hospitalización por tipo": 38.0,  # Alta proporción con signos alarma
            "Zona del canal endémico (situación)": 4,  # Zona de epidemia
            "Razón de crecimiento epidémico frente al año anterior": 2.2,  # Crecimiento explosivo
            "Variación porcentual": 55.0,  # Aumento masivo
            "Variación promedio vs. años anteriores": 70.0,  # Muy por encima de históricos
            "Serotipos circulantes": 3,  # Múltiples serotipos

            # Indicadores entomológicos - EXTREMOS
            "Índice de vivienda (IV)": 32.0,  # Muy alto
            "Índice de Breteau (IB)": 55.0,  # Muy alto
            "Índice de depósito (ID)": 22.0,  # Muy alto
            "Índice Aédico en sumidero": 15.0,  # Muy alto
            "Índice pupal": 2.8,  # Muy alto
            "Número de ovitrampas positivas": 92.0,  # Casi todas positivas
            "Tasa de reinfestación": 2.0,  # Reinfestación muy rápida
            "Índice de depósito en concentraciones humanas": 8.0,  # Muy alto
            "Índice de predio en concentraciones humanas": 4.5,  # Muy alto
            "Nivel de infestación crítica": 45.0,  # Extremo

            # Recursos y capacidad - COLAPSADOS
            "Disponibilidad de insumos": 45.0,  # Muy insuficiente
            "Disponibilidad de equipos": 52.0,  # Muy insuficiente
            "Personal en terreno": 48.0,  # Muy insuficiente
            "Disponibilidad logística semanal": 42.0,  # Muy insuficiente
            "Cobertura territorial por brigada": 0.4,  # Muy baja
            "Tiempo de alistamiento de brigadas": 72.0,  # Muy retrasado
            "Disponibilidad de camas hospitalarias/UCI para dengue grave": 3.0,  # Crisis hospitalaria
            "Capacidad máxima por comuna": 98.0,  # Al límite

            # Cobertura de intervenciones - COLAPSADA
            "Cobertura de eliminación de criaderos o control químico en zonas de brote": 28.0,  # Muy insuficiente
            "Inspección y control en viviendas": 35.0,  # Muy insuficiente
            "Inspección y control de sumideros": 42.0,  # Muy insuficiente
            "Inspección y control en lugares de concentración humana": 45.0,  # Muy insuficiente
            "Inspección y control en cuerpos de agua (control biológico)": 40.0,  # Muy insuficiente
            "Reducción de índice de Breteau tras control larvario": 5.0,  # Mínima efectividad

            # Tiempos de respuesta - COLAPSADOS
            "Tiempo de respuesta de control vectorial desde la notificación": 144.0,  # Muy retrasado
            "Tiempo entre síntoma y consulta": 6.0,  # Muy retrasado
            "Tiempo entre consulta y notificación": 4.5,  # Muy retrasado
            "Tiempo de notificación y confirmación de casos": 120.0,  # Muy retrasado
            "Tiempo promedio de ejecución": 10.0,  # Muy retrasado

            # Factores ambientales - EXTREMOS
            "Índice de pluviosidad (días previos)": 120.0,  # Lluvias intensas
            "Temperatura máxima (días previos)": 33.0,  # Muy alta
            "Estado de sumideros (limpios / obstruidos)": 55.0,  # Mayoría obstruidos
            "Estado de canales de aguas lluvias (limpios / obstruidos)": 60.0,  # Mayoría obstruidos
            "Continuidad en el servicio de acueducto": 12.0,  # Muy intermitente
            "Cobertura de agua potable": 72.0,  # Insuficiente

            # Factores sociales - CRÍTICOS
            "Percepción de riesgo comunitario": 30.0,  # Muy bajo
            "Rechazo comunitario a intervención": 25.0,  # Alto rechazo
            "Cobertura de educación preventiva": 30.0,  # Muy insuficiente
            "Prácticas preventivas": 25.0,  # Muy insuficiente
            "Retención de aprendizaje comunitario": 40.0,  # Muy insuficiente
            "Cobertura de hogares alcanzados con mensajes de riesgo": 28.0,  # Muy insuficiente

            # Otros - EXTREMOS
            "Tipo de brote": 12.0,  # Brote prolongado
            "Costos unitarios por intervención": 5500000.0,  # Muy alto
            "Probabilidad de reducción de casos": 45.0,  # Baja efectividad esperada
            "Inicio y mantenimiento de brote histórico": 8.0,  # Brote prolongado
            "% de casos confirmados por laboratorio": 38.0,  # Capacidad laboratorio sobrepasada
            "Edad (moda, mediana, promedio) de hospitalización": 8.0,  # Afectando niños
            "Densidad poblacional": 18000.0,  # Muy alta
            "Índice de Vulnerabilidad Socioeconómica": 0.82,  # Muy alto
            "Número de organizaciones sociales": 0,  # Sin apoyo comunitario
            "Frecuencia de recolección de residuos sólidos": 0.5,  # Muy deficiente
            "Presencia de basureros ilegales o puntos críticos de residuos": 3.5,  # Muy alto
            "Tipo de depósito positivo dominante": 65.0,  # Muy alto
            "Cobertura de zonas verdes y árboles por barrio": 45.0,  # Alto
            "Sector económico": 6.0,  # Muchas construcciones
            "Cobertura en instituciones educativas": 45.0,  # Muy insuficiente
            "Establecimiento de Wolbachia": 30.0,  # Insuficiente
        },
        "factores_estrategia": {
            "disponibilidad_recursos": 2,
            "costo_operativo": 9,
            "tiempo_cobertura": 2,
            "dependencias_externas": 8,
            "aceptacion_comunidad": 3,
            "acceso_predios": 4,
            "percepcion_riesgo": 9,
            "resistencia_vector": 7,
            "otros_vectores": 7,
            "efectividad_esperada": 4,
            "magnitud_brote": 10,
        },
        "estrategias_esperadas": [
            "Aplicar adulticidas químicos masivamente",
            "Implementar protocolos de triage de emergencia",
            "Fortalecer articulación institucional",
            "Fortalecer sostenibilidad financiera",
            "Todas las estrategias simultáneamente",
        ],
    },
}


# ============================================================================
# FUNCIONES DE EJECUCIÓN DE ESCENARIOS
# ============================================================================

def cargar_modelo_mcda():
    """Importa el modelo MCDA desde scikit-criteria-demo.py"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("mcda_model", "scikit-criteria-demo.py")
    mcda_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcda_module)
    return mcda_module


def ejecutar_escenario(escenario_id, mcda_module, xlsx_path="Reporte_Estrategias_Indicadores.xlsx", escenarios_def=None, contexto_escenario=None):
    """
    Ejecuta un escenario específico y retorna los resultados del modelo MCDA.

    Args:
        escenario_id: ID del escenario ("bajo_riesgo", "riesgo_moderado", etc.)
        mcda_module: Módulo MCDA cargado
        xlsx_path: Ruta al archivo de configuración de estrategias

    Returns:
        Diccionario con resultados del escenario
    """
    if escenarios_def is None:
        escenarios_def = ESCENARIOS

    if escenario_id not in escenarios_def:
        raise ValueError(f"Escenario '{escenario_id}' no encontrado. Opciones: {list(escenarios_def.keys())}")

    escenario = escenarios_def[escenario_id]

    # Cargar configuración de estrategias
    strategies_config, indicators, indicator_thresholds = mcda_module.load_strategies_from_xlsx(xlsx_path)
    mcda_module.normalize_strategy_weights(strategies_config)

    # Obtener valores de indicadores del escenario
    indicator_values = escenario["indicadores"]

    # Preparar factores por estrategia (mismo factor para todas en este escenario)
    strategy_factors = {}
    for est in strategies_config.keys():
        strategy_factors[est] = escenario["factores_estrategia"].copy()

    # Construir matriz de indicadores
    indicator_matrix, strategy_names = mcda_module.build_indicator_matrix(
        indicator_values,
        strategies_config,
        indicators,
        indicator_thresholds=indicator_thresholds,
    )

    # Construir matriz MCDA
    factor_values_by_strategy = getattr(mcda_module, "FACTOR_VALUES_BY_STRATEGY", {})
    factor_values_general = getattr(mcda_module, "FACTOR_VALUES_GENERAL", {})

    mcda_matrix, criteria_names, _ = mcda_module.build_mcda_matrix(
        indicator_matrix,
        strategy_names,
        strategy_factors,
        factor_values_by_strategy,
        factor_values_general,
        normalize=True,
    )

    # Ejecutar modelo MCDA
    import skcriteria as skc
    from skcriteria.agg import simple

    num_criteria = len(criteria_names)
    weights = [1.0 / num_criteria] * num_criteria
    objectives = [max] * num_criteria

    dm = skc.mkdm(
        mcda_matrix,
        objectives,
        weights=weights,
        alternatives=strategy_names,
        criteria=criteria_names,
    )

    dec = simple.WeightedSumModel()
    result = dec.evaluate(dm)

    # Calcular cumplimiento de indicadores
    compliance = mcda_matrix[:, 0]

    # =========================================================================
    # APLICAR MULTIPLICADORES DE URGENCIA SEGÚN NIVEL DE RIESGO
    # =========================================================================
    # Obtener función de multiplicadores del módulo MCDA
    aplicar_multiplicador = getattr(mcda_module, 'aplicar_multiplicador_urgencia', None)

    if aplicar_multiplicador is not None:
        # Determinar el nivel de riesgo base
        # Si el escenario_id es un nivel de riesgo válido, usarlo directamente
        # Si no, determinar por nivel_alerta del escenario
        niveles_validos = ['bajo_riesgo', 'riesgo_moderado', 'alto_riesgo', 'emergencia']
        if escenario_id in niveles_validos:
            nivel_riesgo = escenario_id
        else:
            # Determinar por nivel_alerta
            nivel_alerta = escenario.get('nivel_alerta', 2)
            nivel_riesgo = {1: 'bajo_riesgo', 2: 'riesgo_moderado', 3: 'alto_riesgo', 4: 'emergencia'}.get(nivel_alerta, 'riesgo_moderado')

        # Aplicar multiplicadores según el nivel de riesgo y contexto del escenario
        scores_ajustados = aplicar_multiplicador(
            result.e_.score,
            strategy_names,
            nivel_riesgo,  # 'bajo_riesgo', 'riesgo_moderado', 'alto_riesgo', 'emergencia'
            contexto_escenario  # 'lluvias_intensas', 'intermitencia_agua', 'alta_densidad', etc.
        )

        # Re-rankear basándose en los scores ajustados
        # Mayor score = mejor ranking (1, 2, 3...)
        indices_ordenados = np.argsort(scores_ajustados)[::-1]  # Descendente
        ranks_ajustados = np.zeros(len(scores_ajustados), dtype=int)
        for rank, idx in enumerate(indices_ordenados, 1):
            ranks_ajustados[idx] = rank

        # Usar scores y ranks ajustados
        scores_finales = scores_ajustados
        ranks_finales = ranks_ajustados
    else:
        # Sin ajuste, usar resultados originales
        scores_finales = result.e_.score
        ranks_finales = result.rank_

    # Ordenar estrategias por ranking ajustado
    ranking = sorted(
        zip(result.alternatives, ranks_finales, scores_finales, compliance),
        key=lambda x: x[1],
    )

    # Contar indicadores que ACTIVAN intervención (están en nivel crítico)
    # Si el indicador CUMPLE con la condición del umbral, significa que está en nivel crítico
    # Ejemplo: si umbral es "IB > 20%" y el valor es 35%, CUMPLE = CRÍTICO
    indicadores_criticos = 0
    indicadores_normales = 0
    for ind in indicators:
        val = indicator_values.get(ind, None)
        if val is not None and ind in indicator_thresholds:
            op = indicator_thresholds[ind]["op"]
            threshold = indicator_thresholds[ind]["threshold"]
            if mcda_module.check_condition(val, op, threshold):
                indicadores_criticos += 1  # El indicador está en nivel que ACTIVA alerta
            else:
                indicadores_normales += 1  # El indicador está en nivel NORMAL

    return {
        "escenario": escenario,
        "ranking": ranking,
        "mcda_matrix": mcda_matrix,
        "criteria_names": criteria_names,
        "indicator_thresholds": indicator_thresholds,
        "indicators": indicators,
        "indicator_values": indicator_values,
        "strategies_config": strategies_config,
        "indicadores_criticos": indicadores_criticos,
        "indicadores_normales": indicadores_normales,
        "result": result,
    }


def generar_reporte_escenario(escenario_id, resultados, output_path=None):
    """
    Genera un reporte detallado en Markdown para un escenario.

    Args:
        escenario_id: ID del escenario
        resultados: Diccionario con resultados del análisis MCDA
        output_path: Ruta de salida (opcional)

    Returns:
        Ruta del archivo generado
    """
    escenario = resultados["escenario"]
    ranking = resultados["ranking"]
    indicator_thresholds = resultados["indicator_thresholds"]
    indicator_values = resultados["indicator_values"]
    indicadores_criticos = resultados["indicadores_criticos"]
    indicadores_normales = resultados["indicadores_normales"]

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"reporte_escenario_{escenario_id}_{timestamp}.md"

    md_lines = []

    # Encabezado
    md_lines.append(f"# {escenario['color']} Escenario: {escenario['nombre']}\n")
    md_lines.append(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_lines.append(f"**Nivel de alerta:** {escenario['nivel_alerta']}/4\n")
    md_lines.append("---\n")

    # Descripción
    md_lines.append("## Descripción del Escenario\n")
    md_lines.append(escenario['descripcion'].strip())
    md_lines.append("\n---\n")

    # Resumen de indicadores
    md_lines.append("## Resumen de Indicadores\n")
    total_indicadores = indicadores_criticos + indicadores_normales
    pct_criticos = (indicadores_criticos / total_indicadores * 100) if total_indicadores > 0 else 0

    md_lines.append(f"| Métrica | Valor |")
    md_lines.append(f"|---------|-------|")
    md_lines.append(f"| Indicadores evaluados | {total_indicadores} |")
    md_lines.append(f"| Indicadores en nivel normal | {indicadores_normales} |")
    md_lines.append(f"| Indicadores en nivel crítico (activan alerta) | {indicadores_criticos} |")
    md_lines.append(f"| Porcentaje de indicadores críticos | {pct_criticos:.1f}% |")
    md_lines.append("")

    # Barra visual de criticidad
    bar_criticos = int(pct_criticos / 5)  # Escala a 20 caracteres
    bar = "🔴" * bar_criticos + "⚪" * (20 - bar_criticos)
    md_lines.append(f"**Nivel de criticidad:** {bar} ({pct_criticos:.0f}%)\n")
    md_lines.append("---\n")

    # Top 5 estrategias recomendadas
    md_lines.append("## Top 5 Estrategias Recomendadas\n")
    md_lines.append("| Rank | Estrategia | Score | Cumplimiento |")
    md_lines.append("|------|------------|-------|--------------|")

    for est, rank, score, comp in ranking[:5]:
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
        est_short = est[:70] + "..." if len(est) > 70 else est
        est_short = est_short.replace("|", "\\|")
        md_lines.append(f"| {rank} {medal} | {est_short} | {score:.4f} | {comp:.3f} |")
    md_lines.append("")

    # Detalle de las top 3 estrategias
    md_lines.append("### Detalle de Estrategias Prioritarias\n")
    for est, rank, score, comp in ranking[:3]:
        md_lines.append(f"#### {rank}. {est}\n")
        md_lines.append(f"- **Score global:** `{score:.4f}`")
        md_lines.append(f"- **Cumplimiento de indicadores:** `{comp:.3f}`")
        md_lines.append(f"- **Prioridad de activación:** {'ALTA' if rank == 1 else 'MEDIA' if rank == 2 else 'NORMAL'}")
        md_lines.append("")

    md_lines.append("---\n")

    # Indicadores críticos (que CUMPLEN el umbral de activación = están en nivel crítico)
    md_lines.append("## Indicadores Críticos (Activadores de Alerta)\n")
    md_lines.append("Los siguientes indicadores han cruzado sus umbrales de activación y requieren atención:\n")
    md_lines.append("| Indicador | Valor Actual | Umbral | Exceso |")
    md_lines.append("|-----------|--------------|--------|--------|")

    from importlib import import_module
    import importlib.util
    spec = importlib.util.spec_from_file_location("mcda_model", "scikit-criteria-demo.py")
    mcda_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcda_module)

    criticos = []
    for ind, threshold_config in indicator_thresholds.items():
        val = indicator_values.get(ind)
        if val is not None:
            op = threshold_config["op"]
            threshold = threshold_config["threshold"]
            # Si CUMPLE con la condición, el indicador está en nivel CRÍTICO
            if mcda_module.check_condition(val, op, threshold):
                # Calcular cuánto excede el umbral
                if op in [">", ">="]:
                    diff = val - threshold  # Positivo = excede hacia arriba
                else:  # < o <=
                    diff = threshold - val  # Positivo = excede hacia abajo
                criticos.append((ind, val, op, threshold, diff))

    # Ordenar por diferencia (más críticos primero)
    criticos.sort(key=lambda x: abs(x[4]), reverse=True)

    for ind, val, op, threshold, diff in criticos[:15]:
        ind_short = ind[:50] + "..." if len(ind) > 50 else ind
        ind_short = ind_short.replace("|", "\\|")
        diff_str = f"+{diff:.1f}" if diff > 0 else f"{diff:.1f}"
        md_lines.append(f"| {ind_short} | {val:.2f} | {op} {threshold} | {diff_str} |")

    if len(criticos) > 15:
        md_lines.append(f"\n*... y {len(criticos) - 15} indicadores críticos más*\n")
    md_lines.append("")

    md_lines.append("---\n")

    # Recomendaciones de acción
    md_lines.append("## Recomendaciones de Acción\n")

    if escenario['nivel_alerta'] == 1:
        md_lines.append("### Acciones Recomendadas para Nivel 1 (Bajo Riesgo)")
        md_lines.append("1. Mantener vigilancia epidemiológica rutinaria")
        md_lines.append("2. Continuar actividades de educación preventiva en comunidad")
        md_lines.append("3. Realizar inspecciones periódicas de criaderos")
        md_lines.append("4. Monitorear condiciones climáticas")
        md_lines.append("5. Actualizar inventario de insumos y equipos")
    elif escenario['nivel_alerta'] == 2:
        md_lines.append("### Acciones Recomendadas para Nivel 2 (Riesgo Moderado)")
        md_lines.append("1. Intensificar vigilancia epidemiológica en zonas afectadas")
        md_lines.append("2. Activar brigadas de control larvario focalizado")
        md_lines.append("3. Difundir alertas preventivas a la comunidad")
        md_lines.append("4. Preparar recursos para posible escalada")
        md_lines.append("5. Coordinar con centros de salud para detección temprana")
        md_lines.append("6. Identificar y priorizar focos de infestación")
    elif escenario['nivel_alerta'] == 3:
        md_lines.append("### Acciones Recomendadas para Nivel 3 (Alto Riesgo)")
        md_lines.append("1. **ACTIVAR** control adulticida en zonas de brote")
        md_lines.append("2. **ACTIVAR** protocolo de triage en centros de salud")
        md_lines.append("3. Movilizar brigadas adicionales de control vectorial")
        md_lines.append("4. Coordinar acciones multisectoriales (agua, saneamiento, educación)")
        md_lines.append("5. Intensificar comunicación de riesgo a la población")
        md_lines.append("6. Solicitar apoyo de niveles superiores si es necesario")
        md_lines.append("7. Activar plan de contingencia hospitalario")
    else:
        md_lines.append("### Acciones Recomendadas para Nivel 4 (Emergencia)")
        md_lines.append("1. **DECLARAR** emergencia sanitaria")
        md_lines.append("2. **ACTIVAR** todos los recursos disponibles")
        md_lines.append("3. **SOLICITAR** apoyo externo (departamental/nacional)")
        md_lines.append("4. Control adulticida masivo en todas las zonas afectadas")
        md_lines.append("5. Reforzar capacidad hospitalaria con personal adicional")
        md_lines.append("6. Establecer centros de atención temporal si es necesario")
        md_lines.append("7. Comunicación de emergencia a toda la población")
        md_lines.append("8. Coordinar con todas las dependencias gubernamentales")
        md_lines.append("9. Implementar medidas extraordinarias de control")

    md_lines.append("")

    # Nota final
    md_lines.append("---\n")
    md_lines.append("*Reporte generado por el Sistema de Soporte a Decisiones para Control de Dengue*\n")
    md_lines.append("*Basado en el modelo MCDA (Multi-Criteria Decision Analysis) con umbrales consensuados por expertos*\n")

    # Escribir archivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

    return output_path


def generar_reporte_comparativo(resultados_escenarios, output_path=None):
    """
    Genera un reporte comparativo de todos los escenarios.

    Args:
        resultados_escenarios: Diccionario con resultados de todos los escenarios
        output_path: Ruta de salida (opcional)

    Returns:
        Ruta del archivo generado
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"reporte_comparativo_escenarios_{timestamp}.md"

    md_lines = []

    # Encabezado
    md_lines.append("# 📊 Reporte Comparativo de Escenarios Prescriptivos\n")
    md_lines.append(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_lines.append("---\n")

    # Resumen de escenarios
    md_lines.append("## Resumen de Escenarios\n")
    md_lines.append("| Escenario | Nivel | Indicadores Críticos | Top Estrategia |")
    md_lines.append("|-----------|-------|---------------------|----------------|")

    for esc_id, resultados in resultados_escenarios.items():
        escenario = resultados["escenario"]
        ranking = resultados["ranking"]
        indicadores_criticos = resultados["indicadores_criticos"]
        indicadores_normales = resultados["indicadores_normales"]
        total = indicadores_criticos + indicadores_normales
        pct = (indicadores_criticos / total * 100) if total > 0 else 0

        top_estrategia = ranking[0][0][:40] + "..." if len(ranking[0][0]) > 40 else ranking[0][0]
        top_estrategia = top_estrategia.replace("|", "\\|")

        md_lines.append(f"| {escenario['color']} {escenario['nombre'][:25]} | {escenario['nivel_alerta']}/4 | {indicadores_criticos}/{total} ({pct:.0f}%) | {top_estrategia} |")

    md_lines.append("")
    md_lines.append("---\n")

    # Comparación de Top 5 estrategias por escenario
    md_lines.append("## Comparación de Estrategias Recomendadas\n")

    for esc_id, resultados in resultados_escenarios.items():
        escenario = resultados["escenario"]
        ranking = resultados["ranking"]

        md_lines.append(f"### {escenario['color']} {escenario['nombre']}\n")
        md_lines.append("| Rank | Estrategia | Score |")
        md_lines.append("|------|------------|-------|")

        for est, rank, score, comp in ranking[:5]:
            est_short = est[:65] + "..." if len(est) > 65 else est
            est_short = est_short.replace("|", "\\|")
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
            md_lines.append(f"| {rank} {medal} | {est_short} | {score:.4f} |")
        md_lines.append("")

    md_lines.append("---\n")

    # Variación de indicadores clave entre escenarios
    md_lines.append("## Variación de Indicadores Clave entre Escenarios\n")

    indicadores_clave = [
        "Número de casos por semana epidemiológica",
        "Tasa de incidencia semanal",
        "Índice de Breteau (IB)",
        "Índice de vivienda (IV)",
        "Porcentaje de hospitalización por dengue",
        "Disponibilidad de insumos",
        "Percepción de riesgo comunitario",
    ]

    md_lines.append("| Indicador | Bajo Riesgo | Moderado | Alto | Emergencia | Umbral |")
    md_lines.append("|-----------|-------------|----------|------|------------|--------|")

    escenario_ids = ["bajo_riesgo", "riesgo_moderado", "alto_riesgo", "emergencia"]

    for ind in indicadores_clave:
        valores = []
        for esc_id in escenario_ids:
            if esc_id in resultados_escenarios:
                val = resultados_escenarios[esc_id]["indicator_values"].get(ind, "N/A")
                if isinstance(val, (int, float)):
                    valores.append(f"{val:.1f}")
                else:
                    valores.append(str(val))
            else:
                valores.append("N/A")

        # Obtener umbral
        umbral = "N/A"
        for esc_id in escenario_ids:
            if esc_id in resultados_escenarios:
                threshold_config = resultados_escenarios[esc_id]["indicator_thresholds"].get(ind)
                if threshold_config:
                    umbral = f"{threshold_config['op']} {threshold_config['threshold']}"
                break

        ind_short = ind[:30] + "..." if len(ind) > 30 else ind
        ind_short = ind_short.replace("|", "\\|")
        md_lines.append(f"| {ind_short} | {valores[0]} | {valores[1]} | {valores[2]} | {valores[3]} | {umbral} |")

    md_lines.append("")
    md_lines.append("---\n")

    # Conclusiones
    md_lines.append("## Conclusiones\n")
    md_lines.append("Los escenarios demuestran cómo el modelo prescriptivo adapta las recomendaciones ")
    md_lines.append("de estrategias según la gravedad de la situación epidemiológica:\n")
    md_lines.append("- **Bajo Riesgo:** Prioriza acciones preventivas y educativas sostenibles")
    md_lines.append("- **Riesgo Moderado:** Activa control larvario focalizado y comunicación de riesgo")
    md_lines.append("- **Alto Riesgo:** Despliega control adulticida intensivo y coordinación sectorial")
    md_lines.append("- **Emergencia:** Movilización total de recursos con apoyo externo\n")

    md_lines.append("---\n")
    md_lines.append("*Sistema de Soporte a Decisiones para Control de Dengue - Modelo Prescriptivo MCDA*\n")

    # Escribir archivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

    return output_path


def ejecutar_todos_escenarios(xlsx_path="Reporte_Estrategias_Indicadores.xlsx", generar_reportes=True):
    """
    Ejecuta todos los escenarios y genera reportes.

    Args:
        xlsx_path: Ruta al archivo de configuración
        generar_reportes: Si True, genera reportes en Markdown

    Returns:
        Diccionario con resultados de todos los escenarios
    """
    print("=" * 80)
    print("SISTEMA DE ESCENARIOS PRESCRIPTIVOS - CONTROL DE DENGUE")
    print("=" * 80)
    print()

    # Cargar módulo MCDA
    print("📂 Cargando modelo MCDA...")
    mcda_module = cargar_modelo_mcda()
    print("✅ Modelo cargado correctamente\n")

    resultados_escenarios = {}
    reportes_individuales = []

    for escenario_id in ESCENARIOS.keys():
        escenario = ESCENARIOS[escenario_id]
        print(f"\n{escenario['color']} Ejecutando escenario: {escenario['nombre']}")
        print("-" * 60)

        # Ejecutar escenario
        resultados = ejecutar_escenario(escenario_id, mcda_module, xlsx_path)
        resultados_escenarios[escenario_id] = resultados

        # Mostrar resumen
        ranking = resultados["ranking"]
        indicadores_criticos = resultados["indicadores_criticos"]
        indicadores_normales = resultados["indicadores_normales"]
        total_ind = indicadores_criticos + indicadores_normales

        print(f"   Indicadores en nivel crítico: {indicadores_criticos}/{total_ind} ({indicadores_criticos/total_ind*100:.0f}%)")
        print(f"   Top 3 estrategias recomendadas:")
        for est, rank, score, comp in ranking[:3]:
            est_short = est[:55] + "..." if len(est) > 55 else est
            print(f"     {rank}. {est_short}")
            print(f"        Score: {score:.4f} | Cumplimiento: {comp:.3f}")

        # Generar reporte individual
        if generar_reportes:
            reporte_path = generar_reporte_escenario(escenario_id, resultados)
            reportes_individuales.append(reporte_path)
            print(f"   📄 Reporte: {reporte_path}")

    # Generar reporte comparativo
    if generar_reportes:
        print("\n" + "=" * 60)
        print("Generando reporte comparativo...")
        reporte_comparativo = generar_reporte_comparativo(resultados_escenarios)
        print(f"📊 Reporte comparativo: {reporte_comparativo}")

    print("\n" + "=" * 80)
    print("EJECUCIÓN COMPLETADA")
    print("=" * 80)

    return resultados_escenarios


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    import sys

    xlsx_path = sys.argv[1] if len(sys.argv) > 1 else "Reporte_Estrategias_Indicadores.xlsx"

    resultados = ejecutar_todos_escenarios(xlsx_path)
