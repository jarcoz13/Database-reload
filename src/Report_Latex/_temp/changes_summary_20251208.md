# Resumen de modificaciones del Reporte - 2025-12-08

## Cambios aplicados

### Archivo: Capítulo - Abstract
- **Actualizado** el `Abstract` para alinear el contenido con el baseline del Delivery 3.
  - Se centró el diseño en **PostgreSQL** con particionamiento temporal y vistas materializadas.
  - Se describió la ingesta como **periódica** (batch) en lugar de "real-time" estricto.
  - Se especificó que el motor de recomendaciones es **rule-based** y que NoSQL se usa para preferencias/configuración.
  - Tecnologías avanzadas (TimescaleDB, MinIO, BI externo) ahora se mencionan como **future work**, no como parte del MVP.

## Archivos modificados
- `chapters/00_i_abstract.tex`
### Archivo: Capítulo 1 - Introduction
- **Actualizado** `chapters/01_introduction.tex` para alinear el capítulo con el alcance realista del Delivery 3.
  - Se cambió lenguaje de "real-time" a "near real-time / periodic" y se evitó presentar TimescaleDB/MinIO/GraphQL como componentes obligatorios.
  - Objetivos reescritos para mostrar PostgreSQL como núcleo, particionamiento temporal, ingesta periódica (ej. 10 min) y API REST como principal opción.
  - Recomendaciones descritas como rule-based y las capacidades avanzadas (product suggestions, navigation guidance) movidas a future work.
  - El apartado de contribuciones ajustado para no declarar métricas de rendimiento como logros ya alcanzados; se añadió el plan de validación.

## Archivos modificados
 - `chapters/01_introduction.tex`
### Archivo: Capítulo 2 - Literature Review
- **Actualizado** `chapters/02_literature.tex` para dejar claro que TimescaleDB, MinIO y frameworks de streaming son tecnologías analizadas y no componentes obligatorios del baseline.
  - Se añadió una frase introductoria en la subsección de TimescaleDB indicando que es una opción considerada, no un requisito del prototipo.
  - Se modificó el resumen para describir a PostgreSQL como baseline y TimescaleDB como posible extensión.
  - Se agregó un párrafo final que conecta la revisión de la literatura con las decisiones de diseño empleadas en el Cap.3 (particionamiento temporal, materialized views, NoSQL para preferencias, ingestión periódica, recomendaciones rule-based).
  - `chapters/02_literature.tex`

## Archivos creados
- `src/Report_Latex/_temp/changes_summary_20251208.md` (este archivo)

## Tareas pendientes
- Revisar y actualizar el **Capítulo 1 (Introduction)** para asegurar que los objetivos, el alcance y el resumen de contribuciones estén alineados con el Delivery 3.
- Aplicar cambios similares en las secciones de Methodology (Cap.3) donde se referencian TimescaleDB/MinIO/MongoDB como parte del núcleo del sistema.

## Notas
- El contenido del `Abstract` se mantiene en inglés, siguiendo las instrucciones del repositorio para los documentos LaTeX.
- Resumen generado por Copilot en formato requerido (español) y guardado en `_temp/`.

---

Si quieres, procedo a actualizar el capítulo 1 (`chapters/01_introduction.tex`) ahora o preparo un diff con las líneas sugeridas para que lo revises antes de aplicar cambios.
