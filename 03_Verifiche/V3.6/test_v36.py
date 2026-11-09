#!/usr/bin/env python3
"""V3.6 regression tests, including negative controls for pin map & shorts."""
import tempfile
from pathlib import Path
from audit_v36 import audit, inspect, PCB, SCH_CSV
r,objects=audit(PCB,record=False)
assert r['revision']=='V3.6'
assert r['footprints']==15
assert r['nets']==8
assert r['segments']==43
assert r['vias']==64
assert set(r['zones_declared_unfilled'])=={'F.Cu','In1.Cu','In2.Cu','B.Cu'}
assert not r['2d_clashes']
assert r['min_2d_inter_net_copper_clearance_mm']>=.20
assert not r['unconnected_nonground_nets']
assert r['ground_pad_count']==24
assert not r['ground_pads_without_explicit_local_via']
assert r['schematic_pin_assignments_ok']==31
assert not r['schematic_pin_mismatches']
assert 'NOT FOR FAB' in PCB.read_text()
assert 'SMA' in r['sma_center_2_05mm'] or 'manufacturer' in r['sma_center_2_05mm']
assert not r['copper_zones_filled']=='YES'
# Negative control 1: wrong net number assignment in old V3.5 L101 should be caught.
old=PCB.parents[1]/'Modulo_RX_Test_50ohm_V3.5/S3900E_RX_TEST_50R_V3_5_PILOT_ROUTES_NOT_FOR_FAB.kicad_pcb'
rold,_=audit(old,record=False)
assert len(rold['schematic_pin_mismatches'])==2, rold['schematic_pin_mismatches']
# Negative control 2: deliberately force short at RF attenuator trunk.
txt=PCB.read_text()
short='  (segment (start 49 65) (end 59 65) (width 0.280) (layer "F.Cu") (net 2) (tstamp "11111111-1111-4111-8111-111111111111"))\n'
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'corrupted.kicad_pcb';p.write_text(txt[:-2]+short+')\n')
    bad,_=audit(p,record=False)
    assert bad['2d_clash_count']>0
# Negative control 3: sever a non-GND path.
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'broken.kicad_pcb';p.write_text(txt.replace('(end 51.450 36.000)', '(end 40.000 36.000)',1))
    bad,_=audit(p,record=False)
    assert 'RF_LNA_INPUT' in bad['unconnected_nonground_nets']
print('V3.6: 18 core regression assertions + 3 negative controls PASS (STATIC only)')
