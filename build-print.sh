#!/usr/bin/env bash
# build-print.sh — Compila PDF stampa per Il Bilanciere Quantistico (IT)
set -e

PDFLATEX="C:/Users/Utente/AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe"
MAIN="main-print-it"
LOG="${MAIN}.log"

echo "=== Passaggio 1/2 ==="
"$PDFLATEX" -interaction=nonstopmode "${MAIN}.tex"

echo "=== Passaggio 2/2 (aggiorna TOC) ==="
"$PDFLATEX" -interaction=nonstopmode "${MAIN}.tex"

echo ""
echo "=== Conteggio overflow ==="
OVERFLOW=$(grep -c "Overfull \\\\hbox" "$LOG" 2>/dev/null || echo "0")
echo "Overfull hbox: $OVERFLOW"

if [ "$OVERFLOW" -gt 0 ]; then
  echo ""
  echo "=== Dettaglio overflow ==="
  grep "Overfull \\\\hbox" "$LOG" | head -30
fi

echo ""
echo "=== PDF generato: ${MAIN}.pdf ==="
