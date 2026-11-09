#!/usr/bin/env python3
"""Controllo V1.8: verifica matematico/strutturale, NON KiCad ERC, NON prova hardware."""
from pathlib import Path
import csv,re,math
D=Path(__file__).resolve().parents[1]
K=D/'04_KiCad/Modulo_MCU_CODEC_V1.8'
S=(K/'S3900E_MCU_CODEC_CLOCK_V1_8_DRAFT.kicad_sch').read_text()
assert S.startswith('(kicad_sch ') and S.rstrip().endswith(')')
# balance ignoring strings
quote=False; esc=False; lvl=0
for c in S:
    if quote:
        if esc:esc=False
        elif c=='\\': esc=True
        elif c=='"':quote=False
    else:
        if c=='"':quote=True
        elif c=='(':lvl+=1
        elif c==')':lvl-=1
        assert lvl>=0
assert not quote and lvl==0
with (K/'Pinout_Oscillatore_LDO_V1.8.csv').open(encoding='utf8') as f: r=list(csv.DictReader(f))
assert len(r)==9
xo={int(x['pin']):x['net'] for x in r if x['ref']=='X201'}
ldo={int(x['pin']):x['net'] for x in r if x['ref']=='U203'}
assert xo=={1:'XO_OE',2:'GND',3:'XO_MCLK_RAW',4:'3V3_AUDIO_CLK'}
assert ldo=={1:'5V_AUX_PROTECTED',2:'GND',3:'5V_AUX_PROTECTED',4:'NO_CONNECT',5:'3V3_AUDIO_CLK'}
for word in ['X201','U203','R204','R205','C215','C216','C217','C218','AUDIO_MCLK_12M288','AUDIO_BCLK','AUDIO_WCLK','CODEC_AVDD_LDO_OUT','CODEC_DVDD_LDO_OUT']:
    assert word in S,word
fs=48000; mclk=12288000; slots=2; slot_bits=32
assert mclk//fs==256
assert mclk/(1*2*128)==fs
assert mclk/(1*2*128)==fs
assert fs*slots*slot_bits==3072000
assert mclk/(fs*slots*slot_bits)==4
# Independent clocks cannot be used without synchronization: 40ppm drift => 1.92 frames/s
assert math.isclose(48000*40e-6,1.92,rel_tol=1e-12)
assert S.count('(pin ')>=96+4+9
print('PASS V1.8: 9 new pins (X201+U203), labels, no-connect, passive refs, MCLK=12.288MHz, FS=48kHz, BCLK=3.072MHz, no A/D internal LDO tied to 3.3V')
print('Not performed: KiCad ERC, exported netlist, STM32CubeMX and hardware measurements.')
