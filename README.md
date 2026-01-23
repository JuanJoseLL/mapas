# Sistema de Soporte a Decisiones - Control de Dengue

Sistema prescriptivo basado en MCDA (Multi-Criteria Decision Analysis) para recomendar estrategias de control de dengue según escenarios epidemiológicos.

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENTRADA DE DATOS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. indicator_values: Dict[str, float]                                       │
│     - 52 indicadores epidemiológicos, entomológicos, operativos, etc.       │
│     - Ejemplo: {"Índice de Breteau (IB)": 35.0, "Tasa de incidencia": 45.0} │
│                                                                              │
│  2. strategy_factors: Dict[str, Dict[str, float]]                           │
│     - 11 factores de aplicabilidad por estrategia (escala 0-10)             │
│     - Ejemplo: {"Estrategia X": {"disponibilidad_recursos": 7, ...}}        │
│                                                                              │
│  3. strategies_config: (desde Excel)                                         │
│     - 19 estrategias con sus indicadores asociados y pesos                  │
│     - Umbrales de activación por indicador                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODELO MCDA (scikit-criteria)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Evaluar cumplimiento de indicadores vs umbrales                         │
│  2. Calcular score de factores: Σ(factor_estrategia × factor_contexto)      │
│  3. Aplicar multiplicadores de urgencia según nivel de riesgo               │
│  4. Weighted Sum Model: 50% indicadores + 50% factores                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SALIDA                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ranking: List[Tuple[estrategia, rank, score, cumplimiento]]                │
│                                                                              │
│  Ejemplo:                                                                    │
│  [                                                                           │
│    ("Aplicar adulticidas químicos...", 1, 0.8234, 0.756),                   │
│    ("Implementar protocolos de triage...", 2, 0.7891, 0.712),               │
│    ("Aplicar larvicidas químicos...", 3, 0.7456, 0.698),                    │
│    ...                                                                       │
│  ]                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Scripts Principales

### 1. `scikit-criteria-demo.py` - Motor MCDA Principal

**Propósito**: Implementa el modelo de decisión multicriterio usando scikit-criteria.

**Entrada**:
```python
# indicator_values: Dict[str, float]
# Diccionario con 52 indicadores y sus valores actuales
indicator_values = {
    "Número de casos por semana epidemiológica": 8.0,
    "Tasa de incidencia semanal": 45.0,
    "Porcentaje de hospitalización por dengue": 15.0,
    "Índice de Breteau (IB)": 35.0,
    "Índice de vivienda (IV)": 18.0,
    "Disponibilidad de insumos": 72.0,
    # ... 46 indicadores más
}

# strategy_factors: Dict[str, Dict[str, float]]
# 11 factores de aplicabilidad por estrategia (escala 0-10)
strategy_factors = {
    "Aplicar adulticidas químicos...": {
        "disponibilidad_recursos": 6,
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
    # ... 18 estrategias más
}
```

**Salida**:
```python
# result.alternatives: List[str] - nombres de estrategias
# result.rank_: np.array - ranking (1 = mejor)
# result.e_.score: np.array - scores normalizados

# Ejemplo de uso:
ranking = sorted(
    zip(result.alternatives, result.rank_, result.e_.score),
    key=lambda x: x[1]
)
# [("Estrategia A", 1, 0.8234), ("Estrategia B", 2, 0.7891), ...]
```

**Funciones clave**:
- `load_strategies_from_xlsx()`: Carga configuración desde Excel
- `build_indicator_matrix()`: Construye matriz de cumplimiento
- `build_mcda_matrix()`: Combina indicadores y factores
- `aplicar_multiplicador_urgencia()`: Ajusta scores según nivel de riesgo

---

### 2. `escenarios_prescriptivos.py` - Definición de Escenarios

**Propósito**: Define 4 escenarios de riesgo con valores de indicadores predefinidos.

**Estructura de un escenario**:
```python
ESCENARIOS = {
    "bajo_riesgo": {
        "nombre": "Bajo Riesgo - Vigilancia Rutinaria",
        "descripcion": "Situación epidemiológica controlada...",
        "color": "🟢",
        "nivel_alerta": 1,  # 1-4

        # 52 indicadores con valores para este escenario
        "indicadores": {
            "Número de casos por semana epidemiológica": 1.0,
            "Tasa de incidencia semanal": 8.0,
            "Índice de Breteau (IB)": 8.0,
            # ...
        },

        # 11 factores de aplicabilidad
        "factores_estrategia": {
            "disponibilidad_recursos": 8,
            "costo_operativo": 3,
            # ...
        },

        "estrategias_esperadas": [
            "Promover prácticas preventivas sostenibles",
            "Fortalecer la percepción de riesgo",
        ],
    },
    "riesgo_moderado": { ... },
    "alto_riesgo": { ... },
    "emergencia": { ... },
}
```

**Función principal**:
```python
def ejecutar_escenario(
    escenario_id: str,           # "bajo_riesgo", "alto_riesgo", etc.
    mcda_module,                  # Módulo MCDA cargado
    xlsx_path: str,               # Ruta al Excel de configuración
    escenarios_def: dict = None,  # Definición de escenarios (default: ESCENARIOS)
    contexto_escenario: str = None  # Contexto adicional para multiplicadores
) -> dict:
    """
    Retorna:
    {
        "escenario": {...},              # Definición del escenario
        "ranking": [(est, rank, score, compliance), ...],  # Top estrategias
        "mcda_matrix": np.array,         # Matriz de decisión
        "criteria_names": ["cumplimiento_indicadores", "score_factores"],
        "indicator_thresholds": {...},   # Umbrales por indicador
        "indicator_values": {...},       # Valores usados
        "indicadores_criticos": int,     # Cantidad en nivel crítico
        "indicadores_normales": int,     # Cantidad en nivel normal
    }
    """
```

---

### 3. `escenaries.py` - Escenarios Detallados y Perfiles de Zona

**Propósito**: Define escenarios específicos y perfiles diferenciados por tipo de zona.

**Escenarios básicos**:
- `ESCENARIO_NORMAL`: Indicadores controlados
- `ESCENARIO_ALERTA`: Indicadores críticos
- `ESCENARIO_MIXTO`: Algunos críticos, otros normales

**Perfiles para escenarios extremos**:
```python
# Para "Todos Críticos" (emergencia en toda la ciudad)
PERFILES_CRITICOS = {
    "agua_intermitente": {
        "nombre": "Zona con Intermitencia de Agua",
        "comunas": ["14", "15", "21"],
        "indicadores_especificos": {
            "Continuidad en el servicio de acueducto": 8,
            "Tipo de depósito positivo dominante": 85,
        },
        "factores_estrategia": {...},
        "estrategias_prioritarias": [
            "Control físico en depósitos de almacenamiento",
            "Larvicidas químicos en tanques",
        ],
    },
    "alta_densidad": {...},
    "construcciones": {...},
    "dificil_acceso": {...},
    "rechazo_comunitario": {...},
}

# Para "Todos Verdes" (bajo riesgo en toda la ciudad)
PERFILES_VERDES = {
    "historicamente_problematica": {...},
    "bien_organizada": {...},
    "buena_infraestructura": {...},
    "cobertura_agua_variable": {...},
    "transicion": {...},
}
```

---

### 4. `visualizacion_escenarios_mapa.py` - Generación de Mapas

**Propósito**: Genera mapas HTML interactivos con Folium.

**Entrada**:
- Shapefile de barrios de Cali
- Resultados del modelo MCDA por escenario

**Salida**: Archivo HTML con mapa interactivo

---

### 5. `generar_mapas_variantes.py` - Generador de Escenarios Contextuales

**Propósito**: Genera múltiples mapas con diferentes contextos.

**Variantes implementadas**:
1. **Lluvias intensas**: Presión climática y entomológica
2. **Intermitencia de agua**: Criaderos intradomiciliarios
3. **Movilidad y eventos**: Presión epidemiológica
4. **Saturación operativa**: Limitaciones de respuesta

---

## Estructuras de Datos para TypeScript

### Entrada al Modelo

```typescript
// 52 indicadores con sus valores actuales
interface IndicatorValues {
  [indicatorName: string]: number;
}

// Ejemplo:
const indicatorValues: IndicatorValues = {
  "Número de casos por semana epidemiológica": 8.0,
  "Tasa de incidencia semanal": 45.0,
  "Porcentaje de hospitalización por dengue": 15.0,
  "Muertes probables": 1,
  "Letalidad": 0.06,
  "Índice de Breteau (IB)": 35.0,
  "Índice de vivienda (IV)": 18.0,
  "Índice de depósito (ID)": 12.0,
  "Índice pupal": 1.5,
  "Disponibilidad de insumos": 72.0,
  "Disponibilidad de equipos": 82.0,
  "Personal en terreno": 76.0,
  "Tiempo de respuesta de control vectorial desde la notificación": 85.0,
  // ... 39 indicadores más
};

// 11 factores de aplicabilidad por estrategia (escala 0-10)
interface StrategyFactors {
  disponibilidad_recursos: number;  // Personal, equipos, vehículos, insumos
  costo_operativo: number;          // Costo de la intervención
  tiempo_cobertura: number;         // Tiempo de alistamiento y cobertura
  dependencias_externas: number;    // Requiere otras dependencias
  aceptacion_comunidad: number;     // Aceptación de la comunidad
  acceso_predios: number;           // Posibilidad de entrar a viviendas
  percepcion_riesgo: number;        // Percepción de riesgo comunitario
  resistencia_vector: number;       // Resistencia del mosquito
  otros_vectores: number;           // Presencia de otros focos
  efectividad_esperada: number;     // Efectividad esperada
  magnitud_brote: number;           // Magnitud del brote actual
}

interface StrategyFactorsMap {
  [strategyName: string]: StrategyFactors;
}

// Configuración de umbral por indicador
interface ThresholdConfig {
  op: "<" | "<=" | ">" | ">=";
  threshold: number;
}

interface IndicatorThresholds {
  [indicatorName: string]: ThresholdConfig;
}
```

### Salida del Modelo

```typescript
interface StrategyRanking {
  strategy: string;      // Nombre completo de la estrategia
  rank: number;          // Posición en el ranking (1 = mejor)
  score: number;         // Score normalizado (0-1)
  compliance: number;    // Cumplimiento de indicadores (0-1)
}

interface MCDAResult {
  escenario: {
    nombre: string;
    descripcion: string;
    color: string;       // Emoji: "🟢", "🟡", "🟠", "🔴"
    nivel_alerta: 1 | 2 | 3 | 4;
  };
  ranking: StrategyRanking[];
  indicadores_criticos: number;   // Cantidad que cruzan umbrales
  indicadores_normales: number;   // Cantidad dentro de límites
}
```

### Las 19 Estrategias

```typescript
const STRATEGIES = [
  "Aplicar adulticidas químicos como malatión o deltametrina para el control rápido del vector adulto en espacios abiertos.",
  "Aplicar larvicidas químicos en criaderos específicos de gran volumen donde no es viable el control físico, garantizando seguridad ambiental.",
  "Aplicar métodos biológicos para el control larvario del vector, incluyendo el uso de peces larvívoros y Bacillus thuringiensis.",
  "Implementar acciones de control físico en el entorno domiciliario y comunitario para reducir o eliminar criaderos del vector.",
  "Realizar identificación focalizada de criaderos mediante inspección directa y herramientas de georreferenciación.",
  "Promover prácticas preventivas sostenibles mediante campañas educativas, cambio de comportamiento social y vigilancia participativa.",
  "Difundir mensajes preventivos inmediatos a través de canales como SMS, redes sociales y altavoces en zonas de brote.",
  "Fortalecer la percepción de riesgo del dengue y promover prácticas preventivas comunitarias mediante información, educación y comunicación.",
  "Fomentar el uso de medidas de protección individual, como repelente y barreras físicas, especialmente en grupos de riesgo.",
  "Implementar rápidamente protocolos de triage y fortalecer la capacitación del personal de salud para el manejo clínico del dengue.",
  "Articular esfuerzos con los sectores de agua, saneamiento, educación y servicios públicos para acciones preventivas sostenibles.",
  "Fortalecer la articulación institucional para asegurar la continuidad de las acciones de control y facilitar la entrada a predios.",
  "Fortalecer la sostenibilidad del programa de control del dengue mediante inversión continua, alianzas y gestión de recursos.",
  "Utilizar datos meteorológicos y modelos de alerta temprana para anticipar condiciones favorables al vector.",
  "Utilizar tecnologías innovadoras para el monitoreo y control focalizado del vector, como drones, sensores remotos o trampas inteligentes.",
  "Monitorear condiciones climáticas y gestionar escorrentías o acumulaciones de agua que favorezcan criaderos.",
  "Implementar estrategias de control vectorial basadas en biotecnología, como la liberación de mosquitos Wolbachia o técnica del insecto estéril.",
  "Implementar programas de diagnóstico oportuno, tratamiento adecuado y acompañamiento a pacientes con dengue.",
  "Fortalecer la prevención individual frente al dengue mediante el uso de vacunas aprobadas en población objetivo según lineamientos nacionales.",
];
```

### Los 52 Indicadores (agrupados por dominio)

```typescript
const INDICATORS = {
  epidemiologicos: [
    "Número de casos por semana epidemiológica",
    "Tasa de incidencia semanal",
    "Porcentaje de hospitalización por dengue",
    "Muertes probables",
    "Letalidad",
    "Casos según clasificación clínica",
    "Porcentaje de hospitalización por tipo",
    "Zona del canal endémico (situación)",
    "Razón de crecimiento epidémico frente al año anterior",
    "Variación porcentual",
    "Variación promedio vs. años anteriores",
    "Serotipos circulantes",
  ],
  entomologicos: [
    "Índice de vivienda (IV)",
    "Índice de Breteau (IB)",
    "Índice de depósito (ID)",
    "Índice Aédico en sumidero",
    "Índice pupal",
    "Número de ovitrampas positivas",
    "Tasa de reinfestación",
    "Índice de depósito en concentraciones humanas",
    "Índice de predio en concentraciones humanas",
    "Nivel de infestación crítica",
  ],
  operativos: [
    "Disponibilidad de insumos",
    "Disponibilidad de equipos",
    "Personal en terreno",
    "Disponibilidad logística semanal",
    "Cobertura territorial por brigada",
    "Tiempo de alistamiento de brigadas",
    "Disponibilidad de camas hospitalarias/UCI para dengue grave",
    "Capacidad máxima por comuna",
  ],
  cobertura: [
    "Cobertura de eliminación de criaderos o control químico en zonas de brote",
    "Inspección y control en viviendas",
    "Inspección y control de sumideros",
    "Inspección y control en lugares de concentración humana",
    "Inspección y control en cuerpos de agua (control biológico)",
    "Reducción de índice de Breteau tras control larvario",
  ],
  tiempos: [
    "Tiempo de respuesta de control vectorial desde la notificación",
    "Tiempo entre síntoma y consulta",
    "Tiempo entre consulta y notificación",
    "Tiempo de notificación y confirmación de casos",
    "Tiempo promedio de ejecución",
  ],
  ambientales: [
    "Índice de pluviosidad (días previos)",
    "Temperatura máxima (días previos)",
    "Estado de sumideros (limpios / obstruidos)",
    "Estado de canales de aguas lluvias (limpios / obstruidos)",
    "Continuidad en el servicio de acueducto",
    "Cobertura de agua potable",
  ],
  sociales: [
    "Percepción de riesgo comunitario",
    "Rechazo comunitario a intervención",
    "Cobertura de educación preventiva",
    "Prácticas preventivas",
    "Retención de aprendizaje comunitario",
    "Cobertura de hogares alcanzados con mensajes de riesgo",
  ],
  // ... más indicadores
};
```

## Algoritmo Simplificado para TypeScript

```typescript
function evaluateStrategies(
  indicatorValues: IndicatorValues,
  strategyFactors: StrategyFactorsMap,
  thresholds: IndicatorThresholds,
  strategiesConfig: StrategiesConfig,  // Del Excel
  riskLevel: "bajo_riesgo" | "riesgo_moderado" | "alto_riesgo" | "emergencia"
): StrategyRanking[] {

  const strategies = Object.keys(strategiesConfig);
  const results: { strategy: string; score: number; compliance: number }[] = [];

  for (const strategy of strategies) {
    // 1. Calcular cumplimiento de indicadores
    let compliance = 0;
    const indicators = strategiesConfig[strategy];

    for (const { indicator, weight } of indicators) {
      const value = indicatorValues[indicator];
      const threshold = thresholds[indicator];

      if (checkCondition(value, threshold.op, threshold.threshold)) {
        compliance += weight;  // Pesos ya normalizados (suman 1)
      }
    }

    // 2. Calcular score de factores
    const factors = strategyFactors[strategy];
    let factorScore = 0;

    // Factores generales (mismo valor para todas)
    factorScore += factors.percepcion_riesgo * 0.8;   // Ejemplo
    factorScore += factors.resistencia_vector * 0.5;
    factorScore += factors.magnitud_brote * 0.7;

    // Factores específicos
    factorScore += factors.disponibilidad_recursos * getContextValue("disponibilidad_recursos", strategy);
    factorScore += factors.costo_operativo * getContextValue("costo_operativo", strategy);
    // ... más factores

    // 3. Normalizar scores
    const complianceNorm = normalize(compliance);
    const factorScoreNorm = normalize(factorScore);

    // 4. Combinar (50% + 50%)
    let finalScore = 0.5 * complianceNorm + 0.5 * factorScoreNorm;

    // 5. Aplicar multiplicador de urgencia según nivel de riesgo
    const strategyType = getStrategyType(strategy);  // "inmediata", "activa", "preventiva", etc.
    finalScore *= URGENCY_MULTIPLIERS[riskLevel][strategyType];

    results.push({ strategy, score: finalScore, compliance: complianceNorm });
  }

  // Ordenar por score descendente y asignar rankings
  results.sort((a, b) => b.score - a.score);

  return results.map((r, i) => ({
    strategy: r.strategy,
    rank: i + 1,
    score: r.score,
    compliance: r.compliance,
  }));
}

// Multiplicadores de urgencia por nivel de riesgo
const URGENCY_MULTIPLIERS = {
  bajo_riesgo: {
    inmediata: 0.2,     // No desperdiciar químicos
    activa: 0.5,
    preventiva: 1.8,    // Ideal para educar
    coordinacion: 1.5,
    monitoreo: 1.7,
  },
  riesgo_moderado: {
    inmediata: 0.4,
    activa: 1.6,        // Controlar criaderos
    preventiva: 0.9,
    coordinacion: 1.2,
    monitoreo: 1.3,
  },
  alto_riesgo: {
    inmediata: 1.8,     // Adulticidas prioritarios
    activa: 1.3,
    preventiva: 0.4,
    coordinacion: 1.0,
    monitoreo: 0.6,
  },
  emergencia: {
    inmediata: 2.5,     // Máxima prioridad
    activa: 0.9,
    preventiva: 0.2,
    coordinacion: 0.7,
    monitoreo: 0.3,
  },
};
```

## Archivos de Configuración (Excel)

### `Reporte_Estrategias_Indicadores.xlsx`

| Columna | Descripción |
|---------|-------------|
| Estrategia | Nombre completo de la estrategia |
| Indicador | Nombre del indicador asociado |
| Peso (Importancia) | Peso del indicador para esta estrategia |
| Umbral Consensuado | Umbral con operador (ej: "< 70%", "> 3 casos") |
| Dominio | Categoría del indicador |

### `factores_por_estrategia.xlsx`

| Columna | Descripción |
|---------|-------------|
| Estrategia | Nombre de la estrategia |
| disponibilidad_recursos | Valor 0-10 |
| costo_operativo | Valor 0-10 |
| tiempo_cobertura | Valor 0-10 |
| ... | 11 factores en total |

## Ejecución

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar modelo MCDA básico
python scikit-criteria-demo.py

# Ejecutar todos los escenarios prescriptivos
python escenarios_prescriptivos.py

# Generar mapa interactivo base
python visualizacion_escenarios_mapa.py

# Generar mapas de variantes contextuales
python generar_mapas_variantes.py

# Generar mapas con medias de expertos
python generar_mapas_variantes.py --medias
```

## Dependencias

```
scikit-criteria>=0.8.0
numpy>=1.21.0
pandas>=1.3.0
openpyxl>=3.0.0
geopandas>=0.10.0
folium>=0.12.0
branca>=0.4.0
```
