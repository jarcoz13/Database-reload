Perfecto, vamos por partes 💪

Voy a asumir que el **“Report.pdf”** es tu **reporte técnico** y que lo queremos alinear con:

* Lo que pide el profe para el **reporte** (más profundidad en: diseño de BD, normalización, índices, optimización de consultas, resultados/experimentos).
* El **Delivery_Workshop_3** (última versión del proyecto).
* Los requerimientos globales de los Workshops (ingesta continua, queries rápidos, módulo BI, recomendaciones, etc.).

Abajo te dejo un **checklist sección por sección**, con lo que *falta corregir* o ajustar. No voy a reescribir todavía el texto, solo marcar tareas.

---

## 0. Problemas globales (que se repiten en varias secciones)

Antes de entrar sección por sección, hay **cuatro desajustes grandes** que debes corregir en todo el documento:

1. **Arquitectura actual vs arquitectura “soñada”**

   * En el Report todavía se habla como si la arquitectura actual fuera:

     * PostgreSQL + **TimescaleDB** (hypertables, continuous aggregates, métricas específicas de Timescale)
     * **MinIO** para raw JSON
     * **MongoDB** como store semi–estructurado
     * **Real-time dashboards** y “sub-2-second p95 latency under production workloads”
   * En el Delivery_Workshop_3, lo que se presenta como **baseline realista del curso** es:

     * Una arquitectura centrada en **un PostgreSQL** (con posible particionamiento y materialized views).
     * **NoSQL ligero** solo para user_preferences y dashboard_configs
     * Ingesta **periódica** (cada pocos minutos u hora), no “estrictamente en tiempo real”
       👉 **Tarea global**:
   * Donde el Report hable de la arquitectura “final” como *Timescale + MinIO + Mongo + real-time + 1000 usuarios concurrentes*, hay que rebajar a:

     * **“Single PostgreSQL instance + optional partitioning + lightweight NoSQL for preferences/dashboards”**.
     * Timescale, MinIO, Mongo, Grafana, etc. deben quedar descritos como **posibles mejoras o trabajo futuro**, no como parte del prototipo actual.

2. **Real-time vs ingesta periódica**

   * El Report usa mucho “real-time dashboards”, “high-frequency ingestion every 10 minutes”, etc.
   * Delivery_Workshop_3 dejó explícito que **reemplazaron el real-time estricto por ingesta periódica** (cada pocos minutos / cada hora) y que eso es lo que se va a implementar de verdad.
     👉 **Tarea global**:
   * Cambiar todo lo que suene a SLA de *tiempo real* por algo como *“near real-time / periodic ingestion aligned with external API update frequency”*.
   * Mantener el intervalo de 10 minutos como un ejemplo concreto de esa ingesta periódica, si lo quieres conservar, pero sin venderlo como “real-time”.

3. **Requerimientos y alcance ajustados (FR / NFR)**

   * En Delivery_Workshop_3 corrigieron:

     * Recomendaciones: **simples y basadas en reglas**, no ML.
     * **Product suggestions**: solo recomendaciones informativas, **no e-commerce**.
     * Mapas y navegación avanzada → **future work**.
     * Interfaz **solo web responsive**, no apps nativas.
       👉 **Tarea global**:
   * Revisar donde el Report hable de:

     * “recommendation engine”, “product recommendations”, “cleaner-area navigation guidance”, “mobile app”, etc.
   * Asegurarte que:

     * Recomendaciones = **rule-based** sobre AQI.
     * “Product recommendations” = **texto informativo**, sin compra.
     * Navegación y mapas complejos = explícitamente “Future Work”.
     * Solo **responsive web app**, no mobile nativo.

4. **Profundidad analítica en BD, índices y resultados**

   * El Report ya tiene secciones fuertes de:

     * Diseño lógico/físico
     * Normalización (menciona 3NF)
     * Indexing & query optimization
     * Concurrency analysis
   * Peeero:

     * Varias de estas partes están escritas **como si ya hubieras corrido experimentos con TimescaleDB**, usando frases tipo “This methodology ensured that every index or optimization produced measurable improvements...” sin tablas ni números.
       👉 **Tarea global**:
   * O bien:

     * Añadir **datos concretos** (tablas con tiempos de ejecución antes/después, tamaño de índices, etc.) para 2–3 queries clave (por ejemplo las de Delivery_Workshop_3, Codes 1–5).
   * O, si no vas a medir nada:

     * Reescribir esas frases en **modo “diseño propuesto / expected behavior”**, no como resultados empíricos.

---

## 1. Front matter (Abstract, Acknowledgements, TOC)

### Abstract

* **Problema**:

  * Habla de MinIO, TimescaleDB, MongoDB y GraphQL como parte del diseño final, y de “cloud-ready, real-time dashboards, 1000 concurrent users, p95 < 2s”.
* **Tareas**:

  1. Mantener el “story” general del proyecto, pero actualizarlo a:

     * Arquitectura centrada en **PostgreSQL + lightweight NoSQL store** (preferences/dashboards).
     * Ingesta **periódica** y dashboards **near real-time**.
     * Métricas de rendimiento alineadas con NFR realistas (latencias típicas de las consultas del Delivery 3, no promesas duras de p95 < 2s).
  2. Asegurar que menciona explícitamente los **tres ejes de los requerimientos del curso**:

     * Fast queries in big-data-ish context.
     * Constant data ingestion.
     * Business intelligence / analytical views.

### Acknowledgements

* **Actual**: agradece a la comunidad de PostgreSQL, Timescale, MinIO, APIs de calidad del aire y herramientas de IA.
* **Problema** (menor, pero tú ya lo mencionaste):

  * Menciona explícitamente TimescaleDB y MinIO como si fueran parte central del proyecto terminado.
* **Tareas**:

  * Opción simple: generalizar a algo tipo:

    * “open-source database and time-series communities”, “cloud-native storage projects”, etc. (sin nombrar específicos que ya no usas).
  * O dejar Timescale/MinIO pero aclarando en otra parte del reporte que su uso es **explorado conceptualmente / para futuro**.

### Table of Contents

* **Problema**:

  * Incluye secciones **ejemplo** (3.5.x, 3.6, 3.7) de la guía de documentación, que no son parte del proyecto.
* **Tareas**:

  * Eliminar del reporte (o mover a un apéndice opcional) todo lo que sean **“Example of a Table/Figure/Equation”** de la guía (3.5, 3.6, 3.7 y subsecciones). No aportan nada al profe y hacen ruido.

---

## 2. Capítulo 1 – Introduction

### 1.1 Background y 1.2 Problem Statement

* **Estado**:

  * Están bien: plantean el contexto de calidad del aire, usuarios, y el problema que se resuelve.
* **Tareas**:

  * Solo asegurarte de que referencian **explícitamente** los requerimientos clave del curso (ingesta continua, fast queries, BI, multi-location, recomendaciones, alta disponibilidad y escalabilidad) aunque sea de forma resumida.

### 1.3 Aims and Objectives

* **Problema**:

  * Algunos objetivos hablan como si **Timescale + MinIO + Mongo + GraphQL** fueran el stack actual y como si el sistema garantizara real-time y alta concurrencia.
* **Tareas**:

  * Reescribir los objetivos para que:

    * Apunten al **stack del Delivery 3**: PostgreSQL (con particionamiento y vistas materializadas), NoSQL ligero para preferencias, API REST, web app responsive.
    * Haya al menos un objetivo explícito por cada tema que el profe pidió profundizar:

      * Diseño y normalización de la BD.
      * Estrategia de índices y optimización de consultas.
      * Manejo de concurrencia y rendimiento de ingestión.
      * (Opcional) diseño de NoSQL para preferencias/dashboards.

### 1.4 Solution Approach

* **Problema**:

  * Aquí todavía describes una solución “full”: MinIO + Timescale + Mongo + GraphQL + real-time dashboards + “cleaner-area navigation guidance”.
* **Tareas**:

  * Dividir mentalmente en dos niveles:

    1. **Baseline (lo que realmente cubre el proyecto del curso)**:

       * Python ingestion job + normalizer → PostgreSQL (AirQualityReading, AirQualityDailyStats, Alerts, Recommendations, etc.).
       * NoSQL store para user_preferences/dashboard_configs.
       * Web app responsive consumiendo API REST.
    2. **Future work / possible extensions**:

       * MinIO para raw payloads, uso de TimescaleDB, GraphQL, BI externo, mapas avanzados, multi-region, etc.
  * En el texto actual, marca explícitamente qué pertenece a (1) y qué es (2).

### 1.5 Summary of Contributions and Achievements

* **Problema**:

  * Afirma logros como si ya tuvieras:

    * p95 < 2s bajo alta concurrencia.
    * Real-time dashboards sobre TimescaleDB, MinIO, Mongo.
  * Esto no está respaldado con resultados en el Cap. 4.
* **Tareas**:

  * Cambiar el tono a:

    * Lo que **sí está respaldado** por el Delivery 3: modelo relacional bien normalizado, consultas clave bien definidas (Codes 1–5), diseño de índices y particionamiento razonado, añadidura de NoSQL para preferencias, etc.
    * Si quieres mencionar rendimiento, hacerlo como **“target performance goals”**, no como “achieved”.

### 1.6 Organization of the Report

* **Tareas**:

  * Asegurarte que la descripción de cada capítulo esté alineada con lo que realmente tienes ahora:

    * Cap. 3 = metodología (diseño, ingestión, normalización, índices, concurrencia, etc.).
    * Cap. 4 = resultados (aunque sean analíticos / esperados).
    * Cap. 5/6/7 = discusión, conclusiones, future work / reflection (según lo que ya tengas; aquí puedes empujar Timescale, MinIO, mapas, ML, etc. como futuros).

---

## 3. Capítulo 2 – Literature Review

En general, este capítulo está bien y le da el “marco académico” que el profe valora.

* **Puntos a revisar**:

  1. En las secciones donde referencias TimescaleDB, NoSQL, stream processing, etc., deja claro que:

     * Son **tecnologías analizadas**;
     * El proyecto actual implementa solo una parte (PostgreSQL + NoSQL ligero);
     * El resto queda como **candidatas para escalamiento futuro**.
  2. Agregar un mini **“summary paragraph”** que conecte la revisión de literatura con tus decisiones de diseño del Cap. 3 (ej.: por qué se eligió particionamiento temporal, por qué se separa NoSQL para preferencias, etc.).

---

## 4. Capítulo 3 – Methodology

Este es el corazón de lo que el profe criticó. Ya tienes buena base, pero hay que alinear y reforzar.

### 3.1 Objectives, 3.2 Scope, 3.3 Assumptions, 3.4 Limitations

* **Tareas**:

  * Alinear objetivos, alcance y supuestos con lo que está en **“Improvements to Workshop 2”** del Delivery 3:

    * Ingstión periódica, no streaming continuo.
    * Recomendaciones simples, sin ML.
    * Web responsive (no apps nativas).
    * Mapas avanzados y multi-region → future work.
  * En Limitations, mencionar explícitamente:

    * Que no se implementan aún sistemas distribuidos, ni multi-region real, ni ML, ni BI externo (solo se dejan como líneas de trabajo).

### 3.4.1 Database Design Methodology

* **Estado**:

  * Ya explicas: entidades principales, tablas de referencia normalizadas a 3NF, modelado centrado en el usuario, y separación de raw data en MinIO + MongoDB.
* **Problema**:

  * La parte de **MinIO y Mongo** ya no encaja con la arquitectura mínima del curso.
* **Tareas**:

  1. Mantener:

     * La explicación de **3NF** y cómo pasaste del modelo conceptual al lógico (esta es la parte que el profe pedía ver).
     * La descripción de entidades clave que coinciden con el ER / esquema del Delivery 3 (Station, Pollutant, AirQualityReading, AirQualityDailyStats, AppUser, Alert, Recommendation, etc.).
  2. Ajustar:

     * Quitar de aquí la idea de que **MinIO + Mongo son parte del núcleo actual**; en su lugar:

       * Mencionar **NoSQL store** solo para user_preferences y dashboard_configs, alineado con Code 6 y 7 del Delivery 3.
     * Si quieres hablar de MinIO/Mongo, muévelos a **Future Work** o a una subsección explícita de “Alternative Storage Options”.

### 3.4.2 Data Ingestion

* **Estado**:

  * Muy detallada, pero ligada a: MinIO, colas futuras y retención de 7 días en raw JSON.
* **Tareas**:

  * Alinear con lo que describe Delivery 3 en “Optimized Batch Ingestion and Daily Aggregation”:

    * Enfatizar:

      * Python ingestion job → normalizer → PostgreSQL.
      * Batching/bulk inserts.
      * Ventanas de ingestión alineadas con particiones temporales.
    * Dejar claro que lo de MinIO/raw JSON es **opcional / futuro**, no parte del MVP del curso.

### 3.4.3 Normalization and Storage

* **Estado**:

  * Describe muy bien el proceso de mapeo de campos, unidades, AQI y la inserción en un **hypertable Timescale** con compresión y constraint de unicidad.
* **Problema**:

  * Otra vez, asume TimescaleDB como realidad actual.
* **Tareas**:

  1. Replantear la narrativa a:

     * “Normalized relational schema on PostgreSQL”, con:

       * Tablas AirQualityReading y AirQualityDailyStats (como en Delivery 3).
       * Constraint de unicidad (station_id, pollutant_id, datetime) → esto sí es muy bueno, mantenlo.
  2. Explicar brevemente el camino de normalización:

     * 1NF → 2NF → 3NF (por ejemplo: cómo se separaron Station, Pollutant, Provider, User, etc.). Esto responde exactamente al comentario del profe.

### 3.4.4 Indexing and Query Optimization

* **Estado**:

  * Está muy bien en cuanto a **diseño de índices**:

    * idx_reading_station_time, idx_reading_city_pollutant_time, idx_reading_pollutant_station_time, partial index de últimos 30 días, BRIN para histórico.
    * Explica técnicas de query rewriting y caching.
* **Problema**:

  * Está muy metida la idea de “hypertable partitioning (TimescaleDB)” y “TimescaleDB execution metrics”.
* **Tareas**:

  1. Mantener:

     * Índices y racionales, pero explicarlos como **diseño para PostgreSQL estándar**, usando particionamiento declarativo (como en Delivery 3, sección de Performance Improvement Strategies).
  2. Cambiar:

     * “Hypertable partitioning (TimescaleDB)” → “Temporal (and future geographic) partitioning in PostgreSQL”.
     * “TimescaleDB execution metrics” → “PostgreSQL execution metrics (EXPLAIN/EXPLAIN ANALYZE)”.
  3. Conectar explícitamente estos índices con las **consultas del Delivery 3 (Codes 1–5)**:

     * por ejemplo, para Code 1 (latest readings per city), dejar claro qué índice lo soporta.

### 3.4.5 Concurrency Analysis

* **Estado**:

  * Muy completo: analiza escenarios de ingestión vs queries, mantenimiento concurrente, bloqueos, MVCC, niveles de aislamiento, etc.
* **Tareas**:

  * Solo suavizar frases que hagan parecer que *ya hay millones de filas y alto tráfico*; dejarlo como **análisis metodológico**.
  * Puedes hacer una referencia cruzada a las estrategias de particionamiento, réplicas de lectura y caching del Delivery 3.

### 3.4.6 API Layer and Services / 3.4.7 Recommendation Engine

* **Tareas**:

  * Asegurarte que:

    * La API principal es **REST** (GraphQL va como future work si lo mencionas).
    * El recommendation engine está descrito como **rule-based**, no ML, y sus consultas alineadas con la tabla Recommendation / ProductRecommendation del Delivery 3.
    * Las recomendaciones de productos se describen como **informational protective measures**, no e-commerce.

### 3.4.8 Performance Validation and Experiments

* **Problema**:

  * Habla como si ya se hubiera hecho experimentación exhaustiva (JMeter, Prometheus, comparación antes/después) pero en el Cap. 4 no hay números concretos.
* **Tareas**:

  * Decide una de dos:

    1. **Sí medir algo**:

       * Ejecutar al menos 2–3 queries clave con un dataset sintético (volúmenes del Delivery 3) y poner una tablita con tiempos, tamaño de índices, etc.
    2. **No medir nada (opción más rápida)**:

       * Reescribir esta subsección en tono de **“planned evaluation methodology”**, dejando claro que por limitaciones de tiempo solo se hizo análisis teórico y estimaciones.

### 3.5–3.7 – Secciones de “Example …” (Tablas, Figuras, Ecuaciones, Código)

* **Tarea** clara:

  * **Eliminar o mover a apéndices**. Son ejemplos de la guía, no del proyecto, y le restan seriedad al reporte.

---

## 5. Capítulo 4 – Results (o Experiments and Results)

No vimos todas las páginas, pero sí lo suficiente para notar que:

* Hay tablas y texto que describen **targets** más que resultados medidos.
* No se ven **números concretos** de ejecución por consulta, ni comparaciones con/sin índice, etc.

**Tareas**:

1. Asegurar que el capítulo 4 responde a lo que pidió el profe:

   * **“Expand on database design decisions, normalization process, indexing strategies, query optimization, and any experimental results obtained.”**
   * Mucho de esto ya está en Cap. 3, así que aquí puedes:

     * Resumir las decisiones clave (diseño, normalización, índices).
     * Presentar 2–4 **casos de uso de consulta** (por ejemplo Codes 1–5 del Delivery 3) y explicar, aunque sea cualitativamente, cómo los índices/particiones las hacen eficientes.

2. Si tienes tiempo de probar, poner:

   * Aunque sea una tabla simple tipo:

     * Query id
     * Filas en tablas (estimadas según Delivery 3)
     * Índices usados
     * Tiempo de ejecución promedio

3. Ser honesto:

   * Si los resultados son solo analíticos/estimados, dilo explícitamente.

---

## 6. Capítulo 5/6/7 – Discussion, Conclusions, Future Work / Reflection

Depende de cómo estructuraste estos capítulos, pero en general:

* **Tareas**:

  1. En conclusiones:

     * Destacar que lograste:

       * Modelo normalizado alineado con requerimientos de ingesta, consultas rápidas y BI.
       * Diseño de índices y estrategias de particionamiento/caching coherentes con las consultas definidas.
       * Un diseño NoSQL razonable para preferencias/configuración.
  2. En future work:

     * Ahí sí va TODO lo “grande”:

       * TimescaleDB y otras extensiones.
       * MinIO/Mongo como data lake.
       * Streaming real (Kafka/Flink/Spark).
       * Mapas avanzados, navegación geográfica, multi-region, ML, BI externo, etc.

---

## 7. Resumen rápido de tareas (para que te organizes)

Te dejo una mini lista ejecutable:

1. **Limpiar front matter**

   * Actualizar Abstract al baseline del Delivery 3.
   * Ajustar Acknowledgements (remover énfasis en Timescale/MinIO como core).
   * Quitar secciones de ejemplo (3.5, 3.6, 3.7).

2. **Cap. 1**

   * Alinear objetivos y alcance con ingesta periódica, web responsive, recomendaciones rule-based, sin e-commerce ni mobile app.
   * Reescribir Summary of Contributions para no prometer resultados que no están medidos.

3. **Cap. 2**

   * Mantener revisión de literatura, pero aclarando qué tecnologías son **analizadas** vs **implementadas**.

4. **Cap. 3**

   * 3.4.1–3.4.3:

     * Quitar MinIO/Mongo/Timescale como núcleo actual; usar PostgreSQL + NoSQL ligero, y particionamiento nativo.
     * Explicar de forma clara el proceso de normalización (1NF → 3NF) sobre tus tablas reales.
   * 3.4.4:

     * Mantener índices pero “des-timescalear” el texto (hablar de PostgreSQL + particiones).
     * Conectar índices con las consultas del Delivery 3.
   * 3.4.5–3.4.7:

     * Ajustar para API REST, recomendaciones rule-based y NoSQL de preferencias.
   * 3.4.8:

     * O añades aunque sea resultados simples, o lo dejas como metodología planificada (sin fingir experimentos).

5. **Cap. 4**

   * Convertirlo en un capítulo de resultados más claro:

     * o con números sencillos,
     * o con análisis bien estructurado de cómo el diseño propuesto cumple con FR/NFR (ingesta, consultas, BI, etc.).

6. **Cap. 5–7**

   * Reforzar conclusiones centradas en diseño de BD, normalización, índices y cumplimiento de requerimientos.
   * Mover todo lo “muy avanzado” (Timescale, MinIO, multi-region, ML, BI externo) a Future Work.
