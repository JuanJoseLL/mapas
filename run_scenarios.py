"""
Script para ejecutar los tres escenarios de dengue con el sistema MCDA.
"""
import sys
from pathlib import Path

# Importar los escenarios
from escenaries import ESCENARIO_NORMAL, ESCENARIO_ALERTA, ESCENARIO_MIXTO

# Importar el módulo principal
import importlib.util
spec = importlib.util.spec_from_file_location("scikit_criteria_demo", "scikit-criteria-demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def run_scenario(scenario_name, indicator_values, xlsx_path="Reporte_Estrategias_Indicadores.xlsx"):
    """
    Ejecuta el análisis MCDA para un escenario específico.
    """
    print("\n" + "="*100)
    print(f"EJECUTANDO ESCENARIO: {scenario_name}")
    print("="*100)

    # Ejecutar el análisis
    result = demo.main(
        xlsx_path=xlsx_path,
        indicator_values=indicator_values,
        strategy_factors=None,  # Se generarán aleatoriamente
        output_md=True
    )

    # Renombrar el archivo de reporte generado
    import glob
    import os
    from datetime import datetime

    # Buscar el reporte más reciente
    reports = glob.glob("reporte_mcda_*.md")
    if reports:
        latest_report = max(reports, key=os.path.getctime)
        new_name = f"reporte_mcda_{scenario_name}.md"
        os.rename(latest_report, new_name)
        print(f"\n✅ Reporte renombrado a: {new_name}")

    return result

if __name__ == "__main__":
    xlsx_path = sys.argv[1] if len(sys.argv) > 1 else "Reporte_Estrategias_Indicadores.xlsx"

    # Ejecutar los tres escenarios
    scenarios = [
        ("NORMAL", ESCENARIO_NORMAL),
        ("ALERTA", ESCENARIO_ALERTA),
        ("MIXTO", ESCENARIO_MIXTO),
    ]

    for scenario_name, indicator_values in scenarios:
        run_scenario(scenario_name, indicator_values, xlsx_path)

    print("\n" + "="*100)
    print("✅ TODOS LOS ESCENARIOS EJECUTADOS")
    print("="*100)
    print("\nReportes generados:")
    print("  - reporte_mcda_NORMAL.md")
    print("  - reporte_mcda_ALERTA.md")
    print("  - reporte_mcda_MIXTO.md")
