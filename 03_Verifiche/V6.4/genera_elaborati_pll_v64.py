#!/usr/bin/env python3
"""Genera documenti V6.4. Solo elaborati tecnici, nessuno schema native KiCad."""
from pathlib import Path
import csv,json,html,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
SPEC=ROOT/'01_Specifiche/V6.4'
CHECK=ROOT/'03_Verifiche/V6.4'
BOM=ROOT/'07_Componenti/BOM_PLL_LO_V6.4.csv'

def put(path,text):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.strip()+'\n',encoding='utf8')

def csvout(path,fieldnames,rows):
 with path.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader();w.writerows(rows)

bom=[
('U401','LMX2572RHAR','Sintetizzatore VCO/PLL RHA40','1','Eredita pinmap V0.6, da verificare EVM/TI','CANDIDATO'),
('U402','TPS7A2033DBVR','LDO 3V3_PLL da 5V_RF','1','300 mA nominali da TI, verifica termica bloccante','TERMICA APERTA'),
('Y401','TCXO_12M8','12,8 MHz riferimento PLL','1','Part number, stabilita, livello e pin 10 AFC/GND ancora aperti','TBD'),
('R401','47 kOhm 1%','CE a GND per default OFF','1','Livelli MCU, timing di power-up da verificare','CANDIDATO'),
('R402','10 kOhm 1%','CSB pull-up a 3V3_PLL','1','Non attivare SPI durante lock','CANDIDATO'),
('R403,R404','33 Ohm','Series resistors su SCK/SDI','2','Valore da misurare/EMI e integrita segnali','CANDIDATO'),
('C401,C402','1 uF X7R','LDO ingresso e uscita','2','Capacita effettiva da DC bias, ESR e PCB','CANDIDATO'),
('C403-C408','100 nF X7R','Bypass alimentazioni PLL','6','Quantita non sostituisce bypass completo originale','CANDIDATO'),
('C409-C411','1 uF X7R','Bypass PLL VCC/Vreg','3','Rivalidare singolo pin TI, no rimozione bypass V0.8','CANDIDATO'),
('FB401','Ferrite bead','Isolamento 5V_RF verso U402','1','Impedenza 36-39MHz e corrente reali da misurare','TBD'),
('J401','6 pin controllo','Interfaccia MCU PLL SPI/CE/MUXout/GND','1','Nessuna alimentazione TX','CANDIDATO'),
('J402','SMA o connettore RF LO','LO_RF_RX 36-39MHz verso mixer RX','1','Terminazione, filtro e livello da dimensionare','TBD'),
('R405,C412','TBD','Rete uscita RFoutA AC e matching','2','Non progettare in autonomia 50Ω senza EVM e strumentazione','OPEN'),
('R406,C413','TBD','RFoutB inutilizzato e terminazione','2','Confermare configurazione pin TI/TICS Pro','OPEN'),
('C414-C418','Da V0.6','Loop filter CPout/Vtune candidato','5','NON cambiare valori senza TICS Pro, Kvco, charge pump e fase','OPEN'),
('D401','DNI','Eventuale linea test PLL; no RF PA TX','0','Non montato','DNI')]
rows=[dict(ref=r,part=p,funzione=f,qty=q,note=n,stato=s) for r,p,f,q,n,s in bom]
csvout(BOM,['ref','part','funzione','qty','note','stato'],rows)

basepath=ROOT/'04_KiCad/Bozze_pre_KiCad/LMX2572_RHA_Pinmap_V0.6.csv'
with basepath.open() as f:old=list(csv.DictReader(f))
renames={'3V3_PLL':'3V3_PLL','TCXO_12M8_AC':'TCXO_12M8_AC','RF_A_POS':'PLL_RFOUT_AP','RF_A_NEG':'PLL_RFOUT_AM',
         'RF_B_POS':'RF_B_POS_DNI','RF_B_NEG':'RF_B_NEG_DNI','PLL_SPI_SCK':'PLL_SCK',
         'PLL_SPI_MOSI':'PLL_SDI','PLL_SPI_CSB':'PLL_CS_N','RF_GND':'RF_GND'}
term=[]
for r in old:
 net=renames.get(r['net_proposta'],r['net_proposta'])
 if r['pin']=='1':net='PLL_CE'
 term.append({'ref':'U401','pin':r['pin'],'name':r['ti_name'],'net_v64':net,
              'tipo':r['type'],'status':'RIUSO PIN V0.6 DA VERIFICARE','nota':r['connessione_preliminare']})
for gpio,ref,pin,net in [('PA4','U_MCU','19','PLL_CS_N'),('PA5','U_MCU','20','PLL_SCK'),
                         ('PA7','U_MCU','22','PLL_SDI'),('PB0','U_MCU','25','PLL_MUXOUT'),
                         ('PB1','U_MCU','26','PLL_CE')]:
 term.append({'ref':ref,'pin':pin,'name':gpio,'net_v64':net,'tipo':'MCU_GPIO',
              'status':'MATCH V6.1 PINMAP','nota':'Linea 3,3 V; MCU sempre TX disabilitata'})
csvout(SPEC/'PIN_RETE_PLL_MCU_V6.4.csv',['ref','pin','name','net_v64','tipo','status','nota'],term)

put(SPEC/'SCHEMA_FUNZIONALE_PLL_V6.4.md',f'''# Modulo PLL/LO V6.4 — schema a componenti candidato

**Stato: studio progettuale pin/rete, non schematico KiCad con ERC. NO FAB, RX ONLY, TX DISABILITATA.**

## Obiettivo

Generare LO sopra il canale in prima conversione, **fLO = fRX + 10,695 MHz**. Percorso: TCXO 12,8 MHz → OSCin → U401 LMX2572 (R=10, fPFD=1,28 MHz, integer N) → VCO 4,64768–4,992 GHz → ÷128 → RFoutA → disaccoppiamento e filtro/matching da definire → **J402 LO_RX** 36,310–39,000 MHz → mixer RX. RFoutB inutilizzata e da terminare secondo produttore.

## Collegamenti e sezione elettrica

- U401 LMX2572 in VQFN/RHA 40: 41 terminali comprendendo exposed pad; la tabella V6.4 eredita **senza sostituirlo** il pinmap precedente e include i cinque pin STM32 V6.1.
- PA4 → `PLL_CS_N` (CSB pin 24); PA5 → `PLL_SCK` (SCK pin16); PA7 → `PLL_SDI` (SDI pin17); PB0 ← `PLL_MUXOUT` (pin20); PB1 → `PLL_CE` (pin1). PA6 resta riservato, nessuna modifica ai pin codec. **CE pulldown 47 kΩ**, CSB pullup 10 kΩ, resistenze serie SPI 33 Ω candidate.
- U402 TPS7A2033DBVR da `5V_RF` della V6.3 attraverso FB401 → `3V3_PLL`; rail distinto da `3V3_A`. Condensatori di ingresso/uscita e bypass U401 come studio V0.8; quantità di BOM V6.4 **non è un circuito di bypass completamente validato pin-per-pin**.
- J401 controllo SPI/CE/MUXout + GND; J402 **solo LO ricevitore**, connesso a mixer RX via stadio filtro/matching da definire. Nessuna connessione verso finale RF o TX, nessun connettore RF PA abilitato.
- CPout (pin12) / Vtune (pin35) tramite filtro loop precedente V0.6, **non ricalcolato con modello VCO completo**; richiede TICS Pro, fase, stabilità e spur.
- Oscillatore TCXO 12,8 MHz (Y401) candidato: livello OSCin, condensatori AC e possibile pin 10 AFC/GND sono **da risolvere** prima dello schema nativo; ref_good come controllo logico della V6.4 è un segnale ipotetico, non prova materiale.
- I pin SYNC/SYSREF/RAMP non utilizzati richiedono stati sicuri/terminazione verificata sul datasheet. MUXout richiede bit reali di configurazione per lock-detect; al momento il firmware interpreta un booleano sintetico, non il registro fisico.

## Sequenza di avvio prevista

1. Alimentazioni protette 5V_RF, 3V3_PLL e riferimento TCXO presenti, PWR_GOOD_HW valido. In PA l'LO RX può essere spento.
2. Asserire CE soltanto dopo presenza di alimentazioni e riferimento; attesa **almeno 0,5 ms** per la stabilizzazione interna (il modello usa 1 ms).
3. Caricare **soltanto** profilo di 126 registri (125 → 0) con valori reali validati TICS Pro e relativo RESET R0. Il generatore di V6.4 **non emette registri**: precedente `lmx2572_spi_transport_v15.py` accetta profilo solo con conferma esplicita.
4. Attendere MUXout configurato per lock-detect e lock stabile per finestra *software* candidata 3 ms. Un cambio canale o perdita lock silenzia RX prima di un eventuale aggiornamento.
5. Ogni fault, PWR_GOOD_HW assente, ref mancante o passaggio PA porta a RX silenziata e CE OFF. **TX sempre FALSE**, compreso CH9 e tutti i canali della banda D.

## Limitazioni critiche

**Solo aritmetica**: il calcolo fVCO=fPFD×N e fLO=fVCO/128 è esatto per 270 posizioni; non dimostra lock hardware, correttezza dei valori registri, selezione VCO core, livello di uscita, rumore di fase, spur, spur da buck, phase noise TCXO, EMI, filtri LO, RF image rejection o stabilità del loop. Non usare questa BOM per ordinare PCB.

Fonti: TI LMX2572 https://www.ti.com/product/LMX2572 ; TI TPS7A20 https://www.ti.com/product/TPS7A20 .
''')

put(SPEC/'ECO_ALIMENTAZIONE_E_INTEGRAZIONE_V6.4.md','''# ECO-V64 — integrazione alimentazione/MCU/PLL, obbligatoria nel progetto unificato

1. La V6.3 prevede già `PLL_LO` **0,150 A nominali / 0,250 A inviluppo** sul `5V_RF`. La V6.4 **non aggiunge una seconda voce di carico**: divide il medesimo budget in TPS7A20 dedicato `3V3_PLL` (LMX ~82 mA tipici, TCXO 10 mA assunto, I/O/buffer 13 mA assunti = circa 105 mA, 130–150 mA target di progetto). Attenzione: TCXO e buffer potrebbero essere alimentati diversamente, quindi ricalcolare i consumi reali.
2. V6.3 `3V3_A` (45 mA nominali / 80 mA inviluppo) **non deve alimentare direttamente LMX2572**. Lasciarlo agli analogici originari.
3. LDO `U402 TPS7A20` è capace nominalmente di 300 mA ma la **termica può essere il limite**: a 5→3,3 V e 150 mA dissipa idealmente 0,255 W; con RθJA illustrativa conservativa 199,6 K/W e ambiente 85°C si ottiene 135,9°C, oltre al limite di riferimento 125°C. Richiede package/PCB/condizioni reali o architettura alternativa; NON APPROVATO.
4. CE/U401: pulldown fisico e rete `PWR_GOOD_HW` coerente V6.2; `PLL_CE` PB1 non può essere unico interblocco di sicurezza generale TX. Mute RX durante lock mancante è previsto nel firmware ma hardware da validare.
5. `PLL_CS_N` PA4, `PLL_SCK` PA5, `PLL_SDI` PA7, `PLL_MUXOUT` PB0 e `PLL_CE` PB1 **già riservati in V6.1**, senza sovrapposizione con audio e pannello. Mappa esatta negli allegati.
6. Uscita RX LO 36–39 MHz: filtro/matching e isolamento dalle alimentazioni switching da definire; evitare collegamento al TX. Non mettere PA RF J907 in BOM da montare.
7. Profilo registri TICS Pro non esiste ancora, fPFD 1,28 MHz è nel range **integer-N** ma sotto il minimo per modalità MASH 1–4; scegliere **integer mode**. Non copiare le parole dei registri di vecchie prove o di un progetto LP diverso.
8. TI Rev.B tabella PFD_DLY_SEL/ordine modulatori da confermare nel profilo TICS Pro. I core VCO della mappa V0.6 sono *stime*, non vanno forzati.
9. Mantenere aperti: TCXO pin10 AFC/GND, filtri analogici CPout/Vtune, termiche, EVM/TICS, parità KiCad, misure RF e spuri.
''')

put(CHECK/'PROCEDURA_V6.4.md','''# V6.4 — controlli riproducibili

Dalla root dello ZIP estratto, con Python 3 e senza KiCad:

```bash
PYTHONDONTWRITEBYTECODE=1 python -B 03_Verifiche/V6.4/simula_pll_v64.py
PYTHONDONTWRITEBYTECODE=1 python -B 03_Verifiche/V6.4/genera_elaborati_pll_v64.py
PYTHONDONTWRITEBYTECODE=1 python -B 03_Verifiche/V6.4/test_pll_v64.py
```

Il primo comando rigenera CSV 270 RX e JSON Monte Carlo con seme fissato. Il secondo rigenera BOM, pin/reti, diagramma e documenti progettuali. Il terzo fa 60 test, incluso un fuzzing di 10.000 transizioni della logica RX/PLL. **Nessuno dei tre modifica file storici precedenti alla V6.4**.

Non eseguiti: TICS Pro e veri registri 126-word, KiCad native ERC/DRC, NGSpice modello vendor, phase noise, spettro, VNA, misure elettriche e hardware. TX disabilitata.
''')

svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 670">',
'<rect width="1300" height="670" fill="#101d30"/>',
'<text x="34" y="51" fill="#f4f7fb" font-family="Arial,sans-serif" font-size="28" font-weight="bold">Superstar 3900 • PLL / LO RX • V6.4</text>',
'<text x="34" y="77" fill="#b7c8db" font-family="Arial,sans-serif" font-size="14">Sintesi integer-N matematica • 270 RX • Non schematico KiCad • NO FAB / NO TX</text>',
'<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="#9db7d3"/></marker></defs>']
def block(x,y,w,h,head,lines,col='#223650'):
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="15" fill="{col}" stroke="#7891af"/>')
 svg.append(f'<text x="{x+14}" y="{y+27}" fill="#eaf3ff" font-family="Arial,sans-serif" font-weight="bold" font-size="16">{html.escape(head)}</text>')
 for i,t in enumerate(lines):svg.append(f'<text x="{x+14}" y="{y+53+i*19}" fill="#c9d7e8" font-family="Arial,sans-serif" font-size="14">{html.escape(t)}</text>')
def arr(x,y,xx,yy):svg.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="#9db7d3" stroke-width="2.6" fill="none" marker-end="url(#a)"/>')
block(38,144,208,129,'TCXO Y401',['12,800 MHz','livello/pin 10 TBD'])
block(283,144,207,129,'LMX2572 R / PFD',['÷10 / 1,280 MHz','integer-N, MASH OFF'])
block(532,144,218,129,'VCO interno',['4,64768–4,992 GHz','calibrazione AUTO'])
block(789,144,190,129,'DIV e RFoutA',['÷128','LO 36,31–39 MHz'])
block(1015,144,247,129,'MIXER RX',['FI1 = 10,695 MHz','immagine: 47–49,695 MHz'])
for a,b in [(246,283),(490,532),(750,789),(979,1015)]:arr(a,207,b,207)
block(54,376,265,127,'5V_RF protetto',['V6.3: carico PLL incluso','0,15 A nominali previsti'],'#314d59')
block(358,376,270,127,'U402 LDO 3V3_PLL',['TPS7A20 candidato','termica 85°C: OPEN'],'#314d59')
block(672,376,278,127,'STM32 MCU V6.1',['PA4,PA5,PA7 / PB0,PB1','SPI / lock / CE'], '#304358')
block(989,376,273,127,'RX MUTE / NO TX',['Mute su perdita lock, PA','TX FALSE in ogni stato'],'#503843')
arr(319,441,358,441);arr(628,441,672,441);arr(950,441,989,441)
svg.append('<path d="M497 375 V318 H654 V274" fill="none" stroke="#9db7d3" stroke-width="2.3" marker-end="url(#a)"/>')
svg.append('<path d="M811 375 V328 H407 V274" fill="none" stroke="#9db7d3" stroke-width="2.3" marker-end="url(#a)"/>')
svg.extend(['<text x="42" y="586" fill="#c9d7e8" font-family="Arial,sans-serif" font-size="15">Riferimento 12,8MHz; N = 3631–3900; 270 posizioni RX, 30 ALFA, 0 permessi TX.</text>',
'<text x="42" y="617" fill="#ffb0b0" font-family="Arial,sans-serif" font-size="15">APERTO: valori registri TICS Pro, termica PLL, filtro loop, spur, matching RF, TCXO, test KiCad e hardware.</text>',
'<text x="42" y="644" fill="#a0b5d1" font-family="Arial,sans-serif" font-size="13">Diagramma progettuale generato da script Python; la continuità elettrica non è ancora stata validata.</text>',
'</svg>'])
p=SPEC/'DIAGRAMMA_PLL_LO_V6.4.svg';p.write_text('\n'.join(svg));ET.parse(p)
print('GENERATI',len(rows),'BOM righe',len(term),'pin/reti',p)
