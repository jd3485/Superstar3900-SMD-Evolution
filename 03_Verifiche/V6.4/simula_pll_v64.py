#!/usr/bin/env python3
"""Piano LO LMX2572 V6.4, calcoli esatti e stress numerico; NON hardware/timing/registri.

Non modifica file preesistenti: genera soltanto rapporti della revisione V6.4.
L'integer-N qui e' MATEMATICA, non una configurazione TICS Pro approvata.
"""
from __future__ import annotations
import csv
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '02_Piano_Frequenze'))
from frequency_plan import rows as original_channel_rows  # noqa: E402

IF_HZ = 10_695_000
TCXO_HZ = 12_800_000
R_DIV = 10
PFD_HZ = TCXO_HZ // R_DIV
OUT_DIV = 128
VCO_LO_HZ = 3_200_000_000
VCO_HI_HZ = 6_400_000_000
INT_PFD_MIN_HZ = 250_000
INT_PFD_MAX_HZ = 250_000_000
MAX_REF_PPM_ASSUMED = 2.5  # solo scenario; il TCXO scelto non e' stato qualificato


def synthesize(band: str, channel: str, rf_hz: int) -> dict:
    if not isinstance(rf_hz, int) or rf_hz <= 0:
        raise ValueError('rf_hz deve essere un intero positivo')
    if type(band) is not str or type(channel) is not str or not band or not channel:
        raise ValueError('banda e canale obbligatori')
    lo_hz = rf_hz + IF_HZ
    vco_hz = lo_hz * OUT_DIV
    q, rem = divmod(vco_hz, PFD_HZ)
    if rem or not (INT_PFD_MIN_HZ <= PFD_HZ <= INT_PFD_MAX_HZ):
        raise ValueError('piano integer N non disponibile alla frequenza impostata')
    if not (VCO_LO_HZ <= vco_hz <= VCO_HI_HZ):
        raise ValueError('VCO fuori intervallo dichiarato LMX2572')
    return {
        'banda': band, 'canale': channel, 'rf_hz': rf_hz,
        'fi1_hz': IF_HZ, 'lo_hz': lo_hz,
        'vco_hz': vco_hz, 'tcxo_hz': TCXO_HZ,
        'r_div': R_DIV, 'pfd_hz': PFD_HZ, 'out_div': OUT_DIV,
        'pll_n': q, 'pll_num': 0, 'pll_den': 1,
        'if_image_hz': lo_hz + IF_HZ,
        'if_image_separation_hz': 2 * IF_HZ,
        'f_vco_margin_low_hz': vco_hz - VCO_LO_HZ,
        'f_vco_margin_high_hz': VCO_HI_HZ - vco_hz,
        'status': 'MODELLO_MATEMATICO_NON_PROFILO_REGISTRI'
    }


def build_table():
    table = []
    for band, channel, alpha, hz, _tx_allowed_legacy in original_channel_rows():
        entry = synthesize(band, channel, hz)
        entry['alfa'] = int(alpha)
        entry['tx_permitted_v64'] = 0  # TX sempre disabilitata in V6.4
        table.append(entry)
    return table


def stress_oscillator(table, n=25000, seed=6402, ppm=MAX_REF_PPM_ASSUMED):
    if n < 1 or ppm < 0:
        raise ValueError('parametri stress non validi')
    rng = random.Random(seed)
    worst = (0.0, None)
    abs_hz = []
    for _ in range(n):
        ch = rng.choice(table)
        deviation_ppm = rng.uniform(-ppm, ppm)
        shift_hz = ch['lo_hz'] * deviation_ppm * 1e-6
        abs_hz.append(abs(shift_hz))
        if abs(shift_hz) > worst[0]:
            worst = (abs(shift_hz), {'banda': ch['banda'], 'canale': ch['canale'], 'ppm': deviation_ppm, 'lo_hz': ch['lo_hz']})
    abs_hz.sort()
    return {
        'samples': n,
        'scenario_ppm_uniform': [-ppm, ppm],
        'seed': seed,
        'max_absolute_lo_error_hz_sample': round(worst[0], 6),
        'p99_abs_lo_error_hz_sample': round(abs_hz[int(0.99*(n-1))], 6),
        'worst_sample_metadata': worst[1],
        'absolute_max_bound_for_all_channels_hz': round(max(e['lo_hz'] for e in table) * ppm / 1e6, 6),
        'note': 'Scenario ipotetico TCXO ±2.5ppm. Esclude deriva IF, rumore PLL e offset di riferimento misurati.'
    }


def linear_3v3_pll_budget(input_v=5.0, output_v=3.3, load_ma=130, theta_ja=199.6, ambient_c=85):
    if not input_v > output_v > 0 or load_ma < 0 or theta_ja <= 0:
        raise ValueError('budget termico impossibile')
    loss_w = (input_v - output_v) * load_ma / 1000
    return {'vin_v': input_v, 'vout_v': output_v, 'load_ma_assumed': load_ma,
            'loss_w_ideal': round(loss_w, 6),
            'theta_ja_k_per_w_assumed_conservative': theta_ja,
            'ambient_c_assumed': ambient_c,
            'tj_ideal_c': round(ambient_c+theta_ja*loss_w, 3),
            'thermal_125c_limit_exceeded': ambient_c+theta_ja*loss_w > 125,
            'note': 'RthetaJA conservativa illustrativa; nessuna valutazione termica reale PCB/part number/footprint.'}


def report():
    table = build_table()
    if len(table) != 270 or len({(x['banda'], x['canale']) for x in table}) != 270:
        raise ValueError('Il piano RX deve coprire esattamente 270 posizioni')
    if len({x['rf_hz'] for x in table}) != len(table):
        raise ValueError('Collisioni RF fra le 270 posizioni')
    stats = {
        'revisione': 'V6.4', 'canali': len(table), 'bande': sorted({r['banda'] for r in table}),
        'alpha_count': sum(r['alfa'] for r in table),
        'rx_min_hz': min(r['rf_hz'] for r in table),
        'rx_max_hz': max(r['rf_hz'] for r in table),
        'lo_min_hz': min(r['lo_hz'] for r in table),
        'lo_max_hz': max(r['lo_hz'] for r in table),
        'vco_min_hz': min(r['vco_hz'] for r in table),
        'vco_max_hz': max(r['vco_hz'] for r in table),
        'pll_n_min': min(r['pll_n'] for r in table),
        'pll_n_max': max(r['pll_n'] for r in table),
        'image_min_hz': min(r['if_image_hz'] for r in table),
        'image_max_hz': max(r['if_image_hz'] for r in table),
        'pfd_hz': PFD_HZ, 'ref_hz': TCXO_HZ,
        'r_div': R_DIV, 'out_div': OUT_DIV,
        'integer_n_all': all(r['pll_num']==0 for r in table),
        'image_offset_hz': 2*IF_HZ, 'tx_disabled_all': all(r['tx_permitted_v64']==0 for r in table),
        'jitter_phase_noise_spectrum': 'NOT_RUN_MODEL_UNAVAILABLE',
        'tics_pro_register_profile': 'NOT_GENERATED',
        'kicad_erc_drc': 'NOT_RUN_NOT_INSTALLED',
        'spice_loop_transient': 'NOT_RUN_VENDOR_MODEL_NOT_AVAILABLE',
        'tcxo_scenario': stress_oscillator(table),
        'pll_3v3_ldo_nominal_105ma_ambient85': linear_3v3_pll_budget(load_ma=105),
        'pll_3v3_ldo_design_150ma_ambient85': linear_3v3_pll_budget(load_ma=150),
        'note_alimentazione': 'La V6.3 gia prevedeva 150 mA nominali PLL_LO sul 5V_RF. La V6.4 ripartisce quel budget e richiede LDO dedicato 3V3_PLL; non sommare due volte. A 150 mA e 85C l esempio termico puo superare 125C: BLOCCO TERMICO APERTO.',
        'rf_pa_connected': False,'fab_authorized': False
    }
    return table, stats


def write_outputs():
    table, st = report()
    csvpath = ROOT/'02_Piano_Frequenze/V6.4/PIANO_PLL_LO_270_RX_V6.4.csv'
    with csvpath.open('w',encoding='utf8',newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0])); writer.writeheader();writer.writerows(table)
    stpath = ROOT/'03_Verifiche/V6.4/RISULTATI_SIMULAZIONI_PLL_V6.4.json'
    stpath.write_text(json.dumps(st, ensure_ascii=False, indent=2)+'\n',encoding='utf8')
    return csvpath,stpath


if __name__=='__main__':
    p,s = write_outputs()
    _,stat = report()
    print('V6.4 PASS',len(build_table()),'RX; fLO',stat['lo_min_hz'],stat['lo_max_hz'],'VCO',stat['vco_min_hz'],stat['vco_max_hz'])
    print('CSV',p,'\nJSON',s)
