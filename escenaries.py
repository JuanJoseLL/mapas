ESCENARIO_NORMAL = {
    # --- INDICADORES EPIDEMIOLÓGICOS (bajos/controlados) ---
    "Número de casos por semana epidemiológica": 0.5,      
    "Letalidad": 0.0,                                       
    "Casos según clasificación clínica": 5,                 
    "Porcentaje de hospitalización por dengue": 2,          
    "Porcentaje de hospitalización por tipo": 5,            
    "Muertes probables": 0,                                 
    "% de casos confirmados por laboratorio": 85,           
    "Tipo de brote": 0,                                     
    "Serotipos circulantes": 1,                             
    "Tiempo entre síntoma y consulta": 1,                   
    
    # --- INDICADORES ENTOMOLÓGICOS (bajos) ---
    "Índice Aédico en sumidero": 2,                         
    "Índice de Breteau (IB)": 8,                            
    "Índice de vivienda (IV)": 4,                           
    "Índice pupal": 0.3,                                    
    "Índice de depósito (ID)": 2,                           # Umbral: >5% → bajo
    "Nivel de infestación crítica": 8,                      # Umbral: >20% → bajo
    "Índice de predio en concentraciones humanas": 0.3,     # Umbral: >1% → muy bajo
    "Tipo de depósito positivo dominante": 15,              # Umbral: ≥40% → bajo
    
    # --- INDICADORES CLIMÁTICOS (normales) ---
    "Índice de pluviosidad (días previos)": 25,             # Umbral: >50 mm → lluvia normal
    "Temperatura máxima (días previos)": 25,                # Umbral: >27°C → temperatura moderada
    
    # --- INDICADORES DE INFRAESTRUCTURA (buenos) ---
    "Cobertura de agua potable": 98,                        # Umbral: <90% → excelente cobertura
    "Continuidad en el servicio de acueducto": 23,          # Umbral: <20 h/día → buena continuidad
    "Estado de sumideros (limpios / obstruidos)": 8,        # Umbral: >20% → mayormente limpios
    "Estado de canales de aguas lluvias (limpios / obstruidos)": 12,  # Umbral: >30% → mayormente limpios
    "Cobertura de zonas verdes y árboles por barrio": 18,   # Umbral: >30% → moderado
    
    # --- INDICADORES SOCIALES (buenos) ---
    "Percepción de riesgo comunitario": 75,                 # Umbral: <50% → alta percepción
    "Prácticas preventivas": 70,                            # Umbral: <50% → buenas prácticas
    "Rechazo comunitario a intervención": 3,                # Umbral: >10% → bajo rechazo
    "Índice de Vulnerabilidad Socioeconómica": 0.35,        # Umbral: >0.6 → baja vulnerabilidad
    "Número de organizaciones sociales": 5,                 # Umbral: <2 → buena organización
    "Retención de aprendizaje comunitario": 85,             # Umbral: <70% → buena retención
    
    # --- INDICADORES DE COBERTURA (altos) ---
    "Cobertura de educación preventiva": 80,                # Umbral: <60% → buena cobertura
    "Cobertura en instituciones educativas": 92,            # Umbral: <80% → excelente
    "Cobertura de hogares alcanzados con mensajes de riesgo": 78,  # Umbral: <60% → buena
    "Inspección y control en lugares de concentración humana": 90, # Umbral: <80% → excelente
    "Inspección y control de sumideros": 88,                # Umbral: <80% → buena
    "Inspección y control en viviendas": 82,                # Umbral: <70% → buena
    "Inspección y control en cuerpos de agua (control biológico)": 85,  # Umbral: <80% → buena
    "Tiempo de respuesta de control vectorial desde la notificaci": 24,  # Umbral: >72h → respuesta rápida
    
    # --- INDICADORES OPERATIVOS (buenos) ---
    "Disponibilidad de insumos": 90,                        # Umbral: <70% → alta disponibilidad
    "Disponibilidad de equipos": 92,                        # Umbral: <80% → alta disponibilidad
    "Personal en terreno": 88,                              # Umbral: <75% → buen personal
    "Costos unitarios por intervención": 1500000,           # Umbral: >3M → costos bajos
    
    # --- INDICADORES BIOTECNOLÓGICOS ---
    "Establecimiento de Wolbachia": 30,                     # Umbral: >60% → no implementado ampliamente (no activa)
}



ESCENARIO_ALERTA = {
    # --- INDICADORES EPIDEMIOLÓGICOS (críticos) ---
    "Número de casos por semana epidemiológica": 15,        # Umbral: >3 → ¡ACTIVA!
    "Letalidad": 0.15,                                      # Umbral: >0.05% → ¡ACTIVA!
    "Casos según clasificación clínica": 35,                # Umbral: >20% → ¡ACTIVA!
    "Porcentaje de hospitalización por dengue": 22,         # Umbral: >10% → ¡ACTIVA!
    "Porcentaje de hospitalización por tipo": 30,           # Umbral: >20% → ¡ACTIVA!
    "Muertes probables": 3,                                 # Umbral: ≥1 → ¡ACTIVA!
    "% de casos confirmados por laboratorio": 45,           # Umbral: <60% → ¡ACTIVA!
    "Tipo de brote": 10,                                    # Umbral: ≥6 semanas → ¡ACTIVA!
    "Serotipos circulantes": 3,                             # Umbral: ≥2 → ¡ACTIVA!
    "Tiempo entre síntoma y consulta": 5,                   # Umbral: >3 días → ¡ACTIVA!
    
    # --- INDICADORES ENTOMOLÓGICOS (críticos) ---
    "Índice Aédico en sumidero": 12,                        # Umbral: >5% → ¡ACTIVA!
    "Índice de Breteau (IB)": 35,                           # Umbral: >20% → ¡ACTIVA!
    "Índice de vivienda (IV)": 18,                          # Umbral: >10% → ¡ACTIVA!
    "Índice pupal": 2.5,                                    # Umbral: >1 → ¡ACTIVA!
    "Índice de depósito (ID)": 12,                          # Umbral: >5% → ¡ACTIVA!
    "Nivel de infestación crítica": 35,                     # Umbral: >20% → ¡ACTIVA!
    "Índice de predio en concentraciones humanas": 3.5,     # Umbral: >1% → ¡ACTIVA!
    "Tipo de depósito positivo dominante": 55,              # Umbral: ≥40% → ¡ACTIVA!
    
    # --- INDICADORES CLIMÁTICOS (desfavorables) ---
    "Índice de pluviosidad (días previos)": 85,             # Umbral: >50 mm → ¡ACTIVA!
    "Temperatura máxima (días previos)": 32,                # Umbral: >27°C → ¡ACTIVA!
    
    # --- INDICADORES DE INFRAESTRUCTURA (deficientes) ---
    "Cobertura de agua potable": 75,                        # Umbral: <90% → ¡ACTIVA!
    "Continuidad en el servicio de acueducto": 14,          # Umbral: <20 h/día → ¡ACTIVA!
    "Estado de sumideros (limpios / obstruidos)": 35,       # Umbral: >20% → ¡ACTIVA!
    "Estado de canales de aguas lluvias (limpios / obstruidos)": 45,  # Umbral: >30% → ¡ACTIVA!
    "Cobertura de zonas verdes y árboles por barrio": 42,   # Umbral: >30% → ¡ACTIVA!
    
    # --- INDICADORES SOCIALES (deficientes) ---
    "Percepción de riesgo comunitario": 30,                 # Umbral: <50% → ¡ACTIVA!
    "Prácticas preventivas": 35,                            # Umbral: <50% → ¡ACTIVA!
    "Rechazo comunitario a intervención": 25,               # Umbral: >10% → ¡ACTIVA!
    "Índice de Vulnerabilidad Socioeconómica": 0.78,        # Umbral: >0.6 → ¡ACTIVA!
    "Número de organizaciones sociales": 1,                 # Umbral: <2 → ¡ACTIVA!
    "Retención de aprendizaje comunitario": 45,             # Umbral: <70% → ¡ACTIVA!
    
    # --- INDICADORES DE COBERTURA (bajos) ---
    "Cobertura de educación preventiva": 40,                # Umbral: <60% → ¡ACTIVA!
    "Cobertura en instituciones educativas": 55,            # Umbral: <80% → ¡ACTIVA!
    "Cobertura de hogares alcanzados con mensajes de riesgo": 35,  # Umbral: <60% → ¡ACTIVA!
    "Inspección y control en lugares de concentración humana": 50, # Umbral: <80% → ¡ACTIVA!
    "Inspección y control de sumideros": 55,                # Umbral: <80% → ¡ACTIVA!
    "Inspección y control en viviendas": 45,                # Umbral: <70% → ¡ACTIVA!
    "Inspección y control en cuerpos de agua (control biológico)": 50,  # Umbral: <80% → ¡ACTIVA!
    "Tiempo de respuesta de control vectorial desde la notificaci": 120, # Umbral: >72h → ¡ACTIVA!
    
    # --- INDICADORES OPERATIVOS (deficientes) ---
    "Disponibilidad de insumos": 50,                        # Umbral: <70% → ¡ACTIVA!
    "Disponibilidad de equipos": 60,                        # Umbral: <80% → ¡ACTIVA!
    "Personal en terreno": 55,                              # Umbral: <75% → ¡ACTIVA!
    "Costos unitarios por intervención": 5500000,           # Umbral: >3M → ¡ACTIVA!
    
    # --- INDICADORES BIOTECNOLÓGICOS ---
    "Establecimiento de Wolbachia": 75,                     # Umbral: >60% → ¡ACTIVA! (estrategia en marcha)
}


ESCENARIO_MIXTO = {
    # --- INDICADORES EPIDEMIOLÓGICOS (algunos en alerta) ---
    "Número de casos por semana epidemiológica": 5,         # Umbral: >3 → ¡ACTIVA! (brote incipiente)
    "Letalidad": 0.02,                                       # Umbral: >0.05% → OK (sin muertes aún)
    "Casos según clasificación clínica": 25,                  # Umbral: >20% → ¡ACTIVA! (casos graves)
    "Porcentaje de hospitalización por dengue": 8,          # Umbral: >10% → OK (aún controlado)
    "Porcentaje de hospitalización por tipo": 15,            # Umbral: >20% → OK
    "Muertes probables": 0,                                   # Umbral: ≥1 → OK (sin muertes)
    "% de casos confirmados por laboratorio": 55,           # Umbral: <60% → ¡ACTIVA! (confirmación baja)
    "Tipo de brote": 4,                                      # Umbral: ≥6 semanas → OK (brote corto)
    "Serotipos circulantes": 2,                              # Umbral: ≥2 → ¡ACTIVA! (múltiples serotipos)
    "Tiempo entre síntoma y consulta": 4,                    # Umbral: >3 días → ¡ACTIVA! (demora)
    
    # --- INDICADORES ENTOMOLÓGICOS (algunos críticos) ---
    "Índice Aédico en sumidero": 8,                          # Umbral: >5% → ¡ACTIVA! (infestación alta)
    "Índice de Breteau (IB)": 25,                            # Umbral: >20% → ¡ACTIVA! (crítico)
    "Índice de vivienda (IV)": 12,                           # Umbral: >10% → ¡ACTIVA! (crítico)
    "Índice pupal": 0.8,                                     # Umbral: >1 → OK (aún bajo)
    "Índice de depósito (ID)": 7,                            # Umbral: >5% → ¡ACTIVA! (alto)
    "Nivel de infestación crítica": 25,                      # Umbral: >20% → ¡ACTIVA! (crítico)
    "Índice de predio en concentraciones humanas": 1.5,       # Umbral: >1% → ¡ACTIVA! (alto)
    "Tipo de depósito positivo dominante": 50,               # Umbral: ≥40% → ¡ACTIVA! (tanques/lavaderos)
    
    # --- INDICADORES CLIMÁTICOS (desfavorables) ---
    "Índice de pluviosidad (días previos)": 65,              # Umbral: >50 mm → ¡ACTIVA! (lluvias intensas)
    "Temperatura máxima (días previos)": 29,                  # Umbral: >27°C → ¡ACTIVA! (calor)
    
    # --- INDICADORES DE INFRAESTRUCTURA (algunos problemas) ---
    "Cobertura de agua potable": 85,                         # Umbral: <90% → ¡ACTIVA! (cobertura baja)
    "Continuidad en el servicio de acueducto": 18,           # Umbral: <20 h/día → ¡ACTIVA! (intermitencia)
    "Estado de sumideros (limpios / obstruidos)": 25,        # Umbral: >20% → ¡ACTIVA! (obstruidos)
    "Estado de canales de aguas lluvias (limpios / obstruidos)": 35,  # Umbral: >30% → ¡ACTIVA! (obstruidos)
    "Cobertura de zonas verdes y árboles por barrio": 25,    # Umbral: >30% → OK (moderado)
    
    # --- INDICADORES SOCIALES (algunos problemas) ---
    "Percepción de riesgo comunitario": 45,                  # Umbral: <50% → ¡ACTIVA! (percepción baja)
    "Prácticas preventivas": 45,                             # Umbral: <50% → ¡ACTIVA! (prácticas bajas)
    "Rechazo comunitario a intervención": 8,                 # Umbral: >10% → OK (rechazo bajo)
    "Índice de Vulnerabilidad Socioeconómica": 0.55,        # Umbral: >0.6 → OK (vulnerabilidad moderada)
    "Número de organizaciones sociales": 3,                   # Umbral: <2 → OK (buena organización)
    "Retención de aprendizaje comunitario": 65,              # Umbral: <70% → ¡ACTIVA! (retención baja)
    
    # --- INDICADORES DE COBERTURA (algunos bajos) ---
    "Cobertura de educación preventiva": 55,                # Umbral: <60% → ¡ACTIVA! (cobertura baja)
    "Cobertura en instituciones educativas": 75,              # Umbral: <80% → ¡ACTIVA! (cobertura baja)
    "Cobertura de hogares alcanzados con mensajes de riesgo": 50,  # Umbral: <60% → ¡ACTIVA! (baja)
    "Inspección y control en lugares de concentración humana": 70, # Umbral: <80% → ¡ACTIVA! (baja)
    "Inspección y control de sumideros": 75,                 # Umbral: <80% → ¡ACTIVA! (baja)
    "Inspección y control en viviendas": 65,                 # Umbral: <70% → ¡ACTIVA! (baja)
    "Inspección y control en cuerpos de agua (control biológico)": 75,  # Umbral: <80% → ¡ACTIVA! (baja)
    "Tiempo de respuesta de control vectorial desde la notificaci": 60,  # Umbral: >72h → OK (respuesta rápida)
    
    # --- INDICADORES OPERATIVOS (algunos problemas) ---
    "Disponibilidad de insumos": 65,                         # Umbral: <70% → ¡ACTIVA! (disponibilidad baja)
    "Disponibilidad de equipos": 75,                         # Umbral: <80% → ¡ACTIVA! (disponibilidad baja)
    "Personal en terreno": 70,                               # Umbral: <75% → ¡ACTIVA! (personal insuficiente)
    "Costos unitarios por intervención": 2500000,           # Umbral: >3M → OK (costos controlados)
    
    # --- INDICADORES BIOTECNOLÓGICOS ---
    "Establecimiento de Wolbachia": 45,                       # Umbral: >60% → OK (implementación parcial)
}


# =============================================================================
# ESCENARIO: TODOS LOS BARRIOS EN CRÍTICO (EMERGENCIA)
# =============================================================================
# Este escenario representa una crisis sanitaria generalizada donde TODOS los
# barrios de la ciudad están en estado de emergencia, pero con diferenciación
# de estrategias según las características específicas de cada zona.
#
# Perfiles de zona:
# - ZONA_AGUA_INTERMITENTE: Barrios con problemas de suministro de agua
# - ZONA_ALTA_DENSIDAD: Barrios con hacinamiento y alta densidad poblacional
# - ZONA_CONSTRUCCIONES: Barrios con muchas obras y escorrentías
# - ZONA_DIFICIL_ACCESO: Barrios con problemas de accesibilidad
# - ZONA_RECHAZO_COMUNITARIO: Barrios con resistencia a intervenciones
# =============================================================================

ESCENARIO_TODOS_CRITICOS_BASE = {
    # --- INDICADORES EPIDEMIOLÓGICOS (CRÍTICOS EN TODA LA CIUDAD) ---
    "Número de casos por semana epidemiológica": 20,         # Umbral: >3 → ¡CRÍTICO!
    "Letalidad": 0.18,                                        # Umbral: >0.05% → ¡CRÍTICO!
    "Casos según clasificación clínica": 45,                  # Umbral: >20% → ¡CRÍTICO!
    "Porcentaje de hospitalización por dengue": 30,          # Umbral: >10% → ¡CRÍTICO!
    "Porcentaje de hospitalización por tipo": 40,            # Umbral: >20% → ¡CRÍTICO!
    "Muertes probables": 5,                                   # Umbral: ≥1 → ¡CRÍTICO!
    "% de casos confirmados por laboratorio": 35,            # Umbral: <60% → ¡CRÍTICO!
    "Tipo de brote": 14,                                      # Umbral: ≥6 semanas → ¡CRÍTICO!
    "Serotipos circulantes": 3,                               # Umbral: ≥2 → ¡CRÍTICO!
    "Tiempo entre síntoma y consulta": 7,                    # Umbral: >3 días → ¡CRÍTICO!

    # --- INDICADORES ENTOMOLÓGICOS (CRÍTICOS EN TODA LA CIUDAD) ---
    "Índice Aédico en sumidero": 18,                          # Umbral: >5% → ¡CRÍTICO!
    "Índice de Breteau (IB)": 55,                             # Umbral: >20% → ¡CRÍTICO!
    "Índice de vivienda (IV)": 35,                            # Umbral: >10% → ¡CRÍTICO!
    "Índice pupal": 3.2,                                      # Umbral: >1 → ¡CRÍTICO!
    "Índice de depósito (ID)": 25,                            # Umbral: >5% → ¡CRÍTICO!
    "Nivel de infestación crítica": 55,                       # Umbral: >20% → ¡CRÍTICO!
    "Índice de predio en concentraciones humanas": 5.0,      # Umbral: >1% → ¡CRÍTICO!
    "Tipo de depósito positivo dominante": 70,               # Umbral: ≥40% → ¡CRÍTICO!

    # --- INDICADORES CLIMÁTICOS (CONDICIONES EXTREMAS) ---
    "Índice de pluviosidad (días previos)": 130,              # Umbral: >50 mm → ¡CRÍTICO!
    "Temperatura máxima (días previos)": 34,                  # Umbral: >27°C → ¡CRÍTICO!

    # --- INDICADORES OPERATIVOS (COLAPSADOS) ---
    "Disponibilidad de insumos": 40,                          # Umbral: <70% → ¡CRÍTICO!
    "Disponibilidad de equipos": 45,                          # Umbral: <80% → ¡CRÍTICO!
    "Personal en terreno": 42,                                # Umbral: <75% → ¡CRÍTICO!
    "Costos unitarios por intervención": 6500000,            # Umbral: >3M → ¡CRÍTICO!

    # --- INDICADORES DE COBERTURA (INSUFICIENTES) ---
    "Cobertura de educación preventiva": 25,                 # Umbral: <60% → ¡CRÍTICO!
    "Cobertura en instituciones educativas": 40,             # Umbral: <80% → ¡CRÍTICO!
    "Cobertura de hogares alcanzados con mensajes de riesgo": 22,  # Umbral: <60% → ¡CRÍTICO!
    "Inspección y control en lugares de concentración humana": 38, # Umbral: <80% → ¡CRÍTICO!
    "Inspección y control de sumideros": 35,                 # Umbral: <80% → ¡CRÍTICO!
    "Inspección y control en viviendas": 32,                 # Umbral: <70% → ¡CRÍTICO!
    "Inspección y control en cuerpos de agua (control biológico)": 30,  # Umbral: <80% → ¡CRÍTICO!
    "Tiempo de respuesta de control vectorial desde la notificaci": 168, # Umbral: >72h → ¡CRÍTICO!

    # --- INDICADORES BIOTECNOLÓGICOS ---
    "Establecimiento de Wolbachia": 25,                       # Umbral: >60% → Insuficiente
}

# Perfiles diferenciados por tipo de zona para escenario CRÍTICO
PERFILES_CRITICOS = {
    # -------------------------------------------------------------------------
    # ZONA CON INTERMITENCIA DE AGUA
    # Barrios donde el suministro de agua es irregular, lo que lleva a
    # almacenamiento doméstico en tanques y recipientes - principales criaderos
    # Estrategia principal: Control de depósitos domésticos y educación
    # -------------------------------------------------------------------------
    "agua_intermitente": {
        "nombre": "Zona con Intermitencia de Agua",
        "descripcion": "Barrios con suministro de agua irregular que almacenan agua en tanques y recipientes",
        "color": "🔴",
        "comunas": ["14", "15", "21"],  # Comunas de Aguablanca con problemas de agua
        "barrios_ejemplo": ["Marroquín I", "Potrero Grande", "Manuela Beltrán", "Alfonso Bonilla Aragón"],
        "indicadores_especificos": {
            "Continuidad en el servicio de acueducto": 8,          # Solo 8 horas/día de agua
            "Cobertura de agua potable": 65,                       # Baja cobertura
            "Tipo de depósito positivo dominante": 85,             # Tanques y albercas dominantes
            "Índice de depósito (ID)": 32,                         # Muy alto por tanques
            "Prácticas preventivas": 20,                           # Muy bajas - no tapan tanques
        },
        "estrategias_prioritarias": [
            "Control físico en depósitos de almacenamiento doméstico",
            "Larvicidas químicos en tanques y albercas",
            "Educación sobre almacenamiento seguro de agua",
            "Coordinación con empresa de acueducto",
            "Distribución de tapas para tanques",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 2,
            "costo_operativo": 8,
            "tiempo_cobertura": 3,
            "dependencias_externas": 9,  # Alta dependencia de sector agua
            "aceptacion_comunidad": 4,
            "acceso_predios": 5,
            "percepcion_riesgo": 8,
            "resistencia_vector": 6,
            "otros_vectores": 3,
            "efectividad_esperada": 5,
            "magnitud_brote": 10,
        },
    },

    # -------------------------------------------------------------------------
    # ZONA DE ALTA DENSIDAD POBLACIONAL
    # Barrios con hacinamiento donde la transmisión es muy rápida
    # Estrategia principal: Control adulticida masivo y protección individual
    # -------------------------------------------------------------------------
    "alta_densidad": {
        "nombre": "Zona de Alta Densidad Poblacional",
        "descripcion": "Barrios con hacinamiento y alta densidad donde la transmisión es explosiva",
        "color": "🔴",
        "comunas": ["13", "16", "20"],  # Comunas densamente pobladas
        "barrios_ejemplo": ["El Retiro", "Charco Azul", "Sardi", "Lleras Camargo"],
        "indicadores_especificos": {
            "Densidad poblacional": 22000,                         # Muy alta densidad
            "Índice de Vulnerabilidad Socioeconómica": 0.88,      # Alta vulnerabilidad
            "Número de casos por semana epidemiológica": 28,       # Muchos casos por densidad
            "Razón de crecimiento epidémico frente al año anterior": 2.5,  # Crecimiento explosivo
            "Tasa de incidencia semanal": 120,                     # Muy alta incidencia
        },
        "estrategias_prioritarias": [
            "Aplicar adulticidas químicos (malatión/deltametrina) masivamente",
            "Fomentar uso de protección individual (repelentes, mosquiteros)",
            "Implementar protocolos de triage de emergencia",
            "Establecer puestos de hidratación y atención rápida",
            "Búsqueda activa de casos febriles",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 1,
            "costo_operativo": 10,
            "tiempo_cobertura": 2,
            "dependencias_externas": 7,
            "aceptacion_comunidad": 3,
            "acceso_predios": 3,  # Difícil por hacinamiento
            "percepcion_riesgo": 10,
            "resistencia_vector": 7,
            "otros_vectores": 5,
            "efectividad_esperada": 4,
            "magnitud_brote": 10,
        },
    },

    # -------------------------------------------------------------------------
    # ZONA CON CONSTRUCCIONES Y ESCORRENTÍAS
    # Barrios con muchas obras y problemas de drenaje
    # Estrategia principal: Control de sumideros y escorrentías
    # -------------------------------------------------------------------------
    "construcciones": {
        "nombre": "Zona de Construcciones y Escorrentías",
        "descripcion": "Barrios con obras activas y problemas de drenaje que generan criaderos",
        "color": "🔴",
        "comunas": ["06", "07", "18"],  # Comunas con desarrollo urbanístico
        "barrios_ejemplo": ["Ciudad Córdoba", "Primero de Mayo", "Meléndez"],
        "indicadores_especificos": {
            "Sector económico": 8,                                 # Muchas obras/km²
            "Estado de sumideros (limpios / obstruidos)": 65,     # Mayoría obstruidos
            "Estado de canales de aguas lluvias (limpios / obstruidos)": 70,  # Muy obstruidos
            "Índice Aédico en sumidero": 25,                       # Muy alto en sumideros
            "Cobertura de zonas verdes y árboles por barrio": 50, # Mucha vegetación = hábitats
        },
        "estrategias_prioritarias": [
            "Monitoreo de condiciones climáticas y gestión de escorrentías",
            "Inspección y control intensivo de sumideros",
            "Coordinación con sector construcción para manejo de aguas",
            "Control larvario en obras y áreas de drenaje",
            "Tecnologías innovadoras (drones para mapeo de focos)",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 3,
            "costo_operativo": 8,
            "tiempo_cobertura": 3,
            "dependencias_externas": 8,  # Coordinación con constructoras
            "aceptacion_comunidad": 6,
            "acceso_predios": 4,  # Difícil en obras
            "percepcion_riesgo": 7,
            "resistencia_vector": 5,
            "otros_vectores": 6,
            "efectividad_esperada": 5,
            "magnitud_brote": 9,
        },
    },

    # -------------------------------------------------------------------------
    # ZONA DE DIFÍCIL ACCESO
    # Barrios en ladera o con problemas de accesibilidad
    # Estrategia principal: Tecnología y coordinación comunitaria
    # -------------------------------------------------------------------------
    "dificil_acceso": {
        "nombre": "Zona de Difícil Acceso",
        "descripcion": "Barrios en ladera o con vías de difícil acceso para brigadas",
        "color": "🔴",
        "comunas": ["01", "20"],  # Comunas en ladera (Siloé, Terrón Colorado)
        "barrios_ejemplo": ["Siloé", "Terrón Colorado", "Brisas de Mayo", "Belén"],
        "indicadores_especificos": {
            "Cobertura territorial por brigada": 0.3,              # Muy baja cobertura
            "Tiempo de alistamiento de brigadas": 96,              # Mucho tiempo para llegar
            "Tiempo promedio de ejecución": 12,                    # Muy lento
            "Acceso a predios": 25,                                # Muy difícil acceso
            "Rechazo comunitario a intervención": 8,               # Algo de rechazo
        },
        "estrategias_prioritarias": [
            "Tecnologías innovadoras (drones, sensores remotos)",
            "Vigilancia participativa con líderes comunitarios",
            "Métodos biológicos (peces larvívoros) en tanques accesibles",
            "Capacitación de voluntarios locales",
            "Articulación institucional con juntas de acción comunal",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 2,
            "costo_operativo": 9,
            "tiempo_cobertura": 1,  # Muy difícil cubrir
            "dependencias_externas": 6,
            "aceptacion_comunidad": 5,
            "acceso_predios": 2,  # Muy difícil
            "percepcion_riesgo": 8,
            "resistencia_vector": 6,
            "otros_vectores": 4,
            "efectividad_esperada": 3,
            "magnitud_brote": 9,
        },
    },

    # -------------------------------------------------------------------------
    # ZONA CON RECHAZO COMUNITARIO
    # Barrios donde la comunidad se resiste a las intervenciones
    # Estrategia principal: Comunicación y educación intensiva
    # -------------------------------------------------------------------------
    "rechazo_comunitario": {
        "nombre": "Zona con Rechazo Comunitario",
        "descripcion": "Barrios donde la comunidad muestra resistencia a las intervenciones de salud",
        "color": "🔴",
        "comunas": ["03", "04", "09"],  # Comunas con historial de rechazo
        "barrios_ejemplo": ["San Nicolás", "La Merced", "Obrero", "Junín"],
        "indicadores_especificos": {
            "Rechazo comunitario a intervención": 35,              # Alto rechazo
            "Percepción de riesgo comunitario": 20,               # No perciben el riesgo
            "Prácticas preventivas": 15,                           # Muy bajas
            "Retención de aprendizaje comunitario": 30,           # No retienen información
            "Número de organizaciones sociales": 0,                # Sin líderes comunitarios
        },
        "estrategias_prioritarias": [
            "Campañas educativas con líderes religiosos y comunitarios",
            "Difundir mensajes preventivos por medios locales",
            "Fortalecer percepción de riesgo con testimonios",
            "Jornadas de sensibilización puerta a puerta",
            "Alianzas con organizaciones de base",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 4,
            "costo_operativo": 6,
            "tiempo_cobertura": 4,
            "dependencias_externas": 5,
            "aceptacion_comunidad": 1,  # Muy baja
            "acceso_predios": 2,  # No permiten entrar
            "percepcion_riesgo": 3,  # Muy baja
            "resistencia_vector": 5,
            "otros_vectores": 4,
            "efectividad_esperada": 3,
            "magnitud_brote": 8,
        },
    },
}


# =============================================================================
# ESCENARIO: TODOS LOS BARRIOS EN VERDE (BAJO RIESGO)
# =============================================================================
# Este escenario representa una situación ideal donde TODOS los barrios están
# en bajo riesgo, pero con estrategias diferenciadas de MANTENIMIENTO según
# las características históricas y vulnerabilidades de cada zona.
#
# Perfiles de zona:
# - ZONA_HISTORICAMENTE_PROBLEMATICA: Requiere vigilancia intensiva
# - ZONA_BIEN_ORGANIZADA: Aprovecha la organización comunitaria
# - ZONA_BUENA_INFRAESTRUCTURA: Usa tecnología para monitoreo
# - ZONA_COBERTURA_AGUA_VARIABLE: Educa en almacenamiento seguro
# - ZONA_TRANSICION: Zonas que mejoraron recientemente
# =============================================================================

ESCENARIO_TODOS_VERDES_BASE = {
    # --- INDICADORES EPIDEMIOLÓGICOS (CONTROLADOS EN TODA LA CIUDAD) ---
    "Número de casos por semana epidemiológica": 0.5,        # Umbral: >3 → OK, muy bajo
    "Letalidad": 0.0,                                         # Umbral: >0.05% → OK, sin muertes
    "Casos según clasificación clínica": 3,                   # Umbral: >20% → OK
    "Porcentaje de hospitalización por dengue": 1,           # Umbral: >10% → OK
    "Porcentaje de hospitalización por tipo": 2,             # Umbral: >20% → OK
    "Muertes probables": 0,                                   # Umbral: ≥1 → OK
    "% de casos confirmados por laboratorio": 92,            # Umbral: <60% → OK, alta confirmación
    "Tipo de brote": 0,                                       # Umbral: ≥6 semanas → OK, sin brote
    "Serotipos circulantes": 1,                               # Umbral: ≥2 → OK
    "Tiempo entre síntoma y consulta": 1,                    # Umbral: >3 días → OK, rápido

    # --- INDICADORES ENTOMOLÓGICOS (CONTROLADOS EN TODA LA CIUDAD) ---
    "Índice Aédico en sumidero": 1,                           # Umbral: >5% → OK
    "Índice de Breteau (IB)": 5,                              # Umbral: >20% → OK
    "Índice de vivienda (IV)": 3,                             # Umbral: >10% → OK
    "Índice pupal": 0.2,                                      # Umbral: >1 → OK
    "Índice de depósito (ID)": 1.5,                           # Umbral: >5% → OK
    "Nivel de infestación crítica": 4,                        # Umbral: >20% → OK
    "Índice de predio en concentraciones humanas": 0.3,      # Umbral: >1% → OK
    "Tipo de depósito positivo dominante": 12,               # Umbral: ≥40% → OK

    # --- INDICADORES CLIMÁTICOS (FAVORABLES) ---
    "Índice de pluviosidad (días previos)": 20,               # Umbral: >50 mm → OK, poca lluvia
    "Temperatura máxima (días previos)": 24,                  # Umbral: >27°C → OK, temperatura moderada

    # --- INDICADORES OPERATIVOS (ÓPTIMOS) ---
    "Disponibilidad de insumos": 95,                          # Umbral: <70% → OK, alta disponibilidad
    "Disponibilidad de equipos": 96,                          # Umbral: <80% → OK
    "Personal en terreno": 92,                                # Umbral: <75% → OK
    "Costos unitarios por intervención": 1200000,            # Umbral: >3M → OK, costos bajos

    # --- INDICADORES DE COBERTURA (ÓPTIMOS) ---
    "Cobertura de educación preventiva": 88,                 # Umbral: <60% → OK
    "Cobertura en instituciones educativas": 95,             # Umbral: <80% → OK
    "Cobertura de hogares alcanzados con mensajes de riesgo": 85,  # Umbral: <60% → OK
    "Inspección y control en lugares de concentración humana": 92, # Umbral: <80% → OK
    "Inspección y control de sumideros": 94,                 # Umbral: <80% → OK
    "Inspección y control en viviendas": 88,                 # Umbral: <70% → OK
    "Inspección y control en cuerpos de agua (control biológico)": 90,  # Umbral: <80% → OK
    "Tiempo de respuesta de control vectorial desde la notificaci": 18, # Umbral: >72h → OK, muy rápido

    # --- INDICADORES SOCIALES (FAVORABLES) ---
    "Percepción de riesgo comunitario": 78,                  # Umbral: <50% → OK, alta percepción
    "Prácticas preventivas": 82,                              # Umbral: <50% → OK
    "Rechazo comunitario a intervención": 2,                 # Umbral: >10% → OK, bajo rechazo
    "Retención de aprendizaje comunitario": 85,              # Umbral: <70% → OK

    # --- INDICADORES DE INFRAESTRUCTURA (BUENOS) ---
    "Cobertura de agua potable": 97,                         # Umbral: <90% → OK
    "Continuidad en el servicio de acueducto": 23,           # Umbral: <20 h/día → OK
    "Estado de sumideros (limpios / obstruidos)": 8,         # Umbral: >20% → OK
    "Estado de canales de aguas lluvias (limpios / obstruidos)": 10,  # Umbral: >30% → OK

    # --- INDICADORES BIOTECNOLÓGICOS ---
    "Establecimiento de Wolbachia": 72,                       # Umbral: >60% → Activo, contribuyendo
}

# Perfiles diferenciados por tipo de zona para escenario VERDE
PERFILES_VERDES = {
    # -------------------------------------------------------------------------
    # ZONA HISTÓRICAMENTE PROBLEMÁTICA
    # Barrios que fueron focos de dengue pero ahora están controlados
    # Estrategia principal: Vigilancia intensiva para prevenir recaídas
    # -------------------------------------------------------------------------
    "historicamente_problematica": {
        "nombre": "Zona Históricamente Problemática",
        "descripcion": "Barrios que tuvieron brotes severos y requieren vigilancia intensiva",
        "color": "🟢",
        "comunas": ["13", "14", "15", "21"],  # Ex-zonas críticas de Aguablanca
        "barrios_ejemplo": ["Marroquín I", "Potrero Grande", "El Retiro", "Charco Azul"],
        "indicadores_especificos": {
            "Número de ovitrampas positivas": 35,                  # Monitoreo activo con ovitrampas
            "Tasa de reinfestación": 6,                            # Vigilar reinfestación
            "Inicio y mantenimiento de brote histórico": 2,        # Historial de brotes
            "Índice de Vulnerabilidad Socioeconómica": 0.55,      # Aún vulnerable
        },
        "estrategias_prioritarias": [
            "Mantener vigilancia epidemiológica intensiva con ovitrampas",
            "Inspecciones periódicas de criaderos semanales",
            "Alerta temprana con modelos predictivos",
            "Mantener stocks de insumos para respuesta rápida",
            "Comunicación continua de riesgo a la comunidad",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 8,
            "costo_operativo": 4,
            "tiempo_cobertura": 7,
            "dependencias_externas": 3,
            "aceptacion_comunidad": 8,  # Ya aceptan intervenciones
            "acceso_predios": 8,
            "percepcion_riesgo": 7,  # Recuerdan los brotes
            "resistencia_vector": 3,
            "otros_vectores": 2,
            "efectividad_esperada": 8,
            "magnitud_brote": 2,
        },
    },

    # -------------------------------------------------------------------------
    # ZONA BIEN ORGANIZADA
    # Barrios con buena organización comunitaria y participación
    # Estrategia principal: Vigilancia participativa comunitaria
    # -------------------------------------------------------------------------
    "bien_organizada": {
        "nombre": "Zona Bien Organizada",
        "descripcion": "Barrios con fuerte organización comunitaria y participación ciudadana",
        "color": "🟢",
        "comunas": ["02", "05", "17", "19"],  # Comunas con alta organización
        "barrios_ejemplo": ["Granada", "San Fernando", "El Peñón", "Ciudad Jardín"],
        "indicadores_especificos": {
            "Número de organizaciones sociales": 8,                # Muchas organizaciones activas
            "Retención de aprendizaje comunitario": 92,           # Alta retención
            "Percepción de riesgo comunitario": 85,               # Alta percepción
            "Prácticas preventivas": 90,                           # Excelentes prácticas
            "Rechazo comunitario a intervención": 1,              # Casi nulo rechazo
        },
        "estrategias_prioritarias": [
            "Vigilancia participativa con voluntarios comunitarios",
            "Campañas educativas lideradas por la comunidad",
            "Fortalecer redes de vecinos vigilantes",
            "Reconocimiento a barrios libres de criaderos",
            "Comités de salud barriales activos",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 9,
            "costo_operativo": 2,  # Bajo costo por participación comunitaria
            "tiempo_cobertura": 8,
            "dependencias_externas": 2,
            "aceptacion_comunidad": 10,  # Excelente
            "acceso_predios": 9,
            "percepcion_riesgo": 8,
            "resistencia_vector": 2,
            "otros_vectores": 2,
            "efectividad_esperada": 9,
            "magnitud_brote": 1,
        },
    },

    # -------------------------------------------------------------------------
    # ZONA CON BUENA INFRAESTRUCTURA
    # Barrios con infraestructura moderna que permite monitoreo tecnológico
    # Estrategia principal: Monitoreo con tecnología innovadora
    # -------------------------------------------------------------------------
    "buena_infraestructura": {
        "nombre": "Zona con Buena Infraestructura",
        "descripcion": "Barrios con infraestructura moderna que permite uso de tecnología",
        "color": "🟢",
        "comunas": ["22", "03", "10"],  # Comunas con buena infraestructura
        "barrios_ejemplo": ["Ciudad Jardín", "El Ingenio", "Santa Teresita", "Centenario"],
        "indicadores_especificos": {
            "Cobertura de agua potable": 99,                       # Excelente cobertura
            "Continuidad en el servicio de acueducto": 24,        # 24 horas de agua
            "Estado de sumideros (limpios / obstruidos)": 3,      # Bien mantenidos
            "Estado de canales de aguas lluvias (limpios / obstruidos)": 5,
            "Frecuencia de recolección de residuos sólidos": 5,   # Excelente recolección
        },
        "estrategias_prioritarias": [
            "Datos meteorológicos y modelos de alerta temprana",
            "Tecnologías innovadoras (sensores, mapeo digital)",
            "Mantenimiento preventivo de sumideros y drenajes",
            "Monitoreo automatizado de índices entomológicos",
            "Integración con sistemas de ciudad inteligente",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 9,
            "costo_operativo": 3,
            "tiempo_cobertura": 9,
            "dependencias_externas": 2,
            "aceptacion_comunidad": 9,
            "acceso_predios": 9,
            "percepcion_riesgo": 7,
            "resistencia_vector": 2,
            "otros_vectores": 1,
            "efectividad_esperada": 9,
            "magnitud_brote": 1,
        },
    },

    # -------------------------------------------------------------------------
    # ZONA CON COBERTURA DE AGUA VARIABLE
    # Barrios donde aunque hay agua, hay variabilidad que requiere educación
    # Estrategia principal: Educación en almacenamiento seguro
    # -------------------------------------------------------------------------
    "cobertura_agua_variable": {
        "nombre": "Zona con Cobertura de Agua Variable",
        "descripcion": "Barrios con servicio de agua que a veces tiene interrupciones",
        "color": "🟢",
        "comunas": ["06", "07", "08", "11", "12"],  # Comunas con servicio variable
        "barrios_ejemplo": ["Floralia", "Alfonso López", "Villacolombia", "El Poblado"],
        "indicadores_especificos": {
            "Continuidad en el servicio de acueducto": 20,        # Justo en el límite
            "Cobertura de agua potable": 92,                       # Buena pero no perfecta
            "Tipo de depósito positivo dominante": 25,            # Algunos tanques
            "Prácticas preventivas": 75,                           # Pueden mejorar
        },
        "estrategias_prioritarias": [
            "Educación sobre almacenamiento seguro de agua",
            "Promover tapado de tanques y recipientes",
            "Inspección periódica de depósitos de agua",
            "Coordinación con acueducto para alertar cortes",
            "Distribución de larvicidas para autoaplicación",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 8,
            "costo_operativo": 3,
            "tiempo_cobertura": 7,
            "dependencias_externas": 4,
            "aceptacion_comunidad": 8,
            "acceso_predios": 8,
            "percepcion_riesgo": 6,
            "resistencia_vector": 2,
            "otros_vectores": 2,
            "efectividad_esperada": 8,
            "magnitud_brote": 2,
        },
    },

    # -------------------------------------------------------------------------
    # ZONA EN TRANSICIÓN
    # Barrios que recientemente mejoraron su situación epidemiológica
    # Estrategia principal: Consolidar logros y prevenir retrocesos
    # -------------------------------------------------------------------------
    "transicion": {
        "nombre": "Zona en Transición",
        "descripcion": "Barrios que mejoraron recientemente y necesitan consolidar logros",
        "color": "🟢",
        "comunas": ["16", "18", "20"],  # Comunas que han mejorado
        "barrios_ejemplo": ["Mariano Ramos", "Meléndez", "Siloé (sector mejorado)"],
        "indicadores_especificos": {
            "Razón de crecimiento epidémico frente al año anterior": 0.5,  # Mejorando
            "Variación porcentual": -15,                           # Reducción de casos
            "Reducción de índice de Breteau tras control larvario": 45,  # Buen efecto
            "Índice de Breteau (IB)": 8,                           # Mejorado pero vigilar
        },
        "estrategias_prioritarias": [
            "Mantener intensidad de intervenciones actuales",
            "Evaluación continua de efectividad",
            "Fortalecer sostenibilidad del programa",
            "Documentar lecciones aprendidas",
            "Preparar transferencia de buenas prácticas",
        ],
        "factores_estrategia": {
            "disponibilidad_recursos": 7,
            "costo_operativo": 4,
            "tiempo_cobertura": 7,
            "dependencias_externas": 3,
            "aceptacion_comunidad": 8,
            "acceso_predios": 7,
            "percepcion_riesgo": 7,
            "resistencia_vector": 3,
            "otros_vectores": 2,
            "efectividad_esperada": 8,
            "magnitud_brote": 2,
        },
    },
}


# =============================================================================
# FUNCIONES AUXILIARES PARA OBTENER ESCENARIOS ESPECÍFICOS POR ZONA
# =============================================================================

def obtener_escenario_critico_por_zona(perfil_zona):
    """
    Obtiene el escenario crítico específico para una zona.

    Args:
        perfil_zona: Clave del perfil ('agua_intermitente', 'alta_densidad', etc.)

    Returns:
        Diccionario con indicadores combinados (base + específicos de zona)
    """
    if perfil_zona not in PERFILES_CRITICOS:
        raise ValueError(f"Perfil de zona no encontrado: {perfil_zona}")

    # Combinar indicadores base con los específicos de la zona
    indicadores = ESCENARIO_TODOS_CRITICOS_BASE.copy()
    indicadores.update(PERFILES_CRITICOS[perfil_zona].get("indicadores_especificos", {}))

    return {
        "indicadores": indicadores,
        "factores_estrategia": PERFILES_CRITICOS[perfil_zona]["factores_estrategia"],
        "estrategias_prioritarias": PERFILES_CRITICOS[perfil_zona]["estrategias_prioritarias"],
        "nombre": PERFILES_CRITICOS[perfil_zona]["nombre"],
        "descripcion": PERFILES_CRITICOS[perfil_zona]["descripcion"],
        "color": PERFILES_CRITICOS[perfil_zona]["color"],
    }


def obtener_escenario_verde_por_zona(perfil_zona):
    """
    Obtiene el escenario verde específico para una zona.

    Args:
        perfil_zona: Clave del perfil ('historicamente_problematica', 'bien_organizada', etc.)

    Returns:
        Diccionario con indicadores combinados (base + específicos de zona)
    """
    if perfil_zona not in PERFILES_VERDES:
        raise ValueError(f"Perfil de zona no encontrado: {perfil_zona}")

    # Combinar indicadores base con los específicos de la zona
    indicadores = ESCENARIO_TODOS_VERDES_BASE.copy()
    indicadores.update(PERFILES_VERDES[perfil_zona].get("indicadores_especificos", {}))

    return {
        "indicadores": indicadores,
        "factores_estrategia": PERFILES_VERDES[perfil_zona]["factores_estrategia"],
        "estrategias_prioritarias": PERFILES_VERDES[perfil_zona]["estrategias_prioritarias"],
        "nombre": PERFILES_VERDES[perfil_zona]["nombre"],
        "descripcion": PERFILES_VERDES[perfil_zona]["descripcion"],
        "color": PERFILES_VERDES[perfil_zona]["color"],
    }


def obtener_perfil_por_comuna(comuna, escenario_tipo="critico"):
    """
    Determina el perfil de zona apropiado para una comuna.

    Args:
        comuna: Código de la comuna (ej: "13", "02")
        escenario_tipo: "critico" o "verde"

    Returns:
        Clave del perfil de zona correspondiente
    """
    perfiles = PERFILES_CRITICOS if escenario_tipo == "critico" else PERFILES_VERDES

    for perfil_key, perfil_data in perfiles.items():
        if comuna in perfil_data.get("comunas", []):
            return perfil_key

    # Perfil por defecto si no se encuentra la comuna
    if escenario_tipo == "critico":
        return "alta_densidad"  # Perfil crítico por defecto
    else:
        return "cobertura_agua_variable"  # Perfil verde por defecto