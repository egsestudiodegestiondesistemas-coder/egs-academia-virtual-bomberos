# EGS Simulation Core

## Principio
Teoría -> observación -> decisión -> consecuencia -> análisis -> fuente.

## Archivos
- catalog.json: familias y escenarios.
- schemas/state.schema.json: estado de simulación.
- schemas/rule.schema.json: regla doctrinaria.
- scenarios/structural_house_master.json: primer escenario maestro.
- rules/: reglas validadas.

## Regla doctrinaria
No se incorporan consecuencias tácticas definitivas sin una fuente identificable y validada.

## Arquitectura
El motor gráfico (web, Unreal u otro) consume estos estados y reglas.
Así podemos cambiar de tecnología visual sin perder conocimiento, trazabilidad ni diseño pedagógico.
