"""Verifiche della logica: tutte le combinazioni base in RX, TX fail-closed."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'08_Firmware_Prototipi'))
from radio_control_model import *
from dataclasses import replace

ok=Health(pll_locked=True, hw_interlock=True, supply_ok=True, temperature_ok=True,
          swr_ok=True, antenna_relay_settled=True, atu_busy=False)
assert evaluate(Controls(band='D',channel=9,ptt=True),ok)==Result(27_065_000,'AM',True,'')
# CH9 forza banda D, canale 9, AM (comandi fisici precedenti invariati)
assert evaluate(Controls(band='F',channel=19,alpha=True,ch9=True,mode='USB',ptt=True),ok).tx_enabled
assert evaluate(Controls(band='F',channel=19,alpha=True,ch9=True,mode='USB'),ok).rf_hz==27_065_000
assert evaluate(Controls(band='F',channel=19,alpha=True,ch9=False,mode='USB'),ok).rf_hz==28_095_000
assert evaluate(Controls(band='F',channel=19,alpha=True,ch9=False,mode='USB'),ok).mode=='USB'
for band in 'ABCDEF':
    for ch in range(1,41):
        for alpha in (False,True):
            e=evaluate(Controls(band=band,channel=ch,alpha=alpha,ptt=True),ok)
            assert e.rf_hz is not None
            expected=band=='D' and not(alpha and ch in {3,7,11,15,19})
            assert e.tx_enabled==expected
            for k in ('pll_locked','hw_interlock','supply_ok','temperature_ok','swr_ok','antenna_relay_settled'):
                assert not evaluate(Controls(band='D',channel=ch,ptt=True),replace(ok,**{k:False})).tx_enabled
assert not evaluate(Controls(band='D',channel=9,ptt=True),replace(ok,atu_busy=True)).tx_enabled
assert not evaluate(Controls(band='A',channel=9,ptt=True),ok).tx_enabled
assert not evaluate(Controls(band='D',channel=3,alpha=True,ptt=True),ok).tx_enabled
assert not evaluate(Controls(band='D',channel=9,ptt=False),ok).tx_enabled
assert not evaluate(Controls(band='D',channel=0,ptt=True),ok).tx_enabled
assert not evaluate(Controls(band='D',channel=9,mode='ERR',ch9=True,ptt=True),ok).tx_enabled
print('PASS: CH9/ALFA/AM, 6 bande, blocco TX, 6 fault inibitori, ATU busy e input invalidi.')
