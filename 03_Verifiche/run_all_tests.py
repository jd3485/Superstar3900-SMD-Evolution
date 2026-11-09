"""Test locali; modelli numerici, non prove RF/EM/PLL hardware."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
scripts=['test_frequency_plan.py','test_pll_plan.py','test_control_model.py','test_rx_noise_budget.py','test_stage2.py','test_lo_filter.py']
for script in scripts:
    print('>',script,flush=True)
    subprocess.run([sys.executable,str(root/script)],check=True)
print(f'RISULTATO: {len(scripts)} suite PASS (solo controlli software; RF/EM e PCB non verificati).')
