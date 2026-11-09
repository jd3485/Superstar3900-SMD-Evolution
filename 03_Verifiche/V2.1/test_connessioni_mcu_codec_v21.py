#!/usr/bin/env python3
"""V2.1 - static verification only. NOT KiCad ERC or electronics simulation."""
import csv, json, re, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sch=(ROOT/'04_KiCad/Modulo_MCU_CODEC_V2.1/S3900E_MCU_CODEC_AFE_V2_1_DRAFT.kicad_sch').read_text()
with (ROOT/'04_KiCad/Modulo_MCU_CODEC_V2.1/Mappatura_Pin_U201_U202_V2.1.csv').open(newline='') as f: pinmap=list(csv.DictReader(f))
with (ROOT/'04_KiCad/Modulo_MCU_CODEC_V2.1/Contratto_Pin_AF_SAI_I2C_SPI_V2.1.csv').open(newline='') as f: afmap=list(csv.DictReader(f))
get=lambda ref,p:next(r for r in pinmap if r['ic']==ref and r['pin']==str(p))
checks={
 'MCU_64_pins_and_codec_32_pins':len(pinmap)==96 and sum(r['ic']=='U201' for r in pinmap)==64,
 'MIC_left_ADC_U202_pin13':get('U202',13)['net']=='MIC_CODEC_IN',
 'FM_right_ADC_U202_pin16':get('U202',16)['net']=='FM_CODEC_IN',
 'FM_left_ADC_U202_pin15_unassigned':get('U202',15)['net']=='UNASSIGNED_NC_DRAFT',
 'FM_label_at_pin16':'(label "FM_CODEC_IN" (at 351.7400 186.6700' in sch,
 'NC_moved_from_pin16_to15':'(no_connect (at 351.7400 182.8600' in sch and '(no_connect (at 351.7400 186.6700' not in sch,
 'no_fm_pin15_label':'(label "FM_CODEC_IN" (at 351.7400 182.8600' not in sch,
 'all_8_MCU_alt_function_pins_consistent':all(get('U201',r['pin'])['pin_name']==r['gpio'] and get('U201',r['pin'])['net']==r['net'] for r in afmap),
 'SAI_audio_slot_calculation': 48_000*2*32==3_072_000 and 12_288_000/48_000==256,
 'first_IF_LO_image_math':abs((25.615+10.695)-36.310)<1e-8 and abs((28.305+2*10.695)-49.695)<1e-8,
 'no_duplicate_IC_pins':len({(r['ic'],r['pin']) for r in pinmap})==96,
 'parenthesis_balance_rough': sch.count('(')==sch.count(')'),
}
report={'revision':'V2.1','type':'STATIC SOURCE AUDIT; NOT ERC','passed':sum(checks.values()),'total':len(checks),'checks':checks,
'limitations':['KiCad executable absent, no netlist/ ERC','AF values from datasheet must be checked in STM32CubeMX','Codec register map not programmed or validated','ADC concurrency not measured','No PCB/EMC/SPICE tests']}
assert all(checks.values()),json.dumps(report,indent=2)
out=ROOT/'03_Verifiche/V2.1/Report_Test_V2.1.json'
out.write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(f'STATIC tests {report["passed"]}/{report["total"]}: PASS; NOT ERC')
