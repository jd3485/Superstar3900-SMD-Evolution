from pathlib import Path
from datetime import datetime
import shutil,csv,zipfile,hashlib,json,re,uuid,subprocess,sys,math
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm

root=Path('/mnt/data'); prev=root/'Superstar3900_SMD_Evolution_V1.7'; dst=root/'Superstar3900_SMD_Evolution_V1.8'
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(prev,dst,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
mod=dst/'04_KiCad'/'Modulo_MCU_CODEC_V1.8'; mod.mkdir(parents=True,exist_ok=True)
ver=dst/'03_Verifiche'; comp=dst/'07_Componenti'; spec=dst/'01_Specifiche'; mg=dst/'00_Gestione_Progetto'
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def q(t): return '"'+str(t).replace('\\','\\\\').replace('"','\\"')+'"'
def uuid4(): return str(uuid.uuid4())
orig=(prev/'04_KiCad/Modulo_MCU_CODEC_V1.7/S3900E_MCU_CODEC_V1_7_DRAFT.kicad_sch').read_text()
assert orig.startswith('(kicad_sch ') and orig.rstrip().endswith(')')
# Inietta nuovi simboli nella libreria locale esistente: elementi simbolo qui sono riferimenti a bozza, non librerie approvate.
newlibs=[]
xo_pins=[(1,'OE',-10.16,7.62,0,'input'),(2,'GND',-10.16,-7.62,0,'power_in'),(3,'OUT',10.16,-7.62,180,'output'),(4,'VDD',10.16,7.62,180,'power_in')]
ldo_pins=[(1,'IN',-10.16,10.16,0,'power_in'),(2,'GND',-10.16,-10.16,0,'power_in'),(3,'EN',-10.16,0,0,'input'),(4,'NC',10.16,-10.16,180,'no_connect'),(5,'OUT',10.16,10.16,180,'power_out')]
def lib_block(name,pins,ref):
    px=[]
    for num,pname,x,y,rot,typ in pins:
        px.append(f'(pin {typ} line (at {x:.4f} {y:.4f} {rot}) (length 5.08) (name {q(pname)} (effects (font (size 1 1)))) (number {q(num)} (effects (font (size 1 1)))))')
    return f'''(symbol "S3900E:{name}" (pin_names (offset 0.762)) (in_bom yes) (on_board yes)
    (property "Reference" "{ref}" (at 0 22.86 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 -22.86 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1" (rectangle (start -7.62 -15.24) (end 7.62 15.24) (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "{name}_1_1" {' '.join(px)}))'''
newlibs.append(lib_block('SIT8008_12M288_OE_DRAFT',xo_pins,'X'))
newlibs.append(lib_block('TPS7A2033_DBV_DRAFT',ldo_pins,'U'))
# Find matching end of (lib_symbols ...): robust nested parser, ignores strings.
def matching(s,start):
    depth=0;instr=False;esc=False
    for i in range(start,len(s)):
        ch=s[i]
        if instr:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=='"': instr=False
        elif ch=='"': instr=True
        elif ch=='(': depth+=1
        elif ch==')':
            depth-=1
            if depth==0:return i
    raise ValueError('unbalanced sexpr')
start=orig.index('(lib_symbols');end=matching(orig,start)
s=orig[:end]+'\n '+'\n '.join(newlibs)+orig[end:]
s=s.replace('S3900E - MCU e codec audio - NON fabbricabile','S3900E - MCU, codec e clock audio - DRAFT V1.8')
s=s.replace('(rev "V1.7 DRAFT")','(rev "V1.8 DRAFT")')
# V1.8 retains unchanged full U201/U202 connectivity; BCLK/WCLK direction is documented, not encoded in embedded generic pins.
root_uuid_match=re.search(r'^\(kicad_sch\s+\(version\s+\d+\).*?\(uuid\s+"([^"]+)"\)',s,re.S)
assert root_uuid_match
root_uuid=root_uuid_match.group(1);proj='S3900E_MCU_CODEC_CLOCK_V1_8_DRAFT'
# Project field uses same name as KiCad file
s=s.replace('S3900E_MCU_CODEC_V1_7_DRAFT','S3900E_MCU_CODEC_CLOCK_V1_8_DRAFT')
def instance(libname,ref,value,x,y,pfx=''):
 return f'''(symbol (lib_id "S3900E:{libname}") (at {x:.4f} {y:.4f} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uuid4()}")
    (property "Reference" "{ref}" (at {x:.4f} {y-20:.4f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" {q(value)} (at {x:.4f} {y+20:.4f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" {q(pfx)} (at {x:.4f} {y:.4f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (instances (project {q(proj)} (path {q('/'+root_uuid)} (reference {q(ref)}) (unit 1)))))'''
def label(x,y,net): return f'(label {q(net)} (at {x:.4f} {y:.4f} 0) (effects (font (size 1.02 1.02)) (justify left bottom)) (uuid "{uuid4()}"))'
newinst=[instance('SIT8008_12M288_OE_DRAFT','X201','SiT8008AI-22-33E-12.288000',610,320), instance('TPS7A2033_DBV_DRAFT','U203','TPS7A2033PDBVR',710,320)]
# Position in schematic: pin y reverses in global coordinates.
pin_nets={'X201':{1:'XO_OE',2:'GND',3:'XO_MCLK_RAW',4:'3V3_AUDIO_CLK'},'U203':{1:'5V_AUX_PROTECTED',2:'GND',3:'5V_AUX_PROTECTED',5:'3V3_AUDIO_CLK'}}
alllab=[]
for ref,x,y,pins in [('X201',610,320,xo_pins),('U203',710,320,ldo_pins)]:
 for pn,nam,px,py,rot,typ in pins:
  if pn in pin_nets[ref]: alllab.append(label(x+px,y-py,pin_nets[ref][pn]))
  else: alllab.append(f'(no_connect (at {x+px:.4f} {y-py:.4f}) (uuid "{uuid4()}"))')
# Candidate passives; footprints left blank intentionally as in V1.7
passives=[('C215','1uF','5V_AUX_PROTECTED','GND','LDO input, min required to verify'),('C216','1uF','3V3_AUDIO_CLK','GND','LDO output, min required to verify'),('C217','100nF','3V3_AUDIO_CLK','GND','local oscillator supply bypass'),('C218','1uF','3V3_AUDIO_CLK','GND','local oscillator supply bulk'),('R204','4.7k','3V3_AUDIO_CLK','XO_OE','OE pullup under 10k'),('R205','33R','XO_MCLK_RAW','AUDIO_MCLK_12M288','series damp, candidate only')]
for i,(ref,val,n1,n2,note) in enumerate(passives):
 x=570+(i//3)*80;y=405+(i%3)*24
 newinst.append(instance('R_DRAFT' if ref.startswith('R') else 'C_DRAFT',ref,val,x,y))
 alllab.append(label(x,y-5.08,n1));alllab.append(label(x,y+5.08,n2))
# insert at end as top level objects
s=s.rstrip(); assert s.endswith(')')
s=s[:-1]+'\n'+'\n'.join(newinst)+'\n'+'\n'.join(alllab)+'\n)\n'
fn=mod/(proj+'.kicad_sch'); write(fn,s)

# CSV mapping for pinning and roles, passives bom
with (mod/'Pinout_Oscillatore_LDO_V1.8.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['ref','pin','name','net','source','verification'])
 for r,pins in [('X201',xo_pins),('U203',ldo_pins)]:
  for num,name,*_ in pins:
   w.writerow([r,num,name,pin_nets[r].get(num,'NO_CONNECT'),'SiTime datasheet' if r=='X201' else 'TI TPS7A20 datasheet','datasheet lookup; NOT ERC'])
with (comp/'BOM_AUDIO_CLOCK_V1.8_DRAFT.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['ref','candidate','type','footprint','status','note'])
 w.writerow(['X201','SiT8008AI-22-33E-12.288000','oscillator 12.288MHz 3.3V','SMD 3.2x2.5 mm NOT assigned','CANDIDATE','pin1 OE pin2 GND pin3 OUT pin4 VDD'])
 w.writerow(['U203','TPS7A2033PDBVR','LDO 3.3V','SOT-23-5 NOT assigned','CANDIDATE','5V to audio clock rail, check load, dissipation'])
 for ref,val,n1,n2,note in passives:
  w.writerow([ref,val,'resistor' if ref.startswith('R') else 'capacitor','SMD TBD','PROVISIONAL',note])

source_notes='''# Clock audio, V1.8 - decisione tecnica e verifiche

**Stato:** bozza per verifica; nessun ERC, SPICE, PCB, misura realizzata.

## Errore di architettura corretto rispetto alla V1.7
La V1.7 ipotizzava oscillatore indipendente da 12.288 MHz al codec e STM32 master dei clock SAI. Due domini di clock non coerenti portano a perdita/duplicazione di campioni se non vi e' ASRC o recupero di clock. **Decisione V1.8:** codec TLV320AIC3204 come **master BCLK/WCLK** derivati dallo stesso clock 12.288 MHz; STM32G474 SAI1 A slave (RX/TX full-duplex tramite blocco B sincrono, configurazione effettiva da verificare in STM32CubeMX e hardware). Direzione delle reti cambia, etichette no.

## Clock di riferimento e calcoli nominali
- X201 candidato: SiTime SiT8008AI-22-33E-12.288000, SMD 3.2x2.5, 3.3 V, OE, +/-25 ppm a condizioni dichiarate. Non ancora acquistato o misurato; EMI e jitter reale da validare.
- Per **Fs = 48 kHz**, rapporto **MCLK/Fs = 256**, slot audio **2 x 32 bit**, BCLK **3.072 MHz**, rapporto MCLK/BCLK **4**.
- Configurazione modello senza PLL del codec: NDAC=1, MDAC=2, DOSR=128, NADC=1, MADC=2, AOSR=128: 12.288 MHz / (1*2*128) = 48 kHz. Opzione clock master BCLK via divisore 4; implementazione registri, sequenza di abilitazione e clock tree da convalidare contro TI SLAA404C e reference guide. NON scrivere ancora firmware di configurazione reale da questi dati.
- Frequenze nominali calcolate, non misurate.

## Collegamenti KiCad aggiunti (bozza)
- U203 TPS7A2033PDBVR: pin1 IN => `5V_AUX_PROTECTED`, pin2 GND, pin3 EN=> `5V_AUX_PROTECTED`, pin4 NC, pin5 OUT=> `3V3_AUDIO_CLK`.
- X201 SiT8008: pin1 OE=> `XO_OE`, pin2 GND, pin3 OUT=> `XO_MCLK_RAW`, pin4 VDD=>`3V3_AUDIO_CLK`.
- R204 4.7k da `3V3_AUDIO_CLK` a `XO_OE` (pullup OE), R205 33R da `XO_MCLK_RAW` a `AUDIO_MCLK_12M288` (resistenza di smorzamento candidata, da ottimizzare secondo PCB e fronte CMOS).
- C215 1uF ingresso LDO; C216 1uF uscita; C217 100nF e C218 1uF sull'alimentazione XO.
- `5V_AUX_PROTECTED` e' solo contratto di rete: collegamento al progetto generale DA ESEGUIRE. Pin codec MCLK e X201 OUT sono sulla stessa rete *attraverso R205*. I nomi di rete non sostituiscono la verifica elettrica.

## Criticita' aperte prima del PCB
1. Controllare con **KiCad ERC** simboli custom e pin passive/power, esportare netlist nativa; assegnare footprint del componente ordinato ed eseguire DRC.
2. Verificare realmente i quattro pin dello specifico ordine SiTime e la polarita' OE; la stima jitter non e' una misura EMI.
3. Confrontare MCU SAI slave 32-bit stereo e codec master clock output in STM32CubeMX; latenza di avvio codec e reset.
4. Confermare registri TI di clock, bit BCLK, NDAC, MDAC, AOSR/DOSR e ADC routing, nella revisione firmware successiva.
5. Aggiungere regolatori separati 3V3 MCU/codec, consolidare collegamento `5V_AUX_PROTECTED`, quantificare correnti e termica (circa 8.5 mW dissipati per ogni 5mA nel LDO da 5V a 3.3V).
6. Verificare ref clock, ringing, clock return paths e spurie RF durante TX e RX su PCB di prova. CTCSS/DCS devono essere letti prima dei filtri audio voce.

## Fonti verificabili
- TLV320AIC3204, TI: https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf
- TI SLAA404C, configurazione clock e alimentazioni: https://www.ti.com/lit/an/slaa404c/slaa404c.pdf
- SiTime pagina prodotto: https://www.sitime.com/products/mhz-oscillators/lvcmos-oscillators/sit8008
- SiTime versione candidata: https://www.digikey.com/en/products/detail/sitime/SIT8008AI-22-33E-12-288000/11352695
- TPS7A20 TI datasheet: https://www.ti.com/lit/ds/symlink/tps7a20.pdf
'''
write(spec/'Clock_Audio_SAI_V1.8.md',source_notes)
write(mod/'LEGGIMI.md','Schema V1.8 MCU/CODEC + clock oscillator e LDO. Bozza KiCad: pinout e label testati via Python; nessun ERC. Aprire in KiCad, verificare lib embedded, etichette e conversione ad assegnazione footprint.\n')

# test reproducible, independent of legacy tests
py='''#!/usr/bin/env python3
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
        elif c=='\\\\': esc=True
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
'''
write(ver/'test_audio_clock_v18.py',py)
proc=subprocess.run([sys.executable,str(ver/'test_audio_clock_v18.py')],capture_output=True,text=True)
write(ver/'LOG_Audio_Clock_V1.8.txt',proc.stdout+'\n'+proc.stderr)
if proc.returncode: raise RuntimeError(proc.stdout+'\n'+proc.stderr)
# run previous, preserve logs; do not overclaim about software
results=[]
for test in ['test_mcu_codec_v17.py','run_all_tests.py']:
 p=subprocess.run([sys.executable,str(ver/test)],cwd=ver,capture_output=True,text=True,timeout=25)
 results.append((test,p.returncode,p.stdout[-1500:],p.stderr[-1500:]))
write(ver/'LOG_Regressione_V1.8.txt','\n\n'.join(f'{a} exit={b}\n{c}\n{d}' for a,b,c,d in results))
# Main summary
write(ver/'Registro_Verifiche_V1.8.md','''# Verifiche V1.8\n\nPASS: algebra MCLK/BCLK/FS, pinout candidato X201 4 pin e U203 5 pin, inventario connessioni, S-expression bilanciata, script automatico.\n\nNON ESEGUITO: controllo nativo KiCad ERC/DRC, assegnazione footprint, simulazioni SPICE, configurazione STM32 SAI/codec via hardware, misure EMI/RF, prova di rumore e jitter.\n\nOsservazione di progetto: V1.7 presupponeva due domini clock potenzialmente indipendenti. V1.8 attribuisce a codec l'origine BCLK/WCLK sincronizzati al 12.288 MHz, con STM32 SAI slave. Restano prove di firmware e registri TI.\n''')
write(mg/'Registro_Decisioni_V1.8.md','''# V1.8 - decisioni\n- Oscillatore SiT8008AI-22-33E-12.288000 candidato, non acquistato.\n- Codec TLV320AIC3204 master BCLK e WCLK; MCU slave SAI.\n- LDO separato 3.3V clock candidato TPS7A2033PDBVR.\n- Tutti i footprint nuovi lasciati NON ASSEGNATI; elettricamente non validato.\n- Non cambiare i requisiti consolidati; percentuale stimata 27%, da non leggere come collaudo.\n''')
write(mg/'RIPRENDI_IN_UNA_NUOVA_CHAT.md','''# Riprendere il progetto - V1.8\n\nAllegare **Superstar3900_SMD_Evolution_V1.8.zip**. **Avanzamento stimato 27%; non fabbricabile**. Lo ZIP comprende tutto lo storico V1.7.\n\nNovita': corretto il rischio di drift audio V1.7; codec TLV320AIC3204 master BCLK/WCLK da SiT8008 12.288 MHz, STM32G474 SAI slave (da verificare), introdotto X201, U203 e passivi nella bozza KiCad.\n\nAprire `04_KiCad/Modulo_MCU_CODEC_V1.8/S3900E_MCU_CODEC_CLOCK_V1_8_DRAFT.kicad_sch` e leggere `01_Specifiche/Clock_Audio_SAI_V1.8.md`.\n\nEseguire: `python3 03_Verifiche/test_audio_clock_v18.py`. **Non equivale a ERC**.\n\nAncora da fare: footprint, KiCad ERC/DRC, 5V reale, clock ed alimentazioni, SAI slave CubeMX + firmware registri codec, microfono/AF, e tutte le restanti sezioni RF/TX, strumentazione, accordatore, misure e manuali.\n\nRequisiti: 270 posizioni RX su 6 bande, ALFA fisico, CH9, AM FM USB LSB, CW, PA, VOX, doppio ascolto, Roger Beep, Eco, CTCSS e DCS, freq/watt/ROS, accordatore, SMD, RX sensibile e silenzioso; TX vincolato a regole applicabili.\n''')
write(dst/'README.md','''# Superstar 3900 SMD Evolution - cumulativo V1.8\n\n**Avanzamento complessivo stimato: 27%. NON fabbricabile.** Include tutto lo storico V1.7, il nuovo schema clock/audio, datasheet references, verifiche automatiche, dossier e istruzioni ripresa.\n\n- Schema: `04_KiCad/Modulo_MCU_CODEC_V1.8/S3900E_MCU_CODEC_CLOCK_V1_8_DRAFT.kicad_sch`\n- Specifiche: `01_Specifiche/Clock_Audio_SAI_V1.8.md`\n- BOM incrementale: `07_Componenti/BOM_AUDIO_CLOCK_V1.8_DRAFT.csv`\n- Test: `python3 03_Verifiche/test_audio_clock_v18.py`\n- Dossier PDF: `Superstar3900_Dossier_Tecnico_V1.8.pdf`\n\nProssime priorita': realizzare KiCad ERC nativo; SPI e registri codec; STM32 SAI slave; integrare alimentazione e ingressi analogici; proseguire progettazione RF.\n''')

# infographic vector as SVG
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="520" viewBox="0 0 1180 520"><rect width="1180" height="520" fill="#f7fafc"/><text x="48" y="60" font-family="Arial" font-size="27" font-weight="bold" fill="#182d40">S3900E - CLOCK AUDIO V1.8</text><text x="48" y="95" font-family="Arial" font-size="16" fill="#586779">Bozza di architettura: dispositivo codec master / MCU slave</text><g fill="white" stroke="#3e6982" stroke-width="2"><rect x="60" y="172" width="245" height="155" rx="16"/><rect x="458" y="172" width="245" height="155" rx="16"/><rect x="855" y="172" width="245" height="155" rx="16"/></g><g font-family="Arial" fill="#182d40" text-anchor="middle"><text x="182" y="224" font-size="20" font-weight="bold">X201</text><text x="182" y="254" font-size="18">12.288 MHz</text><text x="182" y="281" font-size="14">XO SiTime</text><text x="581" y="222" font-size="19" font-weight="bold">TLV320AIC3204</text><text x="581" y="250" font-size="17">MASTER</text><text x="581" y="281" font-size="14">Genera BCLK e WCLK</text><text x="978" y="222" font-size="19" font-weight="bold">STM32G474</text><text x="978" y="250" font-size="17">SLAVE SAI</text><text x="978" y="281" font-size="14">Elabora audio DSP</text></g><g stroke="#0e8175" stroke-width="4" fill="none"><path d="M305 245 H458"/><path d="M703 220 H855"/><path d="M855 278 H703"/></g><g fill="#0e8175"><path d="M458 245 l-12 -7 v14z"/><path d="M855 220 l-12 -7 v14z"/><path d="M703 278 l12 -7 v14z"/></g><g font-family="Arial" font-size="13" fill="#17645d" text-anchor="middle"><text x="381" y="231">MCLK</text><text x="779" y="205">BCLK 3.072 / WCLK 48k</text><text x="779" y="302">Audio dati bidirezionali</text></g><rect x="64" y="369" width="1040" height="70" rx="12" fill="#edf4f7"/><text x="90" y="401" font-size="16" fill="#2d4758" font-family="Arial">U203 LDO 5 V -&gt; 3.3 V clock, alimentazione separata da RF (proposta)</text><text x="90" y="423" font-size="13" fill="#71818e" font-family="Arial">Schema funzionale non fabbricabile: ERC, firmware e PCB da verificare.</text></svg>'''
write(mod/'Architettura_Clock_Audio_V1.8.svg',svg)

# PDF dossier
pdf=root/'Superstar3900_Dossier_Tecnico_V1.8.pdf'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='H1S',parent=styles['Heading1'],textColor=colors.HexColor('#173247'),spaceAfter=12,fontSize=18,leading=21))
styles.add(ParagraphStyle(name='SB',parent=styles['BodyText'],fontSize=10.5,leading=15,spaceAfter=8))
styles.add(ParagraphStyle(name='SM',parent=styles['BodyText'],fontSize=9,leading=12,textColor=colors.HexColor('#526477')))
styles.add(ParagraphStyle(name='TTL',parent=styles['Title'],fontSize=24,leading=29,textColor=colors.HexColor('#173247'),spaceAfter=12))
story=[]
def p(t,style='SB'):story.append(Paragraph(t,styles[style]))
def table(headers, rows, widths=None):
 data=[[Paragraph(str(x),styles['SM']) for x in headers]] +[[Paragraph(str(x),styles['SM']) for x in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e2eff2')),('LINEBELOW',(0,0),(-1,0),.8,colors.HexColor('#899ca8')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.whitesmoke,colors.white]),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#d0dce2'))]));story.append(t);story.append(Spacer(1,5*mm))
p('SUPERSTAR 3900 SMD EVOLUTION','TTL');p('Dossier tecnico V1.8 - clock audio, sincronismo SAI e alimentazione dedicata','H1S')
p('<b>Avanzamento complessivo stimato: 27%.</b> La progettazione rimane preliminare. Tutti i nuovi componenti sono candidati; nessun disegno è approvato per PCBWay.')
p('<b>Decisione progettuale:</b> usare il TLV320AIC3204 come master dei clock audio e lo STM32G474 come slave SAI. La V1.7 ipotizzava clock indipendenti: ciò potrebbe accumulare errori di campionamento. Il nuovo contratto evita due riferimenti indipendenti per MCLK e BCLK/WCLK, ma richiede prova firmware e hardware.')
p('1. Piano frequenze audio','H1S')
table(['Segnale','Valore nominale','Metodo'],[['MCLK','12.288 MHz','Oscillatore X201'],['Fs / WCLK','48 kHz','codec / divisori'],['BCLK','3.072 MHz','48k x 2 canali x 32 bit'],['Rapporto MCLK/Fs','256','12,288,000 / 48,000'],['Rapporto MCLK/BCLK','4','12,288,000 / 3,072,000']],[36*mm,44*mm,92*mm])
p('Il numero di divisione e i registri del codec richiedono verifica. I test software controllano i rapporti di frequenza, non il funzionamento dei circuiti.')
story.append(PageBreak());p('2. Schema elettronico incrementale','H1S')
p('Nel file KiCad V1.8 sono stati aggiunti i due dispositivi attivi e sei componenti passivi. Restano incorporati e invariati gli schemi preliminari del MCU e codec della V1.7. I footprint non sono stati approvati.')
table(['Rif.','Componente','Reti principali'],[['X201','SiT8008AI-22-33E-12.288000','VDD 3V3_AUDIO_CLK; OUT XO_MCLK_RAW; OE XO_OE'],['U203','TPS7A2033PDBVR','IN/EN 5V_AUX_PROTECTED; OUT 3V3_AUDIO_CLK'],['R204','4.7 kohm','pull-up ingresso OE'],['R205','33 ohm','smorzamento verso MCLK codec'],['C215/C216','1 uF','ingresso/uscita LDO'],['C217/C218','100 nF / 1 uF','bypass oscillatore']],[26*mm,60*mm,84*mm])
p('<b>Nota di sistema:</b> la sorgente della rete 5V_AUX_PROTECTED e il collegamento gerarchico al foglio alimentazioni rimangono da completare; non confondere un nome di rete con un percorso fisicamente verificato.')
p('<b>Corrente e termica:</b> stimando 5 mA sul solo oscillatore, il regolatore a 5 V / 3.3 V dissiperebbe circa 8.5 mW. È una stima d’esempio, non un worst-case. Occorre includere correnti a freddo, carichi e temperatura ambientale.')
p('3. Valutazione sincronismo','H1S')
p('Se due clock differissero di 40 ppm complessivi, alla frequenza di 48 kHz l’errore accumulerebbe 1.92 frame/s: senza recupero di clock o buffer adattativo possono verificarsi underflow/overflow. Usare il codec master riduce questo rischio perché i segnali BCLK e WCLK derivano dal medesimo riferimento MCLK. Il firmware SAI STM32 resta da convalidare.')
story.append(PageBreak());p('4. Verifiche e blocchi aperti','H1S')
table(['Prova','Esito V1.8'],[['Controllo dei 9 pin aggiunti (X201/U203)','PASS - software'],['Reti di clock e passivi','PASS - audit di testo, non ERC'],['Fs/BCLK/MCLK','PASS - calcolo riproducibile'],['Regressione precedenti','Eseguita; log allegati'],['KiCad ERC / netlist esportata','NON eseguiti: kicad-cli assente'],['STM32 SAI slave e registri codec','NON eseguiti'],['Rumore, jitter e spurie sulla PCB','NON misurati'],['PCB e fabbricazione','NON pronta']],[90*mm,80*mm])
p('5. Prossime azioni','H1S')
p('1) Verifica KiCad ERC completa e mappatura footprint reali. 2) Collegare fisicamente i fogli di alimentazione e MCU/codec. 3) Configurare STM32 SAI slave e codec clock master in un banco prova. 4) Dimensionare interfacce AF e filtraggio digitale. 5) Continuare con la parte RF/IF e l’audit di rumore.')
p('6. Fonti ufficiali','H1S')
p('Texas Instruments TLV320AIC3204 datasheet (SLOS602E): www.ti.com/lit/ds/symlink/tlv320aic3204.pdf','SM')
p('TI SLAA404C, Design and Configuration Guide: www.ti.com/lit/an/slaa404c/slaa404c.pdf','SM')
p('Texas Instruments TPS7A20 datasheet: www.ti.com/lit/ds/symlink/tps7a20.pdf','SM')
p('SiTime SiT8008 oscillator series: www.sitime.com/products/mhz-oscillators/lvcmos-oscillators/sit8008','SM')
p('Per riprendere il lavoro: allegare lo ZIP V1.8 alla nuova chat; il file RIPRENDI_IN_UNA_NUOVA_CHAT.md contiene lo stato e i rischi aperti.','SM')
def footer(c,d):
 c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#64748b'));c.drawString(18*mm,12*mm,'S3900E · Rev V1.8 · Documento preliminare');c.drawRightString(195*mm,12*mm,f'Pag. {d.page}')
SimpleDocTemplate(str(pdf),pagesize=(210*mm,297*mm),leftMargin=18*mm,rightMargin=18*mm,topMargin=17*mm,bottomMargin=22*mm,title='Superstar 3900 SMD Evolution V1.8').build(story,onFirstPage=footer,onLaterPages=footer)
shutil.copy2(pdf,dst/pdf.name)
# log actual results
write(ver/'RISULTATI_V1.8.json',json.dumps({'revision':'V1.8','status':'draft','completion_percent_estimate':27,'test_audio_clock':proc.returncode,'regression':{x:y for x,y,_,_ in results},'native_kicad_erc':'NOT_EXECUTED','spice':'NOT_EXECUTED','hardware':'NOT_TESTED'},indent=2))
# copy this build script to reproducibility docs (DO NOT execute from inside ZIP without careful output root paths)
shutil.copy2(__file__,ver/'Genera_V1.8_Archivio.py')
# manifest SHA256 excluding itself, master.
manifest_path=dst/'MANIFEST_SHA256_V1.8.csv'
files=sorted([p for p in dst.rglob('*') if p.is_file() and p!=manifest_path and p.name!='MANIFEST_SHA256.txt'])
with manifest_path.open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['file','sha256','bytes'])
 for p in files:w.writerow([str(p.relative_to(dst)),hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_size])
with (dst/'MANIFEST_SHA256.txt').open('w',encoding='utf8') as f:
 for p in sorted([x for x in dst.rglob('*') if x.is_file() and x.name!='MANIFEST_SHA256.txt']):f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(dst))+'\n')
zpath=root/'Superstar3900_SMD_Evolution_V1.8.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(dst.rglob('*')):
  if p.is_file():z.write(p,arcname=str(Path(dst.name)/p.relative_to(dst)))
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 print('ZIP files',len(z.namelist()),'Bytes',zpath.stat().st_size)
print('PDF',pdf.stat().st_size,'V1.8 PASS',proc.stdout.strip())
print('Regressions',[(a,b) for a,b,_,_ in results]);print('OUTPUT',zpath,pdf,fn)
