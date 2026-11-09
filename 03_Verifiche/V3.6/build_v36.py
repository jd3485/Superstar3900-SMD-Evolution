#!/usr/bin/env python3
"""Generate V3.6 copper/stitching study from V3.5 (NO KICAD NATIVE DRC).
Preserves V3.5 historic file; reversible, deterministic UUIDs. No Gerbers.
"""
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
import re
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.5/S3900E_RX_TEST_50R_V3_5_PILOT_ROUTES_NOT_FOR_FAB.kicad_pcb'
OUT=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.6/S3900E_RX_TEST_50R_V3_6_GND_RETURN_STUDY_NOT_FOR_FAB.kicad_pcb'
t=OLD.read_text(encoding='utf-8')
def tag(s): return str(uuid5(NAMESPACE_URL, 'S3900E-V36/'+s))
def mm(x): return f'{x:.3f}'
def track(x,y,xx,yy,net=1,width=.45):
    assert (x,y)!=(xx,yy)
    return f'  (segment (start {mm(x)} {mm(y)}) (end {mm(xx)} {mm(yy)}) (width {mm(width)}) (layer "F.Cu") (net {net}) (tstamp "{tag("trace-"+str((x,y,xx,yy,net)))}"))\n'
def via(x,y,size=.7,drill=.3):
    return f'  (via (at {mm(x)} {mm(y)}) (size {mm(size)}) (drill {mm(drill)}) (layers "F.Cu" "B.Cu") (net 1) (tstamp "{tag("via-"+str((x,y)))}"))\n'
# Fix mismatch with schematic V3.1, which assigns L101 pin 2 to RFOUT_BIAS
# and pin 1 to +5V_BENCH. Only change PAD NUMBERS, not physical nets.
start=t.index('(footprint "S3900E_v33:L_0603"')
end=t.index('  (footprint ',start+12)
block=t[start:end]
assert '(pad "1" smd roundrect (at -0.800' in block
assert '(pad "2" smd roundrect (at 0.800' in block
block=block.replace('(pad "1" smd roundrect (at -0.800','(pad "2" smd roundrect (at -0.800',1)
block=block.replace('(pad "2" smd roundrect (at 0.800','(pad "1" smd roundrect (at 0.800',1)
t=t[:start]+block+t[end:]
# Add inner 3rd ground region (L3) -- polygon is UNFILLED, must open/refill in KiCad.
zone=f'''  (zone (net 1) (net_name "GND_RF") (layer "In2.Cu") (tstamp "{tag('zone-In2-Cu')}")
    (hatch edge 0.5) (connect_pads (clearance 0.3)) (min_thickness 0.25)
    (fill yes (thermal_gap 0.4) (thermal_bridge_width 0.5))
    (polygon (pts (xy 20.7 20.7) (xy 129.3 20.7) (xy 129.3 81.3) (xy 20.7 81.3)))
  )
'''
# Four SMA footprints: explicit GND pad tracks to off-footprint vias. 4 each.
newtracks=[]; newvias=[]
for x0,y0 in [(28,36),(122,36),(28,65),(122,65)]:
    for dx in (-2.85,2.85):
        for dy in (-2.95,2.95):
            x=x0+dx; y=y0+dy; xv=x0+(-4.90 if dx<0 else 4.90)
            newtracks.append(track(x,y,xv,y,1,.45)); newvias.append(via(xv,y))
# Shunt decoupling and bench pads -> dedicated local vias (not via-in-pad)
for x,y,xv,yv in [
    (79.8,45,81.7,45),  # C103 68pF
    (86.8,45,88.7,45),  # C104 1.2nF
    (95.55,45,98.0,45), # C105 1uF
    (110,48,113.0,48),  # J105 return
]:
    newtracks.append(track(x,y,xv,yv,1,.45));newvias.append(via(xv,yv))
# Additional ground fences on either side of signal paths (do not claim shielding measured)
fence=[]
for yy in (31.5,40,59,72):
    for xx in (39,46,53,60,75,82,89,96,103,110):
        if (xx,yy) in [(x,y) for x,y in fence]: continue
        fence.append((xx,yy))
for x,y in fence: newvias.append(via(x,y))
# Include notes as silkscreen text outside existing footprints (without corrupting copper).
note=f'''  (gr_text "V3.6 GND STUDY - ALL ZONES UNFILLED" (at 75 27 0) (layer "F.SilkS")
    (effects (font (size 0.8 0.8) (thickness 0.13))) (tstamp "{tag('silk-warning')}"))
'''
t=t.replace('V3.5 FIRST ROUTING STUDY - NOT FOR FAB','V3.6 GND STUDY - NOT FOR FAB')
t=t.replace('s3900e_v35_route_study','s3900e_v36_return_study')
t=t.replace('RX TEST ONLY - NO TX - PILOT ROUTES V3.5','RX TEST ONLY - NO TX - RETURNS V3.6')
assert t.endswith(')\n')
t=t[:-2]+ '\n' + zone + ''.join(newtracks)+''.join(newvias)+note+')\n'
OUT.write_text(t,encoding='utf-8')
print('WROTE',OUT,'bytes',OUT.stat().st_size,'new traces',len(newtracks),'new vias',len(newvias),'fence',len(fence))
