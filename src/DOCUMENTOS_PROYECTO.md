# Documentos del Proyecto - Air Quality Monitoring

Resumen de todos los documentos generados para la presentación del proyecto.

## 📄 Documentos Disponibles

### 1. **Presentation_Slides/** (Nuevas diapositivas)
- **Archivo**: `Presentation.pdf` (22 diapositivas, 690 KB)
- **Formato**: Beamer LaTeX (16:9 widescreen)
- **Ubicación**: `/src/Presentation_Slides/`
- **Contenido**: Presentación completa con 6 secciones principales
  - Problem Statement (2 diapositivas)
  - Objectives (1 diapositiva)
  - Proposed Solution (4 diapositivas + arquitectura)
  - Technical Details (2 diapositivas)
  - Results & Validation (4 diapositivas)
  - Conclusions & Impact (3 diapositivas)

### 2. **Paper_Latex/** (Artículo técnico)
- **Archivo**: `Paper.pdf` (4 páginas, 707 KB)
- **Formato**: IEEE Tran LaTeX
- **Ubicación**: `/src/Paper_Latex/`
- **Contenido**: Artículo detallado con investigación completa

### 3. **Poster_Latex/** (Póster científico)
- **Archivo**: `Poster.pdf` (1 página A0, 944 KB)
- **Formato**: Baposter LaTeX (A0 portrait)
- **Ubicación**: `/src/Poster_Latex/`
- **Contenido**: 3 columnas con 7 secciones principales
  - Abstract
  - Problem Statement
  - Key Objectives
  - Proposed Solution
  - Technical Implementation
  - Performance Results
  - Conclusions & Impact

## 📊 Comparativa de Documentos

| Documento | Formato | Páginas | Tamaño | Audiencia | Uso |
|-----------|---------|---------|--------|-----------|-----|
| Paper | PDF (IEEE) | 4 | 707 KB | Académica | Publicación, archivos |
| Poster | PDF (A0) | 1 | 944 KB | General | Conferencias, exposiciones |
| Presentation | PDF (Beamer) | 22 | 690 KB | Oral | Presentaciones, seminarios |

## 🗂️ Estructura de Carpetas

```
Database-reload/
├── Catch-Up/
│   ├── Paper.pdf                    # Artículo técnico (4 pags)
│   ├── Poster.pdf                   # Póster científico (A0)
│   └── Presentation.pdf             # Diapositivas (22 slides)
│
└── src/
    ├── Paper_Latex/
    │   ├── Compilar.sh
    │   ├── Paper.tex
    │   ├── Sections/                # Secciones externas
    │   └── images/
    │
    ├── Poster_Latex/
    │   ├── Compilar.sh
    │   ├── Poster.tex
    │   └── images/
    │
    └── Presentation_Slides/         # ← NUEVO
        ├── Compilar.sh
        ├── Presentation.tex
        ├── README.md
        └── images/
```

## 🎯 Recomendaciones de Uso

### Para Presentación Oral
→ Usar **Presentation Slides** (22 diapositivas en Beamer)
- Ideal para seminarios y defensa de proyecto
- Incluye speaker notes y esquema lógico
- Fácil de seguir y bien estructurada

### Para Conferencia/Publicación
→ Usar **Paper** (4 páginas IEEE Tran)
- Formato académico estándar
- Contiene resultados detallados y citas
- Apto para revistas y congresos

### Para Exposición Visual
→ Usar **Poster** (A0 portrait)
- Ideal para ferias, congresos, exposiciones
- Resumen visual completo en una página
- Atrae atención y permite lectura rápida

## 🔧 Comandos Útiles

### Compilar documentos
```bash
# Presentación (diapositivas)
cd src/Presentation_Slides && bash Compilar.sh

# Paper (artículo)
cd src/Paper_Latex && bash Compilar.sh

# Poster (póster científico)
cd src/Poster_Latex && bash Compilar.sh
```

### Ver documentos
```bash
okular Catch-Up/Presentation.pdf   # Diapositivas
okular Catch-Up/Paper.pdf          # Artículo
okular Catch-Up/Poster.pdf         # Póster
```

## 📝 Información de Contenido

**Proyecto**: Arquitectura para Monitoreo Real-Time de Calidad del Aire en Bogotá

**Autores**:
- Jose Alejandro Cortazar López
- Johan Esteban Castaño Martínez
- Stivel Pinilla Puerta

**Institución**: Programa de Ingeniería de Sistemas - Universidad Distrital Francisco José de Caldas

**Fecha**: Diciembre 2025

**Temas Cubiertos**:
- Integración multi-fuente (AQICN, Google, IQAir)
- Esquema PostgreSQL 3NF normalizado (8 entidades)
- Optimizaciones de query (<100ms latencia)
- Recomendaciones personalizadas de salud
- Validación de concurrencia (50-100+ usuarios)
- Proyecciones de escalabilidad

## 📞 Notas Técnicas

- **Lenguaje LaTeX**: Compilador pdflatex
- **Encoding**: UTF-8
- **Tema Beamer**: Madrid (profesional)
- **Aspecto Presentation**: 16:9 (widescreen)
- **Imágenes**: PNG (diagrama arquitectura, logos)

---

**Última actualización**: 13 de diciembre de 2025
