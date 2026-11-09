#!/usr/bin/env python3
"""V5.8: diagnostic of RF trace proximity to GND stitching-via centres.

This is *not* a return-current solver, impedance simulator, KiCad zone filler,
thermal-spoke verifier, DRC or manufacturing sign-off. Inner GND planes are
UNFILLED in the candidate. Numbers are lengths in PCB drawing coordinates.
"""
from __future__ import annotations
import argparse, hashlib, json, math, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'03_Verifiche/V5.5'))
from audit_rame_v55 import PCB, actual_board_copper, parse, child, children, numpair
RF_NETS={'RF_LNA_INPUT','RF_LNA_IC_IN','RF_BIAS_OUT','RF_LNA_OUT','RF_ATTEN_IN','RF_ATTEN_OUT'}
SCREEN_RADIUS_MM=5.0 # diagnostic ranking threshold, NEVER a manufacturing limit
SAMPLE_STEP_MM=0.20


def audit(text:str, step_mm:float=SAMPLE_STEP_MM, reference_text:str|None=None):
    if not (0.05<=step_mm<=0.40):raise ValueError('Allowed diagnostic step 0.05–0.40 mm')
    board=parse(text)
    nets={int(n[1]):n[2] for n in children(board,'net')}
    items,counts,_=actual_board_copper(text)
    errors=[]
    zones=children(board,'zone');vias=children(board,'via')
    if (counts['pads'],counts['segments'],counts['vias'],counts['zones'],counts['filled_zone_polygons'])!=(44,44,70,4,0):
        errors.append('COPPER_OBJECT_COUNTS_OR_ZONE_FILL_CHANGED')
    if set(nets.values())!=({'','GND_RF','RF_LNA_INPUT','RF_LNA_IC_IN','RF_BIAS_OUT','RF_LNA_OUT','+5V_BENCH','RF_ATTEN_IN','RF_ATTEN_OUT'}):
        errors.append('NET_SET_CHANGED')
    if len(vias)!=70 or any(int(child(v,'net')[1])!=1 for v in vias):
        errors.append('GND_VIA_COUNT_OR_ASSIGNMENT_CHANGED')
    if len(zones)!=4 or {child(z,'layer')[1] for z in zones}!={'F.Cu','In1.Cu','In2.Cu','B.Cu'} or any(int(child(z,'net')[1])!=1 for z in zones):
        errors.append('ZONE_CONFIG_CHANGED')
    if reference_text is not None:
        ref_items,refcounts,refnets=actual_board_copper(reference_text)
        same=counts==refcounts and nets==refnets and len(items)==len(ref_items) and all(
            a['kind']==b['kind'] and a['id']==b['id'] and a['net']==b['net'] and a['geometry'].equals_exact(b['geometry'],1e-8)
            for a,b in zip(items,ref_items))
        if not same:errors.append('COPPER_NOT_IDENTICAL_TO_V48_REFERENCE')
    else:
        same=None
    gnd_vias=np.array([numpair(child(v,'at')) for v in vias if int(child(v,'net')[1])==1],dtype=float)
    if gnd_vias.shape!=(70,2):
        errors.append('INVALID_VIA_CENTRES')
        gnd_vias=np.zeros((1,2),dtype=float)
    tracks=[]
    for i,s in enumerate(children(board,'segment')):
        net_id=int(child(s,'net')[1]);name=nets.get(net_id,'?')
        if name not in RF_NETS:continue
        a=np.array(numpair(child(s,'start')));b=np.array(numpair(child(s,'end')))
        width=float(child(s,'width')[1]);length=float(np.linalg.norm(b-a))
        if child(s,'layer')[1]!='F.Cu' or not (0<width<=0.5) or length<0.001:
            errors.append('RF_SEGMENT_UNSUPPORTED:'+str(i));continue
        n=max(1,math.ceil(length/step_mm))
        t=np.linspace(0.,1.,n+1)
        samples=a[None,:]+(b-a)[None,:]*t[:,None]
        d=np.sqrt(np.sum((samples[:,None,:]-gnd_vias[None,:,:])**2,axis=-1))
        nearest=d.min(axis=1)
        max_idx=int(np.argmax(nearest))
        # Count *distinct* GND vias closer than 3mm to any point of the segment centreline.
        ab=b-a
        t_v=np.clip(((gnd_vias-a[None,:])@ab)/(length**2),0,1)
        closest=a[None,:]+t_v[:,None]*ab[None,:]
        via_to_line=np.linalg.norm(gnd_vias-closest,axis=1)
        tracks.append({
          'pcb_segment_index':i,'net':name,'start_mm':[round(float(v),4) for v in a],
          'end_mm':[round(float(v),4) for v in b], 'length_mm':round(length,4),
          'trace_width_mm':width,'sample_count':n+1,
          'nearest_gnd_via_centre_max_mm':round(float(nearest[max_idx]),4),
          'max_distance_sample_point_mm':[round(float(v),4) for v in samples[max_idx]],
          'nearest_gnd_via_centre_min_mm':round(float(nearest.min()),4),
          'samples_over_5mm':int(np.sum(nearest>SCREEN_RADIUS_MM)),
          'sample_fraction_over_5mm':round(float(np.mean(nearest>SCREEN_RADIUS_MM)),4),
          'distinct_gnd_vias_within_3mm_of_trace_centreline':int(np.sum(via_to_line<=3.0)),
          'distance_max_unsampled_upper_bound_mm':round(float(nearest[max_idx]+length/(2*n)),4)
        })
    if len(tracks)!=13 or {t['net'] for t in tracks}!=RF_NETS:
        errors.append('RF_TRACK_SET_CHANGED')
    summary=[]
    for name in sorted(RF_NETS):
        tt=[t for t in tracks if t['net']==name]
        if not tt:continue
        worst=max(tt,key=lambda x:x['nearest_gnd_via_centre_max_mm'])
        summary.append({'net':name,'rf_segment_count':len(tt),
          'rf_trace_total_length_mm':round(sum(x['length_mm'] for x in tt),4),
          'max_nearest_gnd_via_centre_mm':worst['nearest_gnd_via_centre_max_mm'],
          'conservative_upper_bound_at_sample_step_mm':max(t['distance_max_unsampled_upper_bound_mm'] for t in tt),
          'worst_point_mm':worst['max_distance_sample_point_mm'],
          'segments_with_any_sample_over_5mm':sum(bool(t['samples_over_5mm']) for t in tt),
          'screening_flag':'REVIEW_RETURN_PROXIMITY' if worst['nearest_gnd_via_centre_max_mm']>5 else 'NO_5MM_HOTSPOT_IN_SAMPLES'})
    summary.sort(key=lambda x:-x['max_nearest_gnd_via_centre_mm'])
    # Only a geometric statement about the source files. It is not a DRC or RF test.
    return {'revision':'V5.8','method':'sampled RF copper centerline vs closest GND through-via centre',
      'pcb_sha256':hashlib.sha256(text.encode()).hexdigest(),
      'reference_copper_identity_v48':same,'rf_nets':len(summary),'rf_tracks':len(tracks),
      'ground_via_centers':int(gnd_vias.shape[0]),'sampling_step_mm':step_mm,
      'nearest_via_distance_Lipschitz_sampling_upper_error_mm':round(step_mm/2,4),
      'review_threshold_mm_not_a_design_rule':SCREEN_RADIUS_MM,
      'by_net':summary,'by_segment':tracks,'errors':errors,
      'status':'STATIC_RF_VIA_PROXIMITY_AUDITED_NATIVE_PENDING' if not errors else 'STATIC_RF_AUDIT_FAIL',
      'native_erc':'NOT_RUN','native_drc':'NOT_RUN','native_zone_refill':'NOT_RUN',
      'fabrication_allowed':False,'tx_allowed':False,
      'interpretation':[
        'The nearest-via distance is a geometric measure ONLY, not return-current path length or RF performance.',
        'A continuous nearby ground plane could provide the main RF return independently of via spacing.',
        'Both inner ground planes are UNFILLED in this KiCad source; no dielectric stack-up/CPWG 50-ohm validation is available.',
        '5mm is a study hotspot threshold only; no manufacturing or RF limit is asserted.',
        'The upper bound for a straight segment follows from nearest-distance being 1-Lipschitz and step<=0.4mm.',
        'No extra ground via should be added without native DRC and a validated stack-up.',
        'NO FAB, NO PCBWay, NO TX']}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pcb',type=Path,default=PCB)
    ap.add_argument('--reference',type=Path,default=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB.kicad_pcb')
    ap.add_argument('--sample-step',type=float,default=SAMPLE_STEP_MM);ap.add_argument('--output',type=Path)
    a=ap.parse_args();result=audit(a.pcb.read_text(),a.sample_step,a.reference.read_text())
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('by_segment','interpretation')},indent=2,ensure_ascii=False))
    return 0 if result['status']=='STATIC_RF_VIA_PROXIMITY_AUDITED_NATIVE_PENDING' else 2
if __name__=='__main__':raise SystemExit(main())
