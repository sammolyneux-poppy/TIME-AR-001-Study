#!/bin/bash
# TIME-AR-001: Complete replication script
# Runs all computation, statistical tests, figures, and DOCX generation.
set -e

echo "TIME-AR-001: Temporal Admissible Region Study — Full Pipeline"
echo "============================================================="
echo ""

cd "$(dirname "$0")"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.9+."
    exit 1
fi

echo "Step 1: Computing gamma_crit and F15 classifications..."
python3 compute_gamma_crit.py
echo ""

echo "Step 2: Running Fisher exact test..."
python3 fisher_test.py
echo ""

echo "Step 3: Generating figures..."
python3 generate_figures.py || echo "WARNING: Figure generation failed (matplotlib may not be installed). Run: pip3 install matplotlib"
echo ""

echo "Step 4: Building supplementary DOCX..."
python3 build_docx.py || echo "WARNING: DOCX build failed (python-docx may not be installed). Run: pip3 install python-docx"
echo ""

echo "============================================================="
echo "Replication complete. Output files:"
echo "  data/processed/ - All computed data (master_scorecard.csv + 5 others)"
echo "  figures/         - All figures (8 PNGs)"
echo "  docs/           - Supplementary tables DOCX"
echo "============================================================="
