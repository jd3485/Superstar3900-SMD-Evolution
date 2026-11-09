#!/usr/bin/env python3
"""Test modello puro V4.0: non verificano hardware, emissioni o normativa."""
from dataclasses import replace
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'08_Firmware_Prototipi'))
from radio_supervisor_v40 import *

PASS=Guards(True,True,True,True,True,True,True,True)
assert not supervise(Settings(ptt=True),Guards()).tx_request
assert supervise(Settings(ptt=True),PASS).tx_request
counter=0; rx_positions=set(); d_tx=0
for band in 'ABCDEF':
  for ch in range(1,41):
    for alpha in (False,True):
      for mode in ('AM','FM','USB','LSB','CW'):
        x=Settings(primary=Tune(band,ch,alpha,mode),ptt=True)
        o=supervise(x,PASS); counter+=1
        should_tx=(band=='D' and not (alpha and ch in ALPHA_CHANNELS) and mode!='CW')
        assert o.tx_request==should_tx,(band,ch,alpha,mode,o)
        if ch in ALPHA_CHANNELS or not alpha:
          rx_positions.add((band,ch, bool(alpha)))
assert len(rx_positions)==270, len(rx_positions)
for ch in range(1,41):
    assert supervise(Settings(primary=Tune('D',ch,False,'AM'),ptt=True),PASS).tx_request
    d_tx+=1
# CH9 highest user tuning priority, without making bad inputs valid.
assert supervise(Settings(primary=Tune('F',19,True,'USB'),ch9=True,ptt=True,dual_watch=True,echo=True,roger_beep=True,ctcss_rx=True),PASS).rx_hz==27065000
ch9=supervise(Settings(primary=Tune('F',19,True,'USB'),ch9=True,ptt=True,dual_watch=True,echo=True,roger_beep=True,ctcss_rx=True),PASS)
assert (ch9.tx_request,ch9.rx_mode,ch9.dw_effective,ch9.echo_effective,ch9.roger_beep_armed,ch9.subtones_rx_effective)==(True,'AM',False,False,False,False)
assert supervise(Settings(ch9=True,ptt=True,ctcss_tx=True,dcs_tx=True),PASS).tx_request
assert supervise(Settings(primary=Tune('F',19,True,'USB'),ch9=False),PASS).rx_hz==28095000
# PA must not let any RF through, even if CH9 or physical PTT/VOX.
for ptt in (False,True):
 for vox in (False,True):
  x=supervise(Settings(pa=True,ch9=True,ptt=ptt,vox_enabled=True,vox_gate=vox),PASS)
  assert not x.tx_request and x.rx_mode=='PA' and x.pa_audio_requested==(ptt or vox)
# Dual-watch B is RX-only: TX always targets A, never B.
s=Settings(primary=Tune('D',9,False,'FM'),secondary=Tune('D',19,False,'FM'),dual_watch=True,dw_slot='B')
assert supervise(s,PASS).rx_hz==27185000
assert supervise(replace(s,ptt=True),PASS).tx_target_hz==27065000
# All guards required independently, including country profile.
for name in PASS.__dataclass_fields__:
 assert not supervise(Settings(ptt=True),replace(PASS,**{name:False})).tx_request,name
# Vox must be enabled AND armed. No RF without valid guards.
assert not supervise(Settings(vox_enabled=True,vox_gate=True),Guards()).tx_request
assert supervise(Settings(vox_enabled=True,vox_gate=True),PASS).tx_request
assert not supervise(Settings(vox_enabled=False,vox_gate=True),PASS).tx_request
# FM subtone only, CTCSS and DCS conflict denies TX.
assert supervise(Settings(primary=Tune('D',9,False,'FM'),ctcss_rx=True,ctcss_tx=True),PASS).subtones_rx_effective
assert not supervise(Settings(primary=Tune('D',9,False,'FM'),ctcss_rx=True,ctcss_tx=True),PASS).subtones_tx_effective
assert supervise(Settings(primary=Tune('D',9,False,'FM'),ctcss_rx=True,ctcss_tx=True,ptt=True),PASS).subtones_tx_effective
assert not supervise(Settings(primary=Tune('D',9,False,'USB'),ctcss_rx=True,ctcss_tx=True),PASS).subtones_rx_effective
assert not supervise(Settings(primary=Tune('D',9,False,'FM'),ctcss_tx=True,dcs_tx=True,ptt=True),PASS).tx_request
# Invalid control state never causes TX, even CH9.
for bad in (Tune('Z',9,False,'AM'),Tune('D',0,False,'AM'),Tune('D',True,False,'AM'),Tune('D',9,False,'XX')):
 assert not supervise(Settings(primary=bad,ch9=True,ptt=True),PASS).tx_request
# Reject malformed typed flags, not only falsy values. Strings and ints are invalid.
for key in PASS.__dataclass_fields__:
 assert not supervise(Settings(ptt=True),replace(PASS,**{key:'true'})).tx_request
for key in ('ptt','ch9','pa','vox_gate','dual_watch','echo'):
 assert not supervise(replace(Settings(ptt=True),**{key:'False'}),PASS).tx_request
assert not supervise(Settings(ptt=1),PASS).tx_request
# PA and CW no TX.
assert not supervise(Settings(primary=Tune('D',9,False,'CW'),ptt=True),PASS).tx_request
# Fail closed in DW if secondary is invalid.
assert not supervise(Settings(secondary=Tune('X',9,False,'FM'),dual_watch=True,ptt=True),PASS).tx_request
print(json.dumps({"passed":True,"matrix_states_checked":counter,"distinct_rx_positions":len(rx_positions),"channel_d_tx_checked":d_tx,"guard_fault_injection":len(PASS.__dataclass_fields__),"note":"test funzionali software, nessun TX reale"},ensure_ascii=False,indent=2))
