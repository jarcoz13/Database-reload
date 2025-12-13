#!/bin/bash

# Compilation script for Beamer presentation
# Generates PDF from LaTeX source

FILENAME="Presentation"
OUTPUT_DIR="../../Catch-Up"

echo "Compilando presentación LaTeX: $FILENAME.tex"
echo "=================================================="

# First compilation pass
pdflatex -interaction=nonstopmode -shell-escape $FILENAME.tex > /dev/null 2>&1

# Second compilation pass (for TOC and references)
pdflatex -interaction=nonstopmode -shell-escape $FILENAME.tex > /dev/null 2>&1

# Third compilation pass (final)
pdflatex -interaction=nonstopmode -shell-escape $FILENAME.tex > /dev/null 2>&1

# Check if PDF was generated successfully
if [ -f "$FILENAME.pdf" ]; then
    # Create output directory if it doesn't exist
    mkdir -p "$OUTPUT_DIR"
    
    # Move PDF to Catch-Up directory
    cp "$FILENAME.pdf" "$OUTPUT_DIR/$FILENAME.pdf"
    
    # Get file size
    SIZE=$(du -h "$OUTPUT_DIR/$FILENAME.pdf" | cut -f1)
    
    echo "✓ Compilación exitosa"
    echo "✓ PDF generado: $OUTPUT_DIR/$FILENAME.pdf ($SIZE)"
    
    # Clean up temporary files
    rm -f $FILENAME.aux $FILENAME.log $FILENAME.nav $FILENAME.out $FILENAME.snm $FILENAME.toc 2>/dev/null
    
else
    echo "✗ Error en compilación. Revisar $FILENAME.log para más detalles"
    exit 1
fi

echo "Compilación completada."
