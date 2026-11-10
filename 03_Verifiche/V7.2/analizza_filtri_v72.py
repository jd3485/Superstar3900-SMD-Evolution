"""Idealized V7.2 BPF audit over the historic 270-channel CSV (no hardware)."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'08_Firmware_Prototipi'/'V7.2'))
from duc_if2_offline_v72 import IF1_HZ, filter_ideal_bpf_loss_db as loss

PLAN = ROOT/'02_Piano_Frequenze'/'V6.4'/'PIANO_PLL_LO_270_RX_V6.4.csv'


def evaluate():
    with PLAN.open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 270 or sum(row['alfa']=='1' for row in rows) != 30:
        raise ValueError("historical 270/30 plan mismatch")
    wanted, lo, image = [], [], []
    for row in rows:
        rf = int(row['rf_hz'])
        if int(row['lo_hz']) != rf+IF1_HZ:
            raise ValueError("unexpected LO1 on " + row['banda']+row['canale'])
        wanted.append(loss(rf, 25_000_000, 29_000_000, 5))
        lo.append(loss(rf+IF1_HZ, 25_000_000, 29_000_000, 5))
        image.append(loss(rf+2*IF1_HZ, 25_000_000, 29_000_000, 5))
    return {
        "analysis":"ideal Butterworth analog transfer only, not hardware",
        "channels":len(rows),
        "alpha_count":sum(row['alfa']=='1' for row in rows),
        "if1_lower_spur_9785_loss_db":loss(9_785_000,10_685_000,10_705_000,2),
        "rf_wanted_max_ideal_loss_db":max(wanted),
        "rf_image_min_relative_ideal_loss_db":min(i-w for i,w in zip(image,wanted)),
        "rf_lo_leak_min_relative_ideal_loss_db":min(l-w for l,w in zip(lo,wanted)),
        "assembly_authorized":False,
        "rf_tx_permitted":False,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
