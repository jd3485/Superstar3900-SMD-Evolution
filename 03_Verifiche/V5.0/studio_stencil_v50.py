#!/usr/bin/env python3
"""Confronto puramente geometrico di due ipotesi stencil U101.
NON genera file CAM, non valida assemblaggio, non modifica KiCad.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'03_Verifiche/V4.9/AUDIT_VIA_STENCIL_V4.9.json'

# Finestre alternative: due rettangoli in F.Paste, soltanto esplorativi;
# deliberatamente collocati fra le 3 righe dei 6 fori.
WINDOWS = [(67.25,32.78,68.75,33.40),(67.25,33.93,68.75,34.55)]

def distance_point_rect(x,y,rect):
    x1,y1,x2,y2=rect
    dx=max(x1-x,0,x-x2);dy=max(y1-y,0,y-y2)
    return math.hypot(dx,dy)

def compute(data):
    pad=data['U101']; a=pad['thermal_pad_bbox_mm']; prior=pad['paste_bbox_mm']
    vias=data['vias']; res=[]
    for r in WINDOWS:
        if not (a[0]<=r[0]<r[2]<=a[2] and a[1]<=r[1]<r[3]<=a[3]):
            raise ValueError('Finestra fuori dal pad')
        if not (prior[0]<=r[0]<r[2]<=prior[2] and prior[1]<=r[1]<r[3]<=prior[3]):
            raise ValueError('Finestra fuori dall’apertura corrente')
        for v in vias:
            gap=distance_point_rect(v['x'],v['y'],r)-v['drill']/2
            res.append(round(gap,6))
            if gap < 0.10-1e-8:
                raise ValueError(f'Finestra troppo vicina al foro {v}')
    a0=pad['thermal_pad_size_mm'][0]*pad['thermal_pad_size_mm'][1]
    area=sum((r[2]-r[0])*(r[3]-r[1]) for r in WINDOWS)
    return {
       'revision':'V5.0','purpose':'geometry_only_assembly_tradeoff','fabrication_approved':False,
       'reference':'03_Verifiche/V4.9/AUDIT_VIA_STENCIL_V4.9.json',
       'pad_area_mm2':round(a0,6),
       'baseline_unsegmented_paste_area_mm2':pad['paste_area_mm2'],
       'baseline_coverage_percent':round(100*pad['paste_coverage_ratio_vs_pad'],2),
       'option_A':{'description':'6 via-in-pad con riempimento/cappatura approvati + apertura paste di riferimento',
                   'status':'IN_ATTESA_DI_APPROVAZIONE_PCBWAY_E_ASSEMBLATORE',
                   'coverage_percent':round(100*pad['paste_coverage_ratio_vs_pad'],2)},
       'option_B':{'description':'2 finestre lontane dai fori non riempiti - SOLTANTO STUDIO, NON RACCOMANDATA',
                   'stencil_rectangles_mm':[list(x) for x in WINDOWS],
                   'area_mm2':round(area,6),'coverage_percent':round(100*area/a0,2),
                   'min_drill_edge_to_aperture_mm':min(res),
                   'holes_intersecting_windows':0,
                   'status':'COPERTURA_MOLTO_INFERIORE; MONTAGGIO_TERMICA_NON_VALIDATI'},
       'comparison':'Non selezionare B come soluzione produttiva senza approvazione; A richiede VIPPO e controllo stencil',
       'constraints':'2D nominale; nessuna tolleranza, reflow, pasta, spessore stencil, voiding, termica, KiCad DRC o qualifica.'
    }

def svg(data,out):
    pad=data['U101']['thermal_pad_bbox_mm']; paste=data['U101']['paste_bbox_mm']
    # plot locali in mm, scala 110 pixel/mm, pad visto frontalmente
    scale=95;X=75;Y=22
    x0,y0=pad[0],pad[1]
    def px(x):return round(X+(x-x0)*scale,3)
    def py(y):return round(Y+(y-y0)*scale,3)
    def rect(r,fill,stroke,dash=''):
        x1,y1,x2,y2=r
        return f'<rect x="{px(x1)}" y="{py(y1)}" width="{(x2-x1)*scale:.3f}" height="{(y2-y1)*scale:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" {dash}/>'
    left=[rect(pad,'#d8b783','#756342'), rect(paste,'#c98a55','#8a4f30')]
    right=[rect(pad,'#d8b783','#756342')]+[rect(r,'#58a1a4','#207078') for r in WINDOWS]
    holes=[]
    for v in data['vias']:
        cx,cy=px(v['x']),py(v['y']); rr=v['drill']/2*scale
        holes.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.2f}" fill="#fff" stroke="#4a362b" stroke-width="1.6"/>')
    content='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 455" width="650" height="455">
<rect width="650" height="455" fill="white"/>
<g font-family="DejaVu Sans,Arial,sans-serif" fill="#293846">
<text x="28" y="25" font-size="17" font-weight="bold">U101 / V5.0 — studio teorico dello stencil, NON CAM</text>
<text x="65" y="53" font-size="13">A. Apertura originale: 81%</text>
<text x="376" y="53" font-size="13">B. Due finestre: 29,7%</text>
</g>'''
    content+=f'<g transform="translate(0,47)">{"".join(left)}{"".join(holes)}</g>'
    content+=f'<g transform="translate(310,47)">{"".join(right)}{"".join(holes)}</g>'
    content+='''<g font-family="DejaVu Sans,Arial,sans-serif" font-size="12" fill="#293846">
<text x="35" y="423">Entrambe le opzioni sono NON APPROVATE: serve DFM, stencil, KiCad, termica e collaudo.</text>
<text x="35" y="439">Colori: rame ocra · apertura paste arancio/azzurro · fori bianchi. Quote nominali in mm.</text>
</g></svg>'''
    out.write_text(content,encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT)
    args=p.parse_args();src=json.loads((args.root/'03_Verifiche/V4.9/AUDIT_VIA_STENCIL_V4.9.json').read_text())
    result=compute(src)
    out=args.root/'03_Verifiche/V5.0'
    (out/'STUDIO_STENCIL_V5.0.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    svg(src,out/'CONFRONTO_STENCIL_U101_V5.0.svg')
    print('Baseline',result['option_A']['coverage_percent'],'%; dry-via study',result['option_B']['coverage_percent'],'%; gap',result['option_B']['min_drill_edge_to_aperture_mm'],'mm')
if __name__=='__main__':main()
