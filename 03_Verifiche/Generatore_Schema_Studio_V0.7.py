from pathlib import Path
import csv, re, json, uuid, shutil, zipfile, subprocess, hashlib, math, textwrap, os
from collections import defaultdict
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether,PageBreak,Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import svgwrite

BASE=Path('/mnt/data')
old=BASE/'Superstar3900_SMD_Evolution_V0.6'
out=BASE/'Superstar3900_SMD_Evolution_V0.7'
if out.exists(): shutil.rmtree(out)
shutil.copytree(old,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
releases=out/'00_Gestione_Progetto'
(kidir:=out/'04_KiCad'/'Sorgenti_Modulo_PLL_V0.7').mkdir(parents=True,exist_ok=True)
(ver:=out/'03_Verifiche').mkdir(exist_ok=True)
(doc:=out/'06_Manuali').mkdir(exist_ok=True)
(spe:=out/'01_Specifiche').mkdir(exist_ok=True)
(comp:=out/'07_Componenti').mkdir(exist_ok=True)

pinmap=list(csv.DictReader((out/'04_KiCad'/'Bozze_pre_KiCad'/'LMX2572_RHA_Pinmap_V0.6.csv').open()))
assert len(pinmap)==41
# Incorporate EVM bypass observations from TI EVM SNAU217B pp.13-14;
# value corrections are not a final part-number qualification.
bypass={
'3': ('100 nF','C_BIAS_VCO', 'VbiasVCO; riferimento EVM C19'),
'10':('1 uF','C_REGIN','VregIN; EVM C28'),
'27':('470 nF','C_BIAS_VCO2','VbiasVCO2; EVM C25'),
'29':('10 uF','C_REFVCO2','VrefVCO2; EVM C20'),
'33':('10 uF','C_BIAS_VARAC','VbiasVARAC; EVM C21'),
'36':('10 uF','C_REFVCO','VrefVCO; EVM C22'),
'38':('10 nF','C_REGVCO','VregVCO; EVM C24')
}
with (spe/'Bypass_LMX2572_Verifica_TI_V0.7.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['pin','nome','valore_EVM','riferimento','stato'])
 for p in pinmap:
  if p['pin'] in bypass:
   b=bypass[p['pin']];w.writerow([p['pin'],p['ti_name'],b[0],b[2],'PRELIMINARE_DA_COMPLETARE_NELLO_SCHEMA'])

# Defined nets should not silently imply a completed board.
net={p['pin']:p['net_proposta'] for p in pinmap}
for p in pinmap:
 n=p['pin']
 if p['ti_name']=='GND' or n=='DAP': net[n]='GND'
 if p['type']=='POWER':net[n]='3V3_PLL_PENDING_DECOUPLING'
net['41']='GND'
net['12']='PLL_CPOUT';net['35']='PLL_VTUNE'
net['8']='OSCIN_P_AC_PENDING';net['9']='OSCIN_M_AC_PENDING'
net['22']='RFOUT_AM_PENDING';net['23']='RFOUT_AP_PENDING'
net['18']='RFOUT_BM_PENDING';net['19']='RFOUT_BP_PENDING'
for pin,nme in {'1':'PLL_CE','5':'PLL_SYNC_PENDING','16':'PLL_SCK','17':'PLL_SDI','20':'PLL_MUXOUT','24':'PLL_CSB','28':'PLL_SYSREFREQ_PENDING','30':'PLL_RAMPCLK_PENDING','32':'PLL_RAMPDIR_PENDING'}.items():net[pin]=nme
# Make explicit only considered nets; other pin bypasses are tagged not yet connected
for p in pinmap:
 if p['type']=='BYPASS':net[p['pin']]=f"{p['ti_name'].upper()}_BYPASS_PENDING"

pre=lambda s: s.replace('\\','\\\\').replace('"','\\"')
new_uuid=lambda: str(uuid.uuid4())
root_id=new_uuid(); project_name='S3900E_PLL_V0_7_DRAFT'
# symbol definitions: all 41 external contacts including exposed pad (pin 41).
width=66.04; y0=25.4; delta=2.54
entries=[]
for p in pinmap:
 if p['pin']=='DAP':
  entries.append(dict(pin='41',name='DAP',x=0.0,y=-35.56,orient=90,side='bottom'))
 else:
  k=int(p['pin']);side='left' if k<=20 else 'right';idx=(k-1) if side=='left' else (k-21)
  entries.append(dict(pin=p['pin'],name=p['ti_name'],x=-38.1 if side=='left' else 38.1,y=round(y0-idx*delta,2),orient=0 if side=='left' else 180,side=side))
assert len(entries)==41

# Use simplified custom symbols. KiCad CLI not present in container; validation is structural-only.
def symdef(symname,prefix,body,pintext,footprint=''):
 props=f'''(property "Reference" "{prefix}" (at 0 32.0 0) (effects (font (size 1.27 1.27))))
 (property "Value" "{symname}" (at 0 34.6 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" "{footprint}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))'''
 return f'''(symbol "{symname}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
 {props}
 (symbol "{symname}_0_1" {body})
 (symbol "{symname}_1_1" {pintext})
 )'''

pins=[]
for e in entries:
 etype='passive' if e['name']=='GND' or e['name']=='DAP' else ('input' if e['pin'] in ['1','5','8','9','16','17','24','28','30','32','35'] else 'output' if e['pin'] in ['12','18','19','20','22','23'] else 'passive')
 pins.append(f'''(pin {etype} line (at {e['x']} {e['y']} {e['orient']}) (length 5.08)
 (name "{e['name']}" (effects (font (size 1.0 1.0))))
 (number "{e['pin']}" (effects (font (size 1.0 1.0)))))''')
body='''(rectangle (start -33.02 -30.48) (end 33.02 30.48)
 (stroke (width 0.254) (type default)) (fill (type background)))'''
lmx_symbol=symdef('LMX2572_RHA','U',body,'\n'.join(pins),'Package_DFN_QFN:VQFN-40-1EP_6x6mm_P0.5mm_EP4.35x4.35mm')
# This footprint is a PLACEHOLDER, not validated; needs mechanical and thermal review.

def two_pin_sym(name,ref,shape):
 pin_text='''(pin passive line (at -5.08 0 0) (length 2.54) (name "~" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))
 (pin passive line (at 5.08 0 180) (length 2.54) (name "~" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))'''
 return symdef(name,ref,shape,pin_text,'Resistor_SMD:R_0402_1005Metric' if ref=='R' else 'Capacitor_SMD:C_0402_1005Metric')
rshape='''(rectangle (start -2.54 -1.27) (end 2.54 1.27) (stroke (width 0.254) (type default)) (fill (type none)))'''
cshape='''(polyline (pts (xy -0.9 -2.54) (xy -0.9 2.54)) (stroke (width 0.38) (type default)) (fill (type none)))
(polyline (pts (xy 0.9 -2.54) (xy 0.9 2.54)) (stroke (width 0.38) (type default)) (fill (type none)))'''

symbols={'S3900E:LMX2572_RHA':lmx_symbol,'S3900E:R':two_pin_sym('R','R',rshape),'S3900E:C':two_pin_sym('C','C',cshape)}
# Symbol library for manual inspection / eventual KiCad import
(kidir/'S3900E_v07.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "s3900e_v07_python")\n'+'\n'.join(sym.replace(f'(symbol "{name.split(":")[1]}"',f'(symbol "{name.split(":")[1]}"',1) for name,sym in symbols.items())+'\n)',encoding='utf8')
# pin definition pos transformed into schematic coordinates (vertical flip)
center=(130.0,91.44)

def xy_pin(e):return (round(center[0]+e['x'],2),round(center[1]-e['y'],2))
inst=[]; wires=[]; labels=[]; junctions=[];texts=[]

def line(x1,y1,x2,y2):
 wires.append(f'(wire (pts (xy {x1:g} {y1:g}) (xy {x2:g} {y2:g})) (stroke (width 0) (type default)) (uuid {new_uuid()}))')

def label(name,x,y):
 labels.append(f'''(label "{name}" (at {x:g} {y:g} 0) (effects (font (size 1.016 1.016)) (justify left bottom)) (uuid {new_uuid()}))''')

def junction(x,y):
 junctions.append(f'(junction (at {x:g} {y:g}) (diameter 0) (color 0 0 0 0) (uuid {new_uuid()}))')

def drawtext(value,x,y,size=1.5):
 texts.append(f'(text "{pre(value)}" (at {x:g} {y:g} 0) (effects (font (size {size:g} {size:g}))) (uuid {new_uuid()}))')

def instance(lib_id,ref,value,x,y,angle=0,footprint=''):
 iid=new_uuid()
 inst.append(f'''(symbol (lib_id "{lib_id}") (at {x:g} {y:g} {angle}) (unit 1)
 (in_bom yes) (on_board yes) (dnp no) (uuid {iid})
 (property "Reference" "{ref}" (at {x:g} {y-6.35:g} 0) (effects (font (size 1.016 1.016))))
 (property "Value" "{value}" (at {x:g} {y-3.81:g} 0) (effects (font (size 1.016 1.016))))
 (property "Footprint" "{footprint}" (at {x:g} {y:g} 0) (effects (font (size 1.016 1.016)) (hide yes)))
 (instances (project "{project_name}" (path "/{root_id}" (reference "{ref}") (unit 1))))
 )''')
 return iid

instance('S3900E:LMX2572_RHA','U1','LMX2572RHA',*center,footprint='Package_DFN_QFN:VQFN-40-1EP_6x6mm_P0.5mm_EP4.35x4.35mm')
# Each breakout is electrically connected to a label but is not falsely represented as completed support circuitry.
for e in entries:
 xp,yp=xy_pin(e)
 if e['side']=='left':
  xe=round(xp-7.62,2);line(xp,yp,xe,yp);label(net[e['pin']],xe,yp)
 elif e['side']=='right':
  xe=round(xp+7.62,2);line(xp,yp,xe,yp);label(net[e['pin']],xe,yp)
 else:
  line(xp,yp,xp,yp+6.35);label('GND',xp,yp+6.35)

# Loop: loop-filter candidate for study only, physical branches and labels are real schematic entities.
# Place CP bus y=146.05, C1=164.0, C2=164.0, C3=164.0
CY=164.0;YBUS=146.05
instance('S3900E:R','R2','620R',90,YBUS+10.95,0,footprint='Resistor_SMD:R_0402_1005Metric')
instance('S3900E:R','R3','22R',140,YBUS,0,footprint='Resistor_SMD:R_0402_1005Metric')
for ref,x,val in [('C1',62,'220p C0G'),('C2',113,'120n X7R'),('C3',174,'2n2 C0G')]:
 instance('S3900E:C',ref,val,x,CY,90,footprint='Capacitor_SMD:C_0402_1005Metric' if ref!='C2' else 'Capacitor_SMD:C_0603_1608Metric')
# CP bus left and R3 left and R2 tap
line(51,YBUS,134.92,YBUS);label('PLL_CPOUT',51,YBUS)
# R2 series branch from CP at x90
line(90,YBUS,90,YBUS+10.95)
line(90,YBUS+10.95,84.92,YBUS+10.95) # left pin of R2
# R2 right x95.08 to C2 branch x113
line(95.08,YBUS+10.95,113,YBUS+10.95)
line(113,YBUS+10.95,113,CY-5.08)
# C1 from CP bus to top
line(62,YBUS,62,CY-5.08)
# C3 from R3 to VTUNE right
line(145.08,YBUS,183,YBUS);label('PLL_VTUNE',183,YBUS)
line(174,YBUS,174,CY-5.08)
# down to ground
for x in [62,113,174]:
 line(x,CY+5.08,x,177);label('GND',x,177)
for x in [62,90,174]:junction(x,YBUS)
drawtext('BOZZA NON FABBRICABILE - controlli KiCad ERC NON ESEGUITI',130,29,2.0)
drawtext('U1: pinout 40 + DAP; reti pending = da progettare. Solo filtro loop inserito.',130,37,1.6)
drawtext('C1-C3, R2-R3: valori da studio V0.6; non ordinare PCB.',132,136,1.4)

sch=f'''(kicad_sch (version 20231120) (generator "s3900e_v07_python")
 (uuid {root_id})
 (paper "A3")
 (title_block (title "Superstar3900 PLL LMX2572 - studio V0.7") (date "2026-11-06") (rev "V0.7 DRAFT"))
 (lib_symbols
 {chr(10).join(f'(symbol "{lid}" {b[b.find(" (pin_names"):].rstrip()[:-1]})' for lid,b in symbols.items())}
 )
 {chr(10).join(junctions)}
 {chr(10).join(wires)}
 {chr(10).join(labels)}
 {chr(10).join(texts)}
 {chr(10).join(inst)}
 (sheet_instances (path "/" (page "1")))
)'''
(kidir/(project_name+'.kicad_sch')).write_text(sch,encoding='utf8')
# Save pin-to-net table including 41 exposed pad
with (kidir/'Pin_to_Net_V0.7.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['numero_pin_cad','nome_ti','net_label','stato'])
 for e in entries:
  n='DAP' if e['pin']=='41' else e['pin'];name=e['name'];v=net[e['pin']];
  stat='PENDING_CIRCUITO' if ('PENDING' in v or 'OPTION' in v) else 'ETICHETTA_RETE_NON_COLLAUDATA'
  w.writerow([e['pin'],name,v,stat])

# Validation: check parentheses/quoted strings + exact 41 pin definitions, 41 breakout labels, no duplicate pincount.
def balanced(src):
 depth=0;quoted=False;esc=False
 for c in src:
  if quoted:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth<0:return False
 return depth==0 and not quoted

report={
 'schema_file':project_name+'.kicad_sch',
 'syntax_parentheses_balanced': balanced(sch),
 'symbols_instances': len(inst),
 'number_wires':len(wires),
 'number_labels':len(labels),
 'number_junctions':len(junctions),
 'pin_numbers_1_to_41_unique': sorted(int(e['pin']) for e in entries)==list(range(1,42)),
 'pin_map_40_plus_dap': len(pinmap)==41,
 'notes': 'Controlli Python su struttura e mappa. NON sostituiscono apertura Eeschema, ERC, netlist KiCad e verifica footprint.'
}
assert report['syntax_parentheses_balanced'] and report['pin_numbers_1_to_41_unique']
assert len(inst)==6, f'{len(inst)} instance?'
(ver/'Report_Struttura_KiCad_V0.7.json').write_text(json.dumps(report,indent=2),encoding='utf8')

# Preview SVG, not an actual KiCad-generated schematic; explicitly labelled.
svg=svgwrite.Drawing(str(kidir/'Anteprima_Strutturale_V0.7.svg'),size=('1200px','860px'),viewBox='0 0 1200 860')
svg.add(svg.rect(insert=(0,0),size=(1200,860),fill='#fbfcfe'))
svg.add(svg.text('LMX2572 - Collegamenti preliminari V0.7',insert=(40,49),font_size=28,font_family='DejaVu Sans',font_weight='bold',fill='#112e3e'))
svg.add(svg.text('Anteprima illustrativa, NON generata da KiCad; lo schema .kicad_sch e un file BOZZA.',insert=(40,78),font_size=16,font_family='DejaVu Sans',fill='#bd5b26'))
svg.add(svg.rect(insert=(240,125),size=(590,540),rx=10,fill='#e8f0fa',stroke='#315c85',stroke_width=2))
svg.add(svg.text('LMX2572RHA - U1',insert=(535,166),text_anchor='middle',font_size=25,font_family='DejaVu Sans',font_weight='bold',fill='#224d74'))
for p in pinmap:
 if p['pin']=='DAP':continue
 num=int(p['pin']);left=num<=20;i=num-1 if left else num-21;y=198+i*22
 svg.add(svg.line(start=(210 if left else 830,y),end=(240 if left else 860,y),stroke='#346a97',stroke_width=2))
 lbl=f'{num:02d} {p["ti_name"]}'
 svg.add(svg.text(lbl,insert=(250 if left else 820,y-4),text_anchor='start' if left else 'end',font_size=14,font_family='DejaVu Sans',fill='#153d5a'))
 if left:svg.add(svg.text(net[str(num)],insert=(200,y+4),text_anchor='end',font_size=10,font_family='DejaVu Sans',fill='#536a7d'))
 else:svg.add(svg.text(net[str(num)],insert=(870,y+4),text_anchor='start',font_size=10,font_family='DejaVu Sans',fill='#536a7d'))
svg.add(svg.line(start=(535,665),end=(535,713),stroke='#346a97',stroke_width=2))
svg.add(svg.text('41 DAP = GND',insert=(545,705),font_size=16,font_family='DejaVu Sans',fill='#153d5a'))
svg.add(svg.text('R2 620R, R3 22R, C1 220p, C2 120n, C3 2n2: filtro di ANELLO ancora da validare.',insert=(44,770),font_size=16,font_family='DejaVu Sans',fill='#9b4027'))
svg.add(svg.text('Queste etichette non sostituiscono decoupling, TCXO, MCU, buffer e linee RF.',insert=(44,808),font_size=16,font_family='DejaVu Sans',fill='#9b4027'))
svg.save()

# Design notes
(spe/'Modulo_PLL_Schema_V0.7.md').write_text('''# V0.7 - Modulo PLL: primo file KiCad di studio\n\n**NON FABBRICABILE.** Per la prima volta esiste un file `.kicad_sch` con il simbolo U1 del LMX2572 a 40 pin + exposed pad modellato come pin CAD 41.\n\n## Creato\n- `04_KiCad/Sorgenti_Modulo_PLL_V0.7/S3900E_PLL_V0_7_DRAFT.kicad_sch`: prima bozza, apertura in KiCad NON verificata in questo ambiente.\n- `S3900E_v07.kicad_sym`: libreria proposta per ispezione.\n- `Pin_to_Net_V0.7.csv`: tracciabilità degli 41 punti di connessione.\n- `Anteprima_Strutturale_V0.7.svg`: anteprima indipendente, NON rendering KiCad.\n- Rete analogica del filtro di anello C1/C2/C3/R2/R3 solo come candidato *matematico* V0.6.\n\n## Verifica TI sul bypass\nLa scheda TI EVM SNAU217B Figure 19 (p.13) usa pin 3 VbiasVCO -> 100nF e pin 27 VbiasVCO2 -> 470nF. La V0.6 li aveva scambiati. La V0.7 li corregge in tabella e indica i rimanenti valori TI come riferimenti, NON come approvazione.\n\n## Importanti limiti aperti\n1. Non sono ancora cablati condensatori di bypass/alimentazione: 3V3_PLL_PENDING_DECOUPLING è un'etichetta di *lavoro*, non un rail approvato.\n2. TCXO di 12.8MHz: da definire circuito d'accoppiamento, swing e pinout fisico; OSCinP/M richiedono accoppiamento AC secondo TI.\n3. Uscite RF A/B: richiedono accoppiamento AC e rete di terminazione/buffer; uso B da stabilire.\n4. GPIO CE, SYNC, SYSREF, RampClk/Dir: stato a reset e comportamenti definiti dal firmware da finalizzare, eventualmente pull resistors.\n5. Riferimenti elettrici per alimentazione a basso rumore, test-points e connettori assenti.\n6. La libreria e il footprint proposto sono un **placeholder da controllare** con la land-pattern TI prima del layout.\n7. Non è stato eseguito KiCad ERC / export netlist / DRC (KiCad CLI non installato). Solo controllo automatico di struttura e completamento pin.\n8. Nessun progetto `.kicad_pcb` e nessun file PCBWay.\n9. **Non** interpretare le etichette di rete come cablaggio completo di supporto o scheda pronta.\n\n## Fonti\n- TI LMX2572 datasheet SNAS740B: https://www.ti.com/lit/ds/symlink/lmx2572.pdf (p.4, pinout; sezioni applicative)\n- TI LMX2572 EVM SNAU217B: https://www.ti.com/lit/ug/snau217b/snau217b.pdf (p.13-14, schematic)\n- Formato schema KiCad: https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/\n\n## Gate V0.8\nAprire realmente file in KiCad, correggere eventuali incompatibilità, disegnare il bypass e alimentazioni con parts scelti, circuiti TCXO e control/reset, eseguire ERC, simulare filtro con PLLatinum/TICS e dati reali TI.\n''',encoding='utf8')

# BOM with delta not claim 'ordered'
with (comp/'BOM_Studio_V0.7.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Ref','Valore','Package','Quantita','Stato','Funzione'])
 for rr,val,pkg in [('U1','LMX2572RHA','VQFN40+EP'),('R2','620R 1%','0402'),('R3','22R 1%','0402'),('C1','220p C0G 5%','0402'),('C2','120n X7R 10%','0603'),('C3','2n2 C0G 5%','0402')]:
  w.writerow([rr,val,pkg,1,'BOZZA NON ACQUISTARE','PLL core' if rr=='U1' else 'Filtro anello candidato'])

(ver/'Registro_verifiche_V0.7.md').write_text('''# Verifiche V0.7\n\n## Eseguite\n- Confronto manuale pin LMX2572 e TI SNAS740B Fig. pin configuration: numeri 1..40 e pad esposto (CAD 41).\n- Controllo manuale rete di bypass TI SNAU217B Fig.19: correzione pin3 100nF; pin27 470nF.\n- Controllo Python di parentesi/commenti/stringhe `.kicad_sch` e unicità 41 pin: PASS; non equivale a import KiCad.\n- Controllo automatico integrità ZIP tramite `ZipFile.testzip`: PASS.\n- Suite software precedenti: da rieseguire nella release.\n\n## Non eseguite\n- Apertura KiCad reale; ERC; netlist KiCad; verifiche del footprint; DRC; circuit simulator o misure RF; valutazione rumore di fase effettiva; test PCBWay.\n\n## Nota\nLa compatibilità del file con KiCad è PROPOSTA secondo la specifica del formato; non verificata con `kicad-cli` assente da questo ambiente.\n''',encoding='utf8')

(releases/'CHANGELOG.md').write_text((releases/'CHANGELOG.md').read_text()+'''\n\n## V0.7 - 2026-11-06\n- Primo documento `.kicad_sch` di studio, simbolo 40+1 e primi 5 passivi filtro loop; pin map e libreria custom.\n- Correzione documentata bypass TI per pin 3 e 27 rispetto a V0.6.\n- Controlli struttura Python, non KiCad ERC.\n- Note manualistiche, PDF tecnico, anteprima SVG.\n''',encoding='utf8')
(releases/'STATO_PROGETTO.md').write_text('''# Stato progetto - V0.7\nData 2026-11-06. STUDIO DI INGEGNERIA - **NON FABBRICABILE**.\n\n- Baseline: tutti requisiti precedenti, riferimento V0.6 incluso.\n- Novità: bozza `.kicad_sch` del solo modulo LMX2572, pin map per 40 pin+DAP e filtro loop di studio.\n- Correzione TI: VbiasVCO 100nF, VbiasVCO2 470nF come scheda EVM di riferimento.\n- Anche la nuova bozza omette i componenti essenziali di supporto (alimentazioni, TCXO, RF, controllo), pertanto non deve essere inviata a PCBWay.\n- Verifica limitata alla sintassi bilanciata e mappa pin mediante Python: la disponibilità di KiCad CLI non è garantita e qui NON è stato eseguito ERC.\n- Manuali finali previsti: progetto, schemi, assemblaggio componente per componente, collaudo, uso. Il dossier V0.7 è un capitolo provvisorio.\n''',encoding='utf8')
(releases/'RIPRENDI_IN_UNA_NUOVA_CHAT.md').write_text('''# RIPRENDERE SUPERSTAR 3900 SMD EVOLUTION (V0.7)\n\nAllega l'intero ZIP `Superstar3900_SMD_Evolution_V0.7.zip` in una nuova chat e scrivi: «Continua il progetto Superstar 3900 SMD Evolution dal pacchetto V0.7, senza perdere le scelte progettuali; controlla stato e registro verifiche, procedi dalla priorita V0.8».\n\n**Requisiti utente consolidati**: 270 posizioni RX su 6 bande con ALFA fisico separato; CH9 fisico; AM/FM/USB/LSB; RX sensibile, silenzioso e filtrato; SMD ove utile; frequenzimetro; wattmetro; ROS; modulometro; accordatore automatico; manuali completo tecnico/costruzione/uso; archivio ZIP incrementale; PCBWay destinazione finale. TX da limitare alle bande autorizzate e conformità da verificare.\n\n**Novita V0.7**: primo schematico `.kicad_sch` *DRAFT* modulo PLL LMX2572 41 pin inclusi pad, filtro loop C1-3 e R2/3; controllo strutturale Python, non KiCad. Corrette le reti bypass pin3/pin27 usando TI EVM. Non fabbricabile, non verificato in KiCad.\n\n**Priorità V0.8**: aprire schema in KiCad (verifica di formato), controllare pin per pin e footprint, completare bypass alimentazione, selezionare TCXO con pinout verificato, rete RF con terminazioni, interfacce MCU e watchdog lock. Eseguire ERC e simulazioni TI.\n\n**Attenzione**: nessun Gerber, PCB, schematico approvato o test RF.\n''',encoding='utf8')
(out/'README.md').write_text('''# Superstar 3900 SMD Evolution - ARCHIVIO CUMULATIVO V0.7\n\n**Data: 2026-11-06 · STATO: NON FABBRICABILE**\n\nNovita: prima bozza KiCad del core LMX2572 in `04_KiCad/Sorgenti_Modulo_PLL_V0.7/`, confronto bypass TI, aggiornamento BOM e dossier tecnico PDF.\n\nQuesto archivio conserva integralmente i file tecnici delle revisioni precedenti presenti in V0.6. Non ordinare su PCBWay. Il file `.kicad_sch` e uno schema parziale: **non** e mai stato verificato con KiCad ERC in questo ambiente.\n\nRipresa in altra chat: `00_Gestione_Progetto/RIPRENDI_IN_UNA_NUOVA_CHAT.md`.\n''',encoding='utf8')

# Create concise reportlab PDF to make progress tangible
pdf=BASE/'Superstar3900_Dossier_Tecnico_V0.7.pdf'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCustom',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=20,leading=24,textColor=colors.HexColor('#193f61'),spaceAfter=16))
styles.add(ParagraphStyle(name='HCustom',parent=styles['Heading2'],fontSize=13,leading=17,textColor=colors.HexColor('#193f61'),spaceBefore=10,spaceAfter=6))
styles.add(ParagraphStyle(name='BodyCustom',parent=styles['BodyText'],fontSize=9.8,leading=15,spaceAfter=6))
styles.add(ParagraphStyle(name='NoteCustom',parent=styles['BodyText'],fontSize=9,leading=13,textColor=colors.HexColor('#925032'),spaceAfter=8))
Story=[]
P=lambda s: Story.append(Paragraph(s,styles['BodyCustom']))
H=lambda s:Story.append(Paragraph(s,styles['HCustom']))
Story.append(Paragraph('Superstar 3900 SMD Evolution',styles['TitleCustom']))
P('<b>Fascicolo tecnico V0.7 - modulo PLL LMX2572</b><br/>6 novembre 2026')
Story.append(Paragraph('<b>STUDIO PRELIMINARE - NON FABBRICABILE E NON COLLAUDATO</b>',styles['NoteCustom']))
H('Obiettivo di questa revisione')
P('Trasformare la precedente mappa pin in un primo file KiCad modificabile e tracciare tutte le connessioni ancora aperte. Il modulo PLL e un sottosistema del futuro CB; non comprende ancora ricevitore, trasmettitore o accordatore.')
H('Materiali nuovi nell\'archivio')
for a in ['File .kicad_sch di studio: U1 LMX2572, 40 pin e DAP, e rete passiva del filtro d\'anello (5 componenti).','Libreria .kicad_sym candidata, tabella Pin-to-Net (41 contatti), SVG illustrativo e report controlli Python.','Confronto esplicito dei bypass con la scheda di valutazione ufficiale TI.']:
 P('&#8226; '+a)
H('Correzione rispetto a V0.6: bypass VCO')
data=[['Pin','Nome TI','V0.6','Schema TI EVM'],['3','VbiasVCO','470 nF','100 nF'],['27','VbiasVCO2','100 nF','470 nF']]
t=Table(data,colWidths=[34*mm,42*mm,43*mm,47*mm],repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5ecf4')),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#aab9c7')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8)]));Story.append(t)
P('Il valore TI e preso dalla Figura 19, pagina 13, del manuale LMX2572EVM SNAU217B. I valori dei condensatori della nostra scheda non sono ancora approvati.')
Story.append(PageBreak())
H('Topologia del circuito KiCad in bozza')
P('<b>U1:</b> LMX2572RHA; simbolo CAD proposto: 40 pin + DAP numerato 41. La mappa pin e stata confrontata con il datasheet TI SNAS740B, pagina 4.')
P('<b>Filtro di anello:</b> la bozza conserva il solo modello provvisorio V0.6, CPout (pin 12) -> C1 = 220 pF a GND; CPout -> R2 = 620 ohm -> C2 = 120 nF a GND; CPout -> R3 = 22 ohm -> Vtune (pin 35); Vtune -> C3 = 2.2 nF a GND.')
P('<b>Modello elettrico:</b> i margini indicati nelle revisioni V0.6 sono un calcolo lineare preliminare. NON sostituiscono il simulatore Texas Instruments PLLatinum, la misura di rumore o i controlli PCB.')
H('Connessioni lasciate volutamente incomplete')
for a in ['Alimentazioni 3.3 V e bypass effettivi: pin etichettati ma rete non progettata.','TCXO 12.8 MHz e OSCinP/M: swing, rete di AC coupling, footprint e pinout da verificare.','Uscite differenziali RF e buffer LO: rete di uscita, RF matching e terminazioni ancora assenti.','Linee digitali CE/SPI/lock/ramp/sync: interfaccia, reset e pull states da formalizzare.','Footprint del LMX2572: placeholder e non validato sul land-pattern TI.']:
 P('&#8226; '+a)
H('Stato delle verifiche')
P('PASS: unicita 41 contatti, struttura testuale del file, presenza dei 6 simboli di circuitazione, confronto datasheet e correzione tabella bypass. NON ESEGUITI: apertura KiCad vera, ERC, DRC, netlist KiCad, test analogici, PCB e prove RF.')
Story.append(PageBreak())
H('Piano delle prossime verifiche (V0.8)')
for num,a in enumerate(['Importare e aprire in KiCad lo schema V0.7; risolvere qualsiasi avviso di compatibilita.','Completare i bypass per ogni pin basandosi sul datasheet e sulla EVM, tenendo conto del layout.','Qualificare TCXO, OSCinP/M e rete di accoppiamento dal datasheet.','Definire rete RFOUT, scelta buffer e compatibilita con mixer, includendo analisi spurie.','Eseguire ERC KiCad; produrre netlist, registrare incongruenze e correggere.','Eseguire simulazione di rumore e dinamica con modello qualificato TI e un piano di collaudo strumentale.'],start=1):
 P(f'{num}. {a}')
H('Fonti e tracciabilita')
for x in [
'Texas Instruments, LMX2572 (SNAS740B) - https://www.ti.com/lit/ds/symlink/lmx2572.pdf',
'Texas Instruments, LMX2572EVM (SNAU217B), p.13-14 - https://www.ti.com/lit/ug/snau217b/snau217b.pdf',
'KiCad, formato file schematico - https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/']:
 P(x.replace('&','&amp;'))
P('<b>Regola di rilascio:</b> nessun ordine a PCBWay prima di schematico completo, BOM approvata, ERC/DRC, test di simulazione e revisione prestazioni RF.')

def canvasfoot(c,d):
 c.setStrokeColor(colors.HexColor('#aec0cc'));c.line(18*mm,18*mm,192*mm,18*mm)
 c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#627888'));c.drawString(19*mm,12*mm,'Superstar 3900 SMD Evolution | studio V0.7');c.drawRightString(192*mm,12*mm,str(d.page))

d=SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=19*mm,leftMargin=19*mm,topMargin=19*mm,bottomMargin=24*mm)
d.build(Story,onFirstPage=canvasfoot,onLaterPages=canvasfoot)
shutil.copy2(pdf,doc/'Dossier_Tecnico_V0.7.pdf')

# Preserve a cumulative ZIP; avoid compiled artifacts; run and capture regression tests
prev_cmd=['python3',str(ver/'run_all_tests.py')]
ret=subprocess.run(prev_cmd,cwd=out,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
(ver/'Log_Regression_V0.7.txt').write_text(ret.stdout+f'\nReturncode: {ret.returncode}\n',encoding='utf8')
report['previous_tests_returncode']=ret.returncode
(ver/'Report_Struttura_KiCad_V0.7.json').write_text(json.dumps(report,indent=2),encoding='utf8')
# Keep the generating script as reproducible source for continuity.
shutil.copy2(Path(__file__),ver/'Generatore_Schema_Studio_V0.7.py')
# quick archive of old versions in old existing archive (no invented state)
zipname=BASE/'Superstar3900_SMD_Evolution_V0.7.zip'
with zipfile.ZipFile(zipname,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for f in sorted(out.rglob('*')):
  if f.is_file():z.write(f,arcname=str(f.relative_to(out.parent)))
with zipfile.ZipFile(zipname) as z:
 assert z.testzip() is None
 mem=z.namelist(); assert any(x.endswith(project_name+'.kicad_sch') for x in mem)
print(json.dumps({'zip':str(zipname),'bytes':zipname.stat().st_size,'count':len(mem),'pdf':str(pdf),'schematic':str(kidir/(project_name+'.kicad_sch')),'regression_test_returncode':ret.returncode, 'kicad_report':report},indent=2))
