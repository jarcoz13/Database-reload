# Presentation Slides - Air Quality Monitoring Project

Presentación en formato Beamer de la arquitectura para monitoreo de calidad del aire en Bogotá.

## Contenido

La presentación está organizada en las siguientes secciones:

1. **Portada** - Título, autores e institución
2. **Agenda** - Tabla de contenidos
3. **Problem Statement** - Motivación y desafíos
4. **Objectives** - Objetivos primarios y secundarios
5. **Proposed Solution** - Arquitectura general del sistema
6. **Ingestion Layer** - Capa de ingesta de datos (APScheduler)
7. **Persistence Layer** - Base de datos PostgreSQL con esquema 3NF
8. **Application Layer** - API FastAPI con caché Redis
9. **Presentation Layer** - Dashboard interactivo
10. **Database Schema** - Diseño de tablas normalizadas
11. **Query Optimization** - Estrategias de optimización
12. **Results & Validation** - Resultados de performance
13. **Optimization Impact** - Antes y después de optimizaciones
14. **Concurrency Validation** - 4 escenarios de concurrencia
15. **Scalability Projections** - Proyecciones de escalabilidad
16. **Key Achievements** - Logros principales
17. **Future Work** - Trabajo futuro
18. **Broader Impact** - Impacto social y científico
19. **Thank You** - Diapositiva final

## Estructura de Archivos

```
Presentation_Slides/
├── Presentation.tex        # Archivo principal LaTeX (Beamer)
├── Compilar.sh             # Script de compilación
├── README.md               # Este archivo
└── images/
    ├── fig1_architecture.png          # Diagrama de arquitectura
    ├── logo_escudo_vertical.png       # Logo universidad
    └── identidad_facultad-02.png      # Identidad visual
```

## Compilación

Para compilar la presentación:

```bash
cd /home/jarcoz/Documentos/Universidad/Sistemas/Bd2/Database-reload/src/Presentation_Slides
bash Compilar.sh
```

El PDF generado se guardará en: `../../Catch-Up/Presentation.pdf`

## Características

- **Tema**: Madrid (profesional y limpio)
- **Aspecto**: 16:9 (pantalla ancha)
- **Idioma**: Español
- **Fuentes**: LaTeX estándar con soporte Unicode
- **Imágenes**: Diagramas de arquitectura y logos universitarios
- **Tablas**: Formatos profesionales con booktabs

## Visualización

Para ver la presentación después de compilar:

```bash
okular ../../Catch-Up/Presentation.pdf
```

O cualquier otro lector PDF como:
- `evince`
- `atril`
- `xpdf`

## Personalización

Para editar la presentación:

1. Modifica el contenido de las diapositivas en `Presentation.tex`
2. Cambia el tema usando `\usetheme{NombreTema}` (opciones: Madrid, Berlin, Singapore, etc.)
3. Personaliza colores con `\usecolortheme{NombreColor}`
4. Recompila con `bash Compilar.sh`

## Autores

- Jose Alejandro Cortazar López
- Johan Esteban Castaño Martínez
- Stivel Pinilla Puerta

**Institución**: Programa de Ingeniería de Sistemas - Universidad Distrital Francisco José de Caldas

**Fecha**: Diciembre 2025

## Notas Técnicas

- Compilador: pdflatex
- Paquetes principales: beamer, graphicx, booktabs, tikz
- Encoding: UTF-8
- Las imágenes deben estar en la carpeta `images/` para que se carguen correctamente
