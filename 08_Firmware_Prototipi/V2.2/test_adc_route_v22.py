#!/usr/bin/env python3
"""Static register-contract checks only; no I2C exchange with real codec."""
import csv
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/'08_Firmware_Prototipi/V2.2/Registri_ADC_Simultanei_V2.2.csv'
rows={(int(x['page']),int(x['register_dec'])):int(x['value_hex'],16) for x in csv.DictReader(p.open())}
assert rows[(1,52)] & 0xC0 == 0x80, 'IN1L must be on left'
assert rows[(1,55)] & 0x30 == 0x20, 'IN2R must be on right'
assert rows[(1,55)] & 0xC0 == 0x00, 'IN1R must not be routed right'
assert rows[(0,81)] & 0xC0 == 0xC0, 'Both ADC must be enabled'
assert rows[(0,82)] == 0
assert len(rows)==8
pinmap=root/'04_KiCad/Modulo_MCU_CODEC_V2.1/Mappatura_Pin_U201_U202_V2.1.csv'
pins={(r['ic'],int(r['pin'])):r['net'] for r in csv.DictReader(pinmap.open())}
assert pins[('U202',13)]=='MIC_CODEC_IN'
assert pins[('U202',16)]=='FM_CODEC_IN'
assert 48000*2*32==3072000 and 48000*256==12288000
print('ADC register + source map: 10 static checks PASS. This does NOT program or validate codec hardware.')
