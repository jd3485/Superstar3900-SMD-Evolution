#!/usr/bin/env python3
"""V1.7 - verifica strutturale ST/TI, nessun ERC e nessun test elettrico."""
import csv, pathlib, re
p=pathlib.Path(__file__).resolve().parents[1]
f=p/'04_KiCad/Modulo_MCU_CODEC_V1.7/Mappatura_Pin_U201_U202_V1.7.csv'
with f.open(encoding='utf-8') as inp: pins=list(csv.DictReader(inp))
assert len(pins)==96,(len(pins),'expected 96')
for part, n in [('U201',64),('U202',32)]:
    ss=[x for x in pins if x['ic']==part]
    assert len(ss)==n
    assert {int(x['pin']) for x in ss}==set(range(1,n+1))
def pin(ref,pin):
    return next(x for x in pins if x['ic']==ref and int(x['pin'])==pin)
expected={('U201',9):('PC1','AUDIO_I2S_TX'),('U201',30):('PB10','AUDIO_BCLK'),('U201',43):('PA9','AUDIO_WCLK'),('U201',58):('PB5','AUDIO_I2S_RX'),('U201',59):('PB6','CODEC_I2C_SCL'),('U201',60):('PB7','CODEC_I2C_SDA'),('U202',24):('AVDD','CODEC_AVDD_LDO_OUT'),('U202',29):('DVDD','CODEC_DVDD_LDO_OUT'),('U202',30):('LDO_SELECT','3V3_CODEC_IO'),('U202',12):('SPI_SELECT','GND')}
for (part,n),(name,net) in expected.items():
    x=pin(part,n); assert x['pin_name']==name,(part,n,x,name)
    assert x['net']==net,(part,n,x,net)
for n in [24,29]: assert pin('U202',n)['net'] != '3V3_CODEC_IO' and pin('U202',n)['net']!='3V3_CODEC_LDOIN'
# All intentional shared nets actually have a producer and a consumer in pin mappings (except external future nets)
for n in ['AUDIO_BCLK','AUDIO_WCLK','AUDIO_I2S_TX','AUDIO_I2S_RX','CODEC_I2C_SDA','CODEC_I2C_SCL','CODEC_RESET_N']:
    assert sum(r['net']==n for r in pins)>=2,n
f2=p/'04_KiCad/Modulo_MCU_CODEC_V1.7/S3900E_MCU_CODEC_V1_7_DRAFT.kicad_sch'
s=f2.read_text(encoding='utf-8')
assert s.startswith('(kicad_sch ') and s.rstrip().endswith(')')
assert s.count('(pin ') == 96+4
assert s.count('(no_connect ') > 35
assert 'CODEC_AVDD_LDO_OUT' in s and 'CODEC_DVDD_LDO_OUT' in s
# Parenthesis balance ignoring strings/escaped quotes
level=0; quoted=False; esc=False
for c in s:
    if esc: esc=False; continue
    if c=='\\' and quoted: esc=True; continue
    if c=='"': quoted=not quoted; continue
    if not quoted:
        if c=='(': level+=1
        elif c==')': level-=1
        assert level>=0
assert level==0 and not quoted
print('PASS: 64 STM32 + 32 CODEC; 11 pin checks, labels shared, internal LDO rails, KiCad syntax parentheses; NO ERC performed')
