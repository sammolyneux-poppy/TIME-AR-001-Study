#!/bin/bash
# TIME-AR-001: Complete replication script
set -e

echo "TIME-AR-001: Temporal Admissible Region Study"
echo "============================================="
echo ""

cd "$(dirname "$0")"

echo "Step 1: Computing gamma_crit and F15 classifications..."
python3 compute_gamma_crit.py
echo ""

echo "Step 2: Generating figures..."
python3 generate_figures.py
echo ""

echo "Step 3: Building DOCX..."
python3 build_docx.py
echo ""

echo "============================================="
echo "Replication complete. Output files:"
echo "  data/processed/ - All computed data"
echo "  figures/        - All figures"
echo "  docs/           - Report (MD + DOCX)"
echo "============================================="
