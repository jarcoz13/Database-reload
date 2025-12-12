# Resumen de modificaciones del Reporte - 2025-12-09

## Cambios aplicados

### Capítulo 3: Methodology
- Reemplazado el capítulo por una versión larga, alineada con el Delivery 3.
- **Enfoque**: PostgreSQL como núcleo, ingesta periódica (ej. 10 min), normalización 1NF→3NF, índices (B-tree compuestos, parciales y BRIN), particionamiento temporal, vistas materializadas opcionales.
- **API**: REST como interfaz principal (GraphQL movido a trabajo futuro).
- **Recomendaciones**: motor rule-based; ML declarado como futuro.
- **Rendimiento**: validación planificada (EXPLAIN/ANALYZE, JMeter) sin afirmar métricas empíricas.
- **Futuro**: TimescaleDB, MinIO y pipelines NoSQL completos descritos como mejoras, no parte del baseline.

## Archivos modificados
- `src/Report_Latex/chapters/03_methodology.tex`

## Archivos creados
- `src/Report_Latex/_temp/changes_summary_20251209.md`

## Tareas pendientes
- Validar consistencia cruzada con `Chapter 1` y `Chapter 2` (labels y narrativa alineada a Delivery 3).
- (Opcional) Añadir figuras/tablas específicas si se definen métricas o esquemas finales.

## Referencias cruzadas verificadas
- No se ejecutó compilación ni validación de referencias por solicitud del usuario.
