"""Run the full version 3 pipeline from the repository root: python analysis/00_run_all.py

analysis/09_prepare_state_boundaries.py is a one-off step whose output is committed.

Set RSCRIPT to the Rscript executable if it is not on PATH. Install R packages first with
Rscript analysis/install_r_packages.R (into the ignored .runtime/R-library).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RSCRIPT = os.environ.get("RSCRIPT") or shutil.which("Rscript") or r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe"

STEPS = [
    ("py", "analysis/13_control_provenance.py"),
    ("R", "analysis/01_load_data_impute.R"),
    ("py", "analysis/02_trade_restructuring.py"),
    ("R", "analysis/03_causal_impact.R"),
    ("R", "analysis/04_robustness_and_placebos.R"),
    ("py", "analysis/05_trend_benchmarks.py"),
    ("py", "analysis/06_land_use_link.py"),
    ("R", "analysis/10_timing_and_political_cycle.R"),
    ("R", "analysis/12_mcmc_diagnostics.R"),
    ("R", "analysis/14_monte_carlo_check.R"),
    ("py", "analysis/11_state_map.py"),
    ("py", "analysis/07_figures.py"),
    ("py", "analysis/08_graphical_abstract.py"),
]

env = dict(os.environ, PYTHONIOENCODING="utf-8")
for kind, script in STEPS:
    cmd = [RSCRIPT, script] if kind == "R" else [sys.executable, script]
    print(f"==> {script}", flush=True)
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)
print("Done.")
