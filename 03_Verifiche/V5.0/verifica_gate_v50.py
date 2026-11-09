#!/usr/bin/env python3
"""Gate di fabbricazione fail-closed: verifiche mancanti => BLOCCATO.
Non esiste alcun percorso per creare Gerber, ordini o autorizzazioni automatiche.
"""
import hashlib, json, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REQUIRED={
'R-01':'ERC KiCad 10 nativo e report esaminato',
'R-02':'DRC KiCad 10 con refill/parita e report esaminato',
'R-03':'DXF/STEP TE CONSMA002-SMD-G confrontati e footprint approvato',
'R-04':'DFM PCBWay scritto per 6 VIPPO / rifinitura / tolleranze',
'R-05':'Approvazione assemblatore: stencil, reflow e ispezione U101',
'R-06':'Analisi e misura termica ADL5535',
'R-07':'Stack-up 4 strati / impedenza RF dimensionata',
'R-08':'BOM, procedure di banco e collaudi RX',
'R-09':'Autorizzazione esplicita per qualsiasi ordine e revisione esecutiva'}
REL='04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB.kicad_pcb'

def gate(root):
    p=root/REL
    assert p.is_file(),f'Sorgente PCB mancante: {p}'
    for q in ['06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf',
              '03_Verifiche/V4.9/AUDIT_VIA_STENCIL_V4.9.json']:
        assert (root/q).is_file(),f'Documento obbligatorio mancante: {q}'
    return {
        'version':'V5.0','policy':'FAIL_CLOSED',
        'source_pcb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
        'release_status':'BLOCKED_NOT_FOR_FAB',
        'fabrication_allowed':False,'TX_allowed':False,
        'native_erc':'NOT_RUN','native_drc':'NOT_RUN',
        'written_manufacturer_approval':'NOT_RECEIVED',
        'gate_items':[{'id':k,'requirement':v,'status':'OPEN','evidence':'NOT_PRESENT'} for k,v in REQUIRED.items()],
        'note':'Il superamento dei test statici e la presenza dei sorgenti non concedono autorizzazione.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT)
    args=p.parse_args();result=gate(args.root)
    path=args.root/'03_Verifiche/V5.0/GATE_RELEASE_V5.0.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Rilascio:',result['release_status'],'—',len(result['gate_items']),'gate aperti')
if __name__=='__main__':main()
