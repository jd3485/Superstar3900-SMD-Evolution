from pathlib import Path
import csv,html,textwrap,json
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'01_Specifiche/V6.5';V=ROOT/'03_Verifiche/V6.5';B=ROOT/'07_Componenti'
def put(path,text):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(textwrap.dedent(text).lstrip(),encoding='utf-8')

def write_csv(path,fields,records):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)

bom=[
('U501','1','ADE-1+','Mixer passivo doppio bilanciato Mini-Circuits','MINICIRCUITS_DATASHEET_PIN_CONFIRMED','RF=3 IF=2 LO=6 GND=1/4/5','CD636 land pattern da importare e verificare'),
('J501','1','50 OHM RX_RF_FROM_V58','Connettore RF verso front-end RX storico','CANDIDATE_INTERFACE','25,615–28,305 MHz','SMA tipo e footprint da qualificare'),
('J502','1','50 OHM LO_RX_FROM_V64','Connettore LO da LMX2572 V6.4','CANDIDATE_INTERFACE','36,310–39,000 MHz','Nessun driver LO qualificato'),
('J503','1','50 OHM IF1_10M695_OUT','Connettore IF verso canale FI/demod','CANDIDATE_INTERFACE','10,695 MHz','Coassiale e carico da definire'),
('F501','1','BPF6 passabanda ideale 25–29 MHz','Preselettore trasformazione Butterworth N=3 (6 poli complessivi)','FUNCTIONAL_PLACEHOLDER','Non sintetizzato in L/C; rete reale da progettare','Perdita e Q ignoti; 50 ohm non verificati'),
('C501','1','TBD C0G RF','Accoppiamento ingresso preselector','VALUE_PENDING','f>25 MHz, reattanza/ESR da simulare','Non assegnare valore senza component parasitic'),
('C502','1','TBD C0G RF','Accoppiamento RF preselector-mixer','VALUE_PENDING','matching 50 ohm','Stessa precauzione'),
('U502','1','BUFFER LO LEVEL+7DBM TBD','Stadio attenuazione o guadagno per LO','PART_PENDING','+7dBm at pin6 U501 into matched network','Non supporre LMX lo eroghi direttamente'),
('FL502','1','LO_BPF 36–39 MHz TBD','Filtro LO per ridurre spur','PART_PENDING','matching 50 ohm','Progettazione V6.6 PLL matching'),
('C503','1','TBD C0G RF','Accoppiamento ingresso LO mixer','VALUE_PENDING','senza sovraccarico sul LO','Valore SRF/Q da verificare'),
('C504','1','TBD C0G IF','Accoppiamento IF dal pin2 mixer','VALUE_PENDING','IF circa 10.695 MHz','Carico mixer, bias, isolamento DC da definire'),
('F503','1','IF_WIDE 10.695 MHz TBD','Filtro FI1 ramo AM/FM','PART_PENDING','BW 6 e 12 kHz solo studio','Nessuna topologia acquistata'),
('F504','1','IF_NARROW 10.695 MHz TBD','Filtro FI1 ramo USB/LSB/CW','PART_PENDING','BW 2.7 / 0.5kHz solo studio','CW alto Q richiede catena adeguata'),
('SW501+SW502','1','GANGED_IF_FILTER_BANK_SELECT TBD','Commutatore IF wide/narrow','PART_PENDING','interdizione durante il retune/PA','Part number e isolamento da dimensionare'),
('U503','1','IF_10M695_AMP TBD','Amplificatore IF successivo','PART_PENDING','guadagno, rumore, dinamica da allocare','Non usare ADL5535 a 10.695 senza verifica'),
('R501','1','50 OHM nominal terminator TBD','Carico/matching interfaccia IF, solo se necessario','VALUE_PENDING','50Ω sistema nominale','Non duplicare terminazione se load already 50Ω'),
('J504','1','CTRL_IF_FILTER_RX','Comando selezione filtri + RX guard','CANDIDATE_INTERFACE','dal MCU V6.1, pin ancora da assegnare','Nessun GPIO inventato'),
('TP501','1','TP_RX_RF','Test point RF (carico 50 Ω)','MEASUREMENT_PLACEHOLDER','misurare con sonda carico adeguata','Non aggiungere stub senza studio'),
('TP502','1','TP_LO_LEVEL','Test point LO','MEASUREMENT_PLACEHOLDER','+7 dBm target','Attenuatore/accoppiatore RF necessario'),
('TP503','1','TP_IF_10M695','Test point IF1','MEASUREMENT_PLACEHOLDER','10.695 MHz','Interferenza con matching da valutare'),
]
write_csv(B/'BOM_MIXER_FI_V6.5.csv',['ref','qty','component_or_value','function','qualification','requirement','blocking_note'],[dict(zip(['ref','qty','component_or_value','function','qualification','requirement','blocking_note'],r)) for r in bom])
netlist=[
('J501','1','RX_RF_50R_FROM_FRONTEND','BPF_PRESELECTOR','RF_FROM_FRONTEND','INTERFACE_CANDIDATE'),
('C501','1','RX_RF_50R_FROM_FRONTEND','BPF_PRESELECTOR','RF_AC_COUPLING','VALUE_TBD'),
('C501','2','RX_RF_PRESEL_IN','BPF_PRESELECTOR','RF_AC_COUPLING','VALUE_TBD'),
('F501','IN','RX_RF_PRESEL_IN','BPF_PRESELECTOR','BPF_25_29_IDEAL','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('F501','OUT','RF_25_29_PRESEL_OUT','BPF_PRESELECTOR','BPF_25_29_IDEAL','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('C502','1','RF_25_29_PRESEL_OUT','MIXER_RF','RF_AC_COUPLING','VALUE_TBD'),
('C502','2','RF_MIXER_IN_AC','MIXER_RF','RF_AC_COUPLING','VALUE_TBD'),
('U501','3','RF_MIXER_IN_AC','MIXER_RF','ADE-1+','PHYSICAL_PIN_CONFIRMED'),
('J502','1','RX_LO_FROM_PLL_V64','MIXER_LO','PLL_V6_4','INTERFACE_CANDIDATE'),
('FL502','IN','RX_LO_FROM_PLL_V64','MIXER_LO','LO_BPF_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('FL502','OUT','RX_LO_FILTERED','MIXER_LO','LO_BPF_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('U502','IN','RX_LO_FILTERED','MIXER_LO','LO_BUFFER_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('U502','OUT','RX_LO_AMP_OUT','MIXER_LO','LO_BUFFER_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('C503','1','RX_LO_AMP_OUT','MIXER_LO','LO_COUPLING','VALUE_TBD'),
('C503','2','RX_LO_36_39_50R','MIXER_LO','LO_COUPLING','VALUE_TBD'),
('U501','6','RX_LO_36_39_50R','MIXER_LO','ADE-1+','PHYSICAL_PIN_CONFIRMED'),
('U501','2','IF_10M695_RAW','IF1_OUTPUT','ADE-1+','PHYSICAL_PIN_CONFIRMED'),
('U501','1','GND_RF','GROUND','ADE-1+','PHYSICAL_PIN_CONFIRMED'),
('U501','4','GND_RF','GROUND','ADE-1+','PHYSICAL_PIN_CONFIRMED'),
('U501','5','GND_RF','GROUND','ADE-1+','PHYSICAL_PIN_CONFIRMED'),
('C504','1','IF_10M695_RAW','IF1_OUTPUT','IF_DC_BLOCK','VALUE_TBD'),
('C504','2','IF_10M695_COUPLED','IF1_OUTPUT','IF_DC_BLOCK','VALUE_TBD'),
('SW501','IN','IF_10M695_COUPLED','IF_FILTER_BANK','IF_BANK_SWITCH','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('SW501','WIDE','IF1_WIDE_IN','IF_FILTER_BANK','IF_BANK_SWITCH','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('SW501','NARROW','IF1_NARROW_IN','IF_FILTER_BANK','IF_BANK_SWITCH','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('F503','IN','IF1_WIDE_IN','IF_FILTER_BANK','IF_WIDE_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('F503','OUT','IF1_WIDE_OUT','IF_FILTER_BANK','IF_WIDE_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('F504','IN','IF1_NARROW_IN','IF_FILTER_BANK','IF_NARROW_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('F504','OUT','IF1_NARROW_OUT','IF_FILTER_BANK','IF_NARROW_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('SW502','WIDE','IF1_WIDE_OUT','IF_FILTER_BANK','IF_BANK_COMBINER','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('SW502','NARROW','IF1_NARROW_OUT','IF_FILTER_BANK','IF_BANK_COMBINER','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('SW502','COMMON','IF_10M695_FILTERED','IF_FILTER_BANK','IF_BANK_COMBINER','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('U503','IN','IF_10M695_FILTERED','IF_GAIN','IF_AMP_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('U503','OUT','IF_10M695_GAINED','IF_GAIN','IF_AMP_TBD','FUNCTIONAL_ONLY_NO_PHYSICAL_PIN'),
('J503','1','IF_10M695_GAINED','IF_TO_DEMOD','IF_STAGE_INTERFACE','INTERFACE_CANDIDATE'),
('J504','SEL','IF_FILTER_SELECT_REQ','CONTROL','MCU_V6_1_TO_BE_ASSIGNED','INTERFACE_CANDIDATE'),
('J504','MUTE','IF_MUTE_RX','CONTROL','GUARD_V6_5','INTERFACE_CANDIDATE'),
]
write_csv(P/'NETLIST_FUNZIONALE_MIXER_FI_V6.5.csv',['ref','pin_or_port','net','group','block','status'],[dict(zip(['ref','pin_or_port','net','group','block','status'],r)) for r in netlist])

put(P/'SCHEMA_FUNZIONALE_MIXER_FI_V6.5.md', '''
# Schema funzionale primo mixer RF e FI1 V6.5

**Candidato in progettazione, NO FAB / NO TX. Non è schematico KiCad con ERC.**

## Catena di ricezione

`Antenna RX → protezioni / attenuatore / LNA storico V5.8 → J501 RX 50Ω → F501 preselettore 25–29MHz (MODELLO IDEALE, RETE NON DIMENSIONATA) → U501 ADE-1+ pin RF3 → pin IF2 → C504 accoppiamento TBD → SW501/SW502 bank filtri IF → ramo AM/FM largo o USB/LSB/CW stretto → U503 amp IF TBD → J503 uscita IF 10,695MHz → demodulatori futuri → audio V6.0`.

Separatamente: `LMX2572 V6.4 J402 LO 36,310–39,000MHz → J502 → filtro spur FL502 TBD → buffer/attenuatore U502 TBD → U501 pin LO6 (+7dBm target 50Ω)`. Il sintetizzatore V6.4 non ha ancora rete d'uscita e livello RF dimostrato.

## Pin mixer ADE-1+ (confermati su datasheet produttore)

- U501 pin 1 GND_RF, pin 2 `IF_10M695_RAW`, pin 3 `RF_MIXER_IN_AC`, pin 4 GND_RF, pin 5 GND_RF, pin 6 `RX_LO_36_39_50R`.
- Case style CD636, port nominali 50Ω, LO +7 dBm nominale, perdita di conversione tipica del componente 5 dB. Non è un guadagno e non è una misura a 27 MHz / 10,695 MHz.
- Nessuna alimentazione elettrica richiesta **dal mixer passivo**, ma gli stadi LO / IF e LNA usano rail preesistenti e devono essere riprogettati nel bilancio di potenza V6.3/6.4.

## Filtro preselector: ipotesi numerica, non componenti fisici

BPF Butterworth di **ordine prototipo 3** e conseguente **ordine analogico 6**, f−3dB=25,000/29,000 MHz e Z0 nominale 50 Ω. Il trasferimento analitico passa tutte le 270 RX con perdita ideale minore di 0,39 dB e determina reiezione relativa immagine minima circa 53,46 dB. Il **valore di ordine non significa tre soli induttori**: la rete reale richiede sintesi LC, parassiti, Q finito, adattamento, perdite e S11/S21, e potrebbe richiedere ulteriori stadi o tracking varicap.

Il caso di esempio `blocker immagine 0 dBm` contro `spur richiesto < -110 dBm` imporrebbe 110 dB di attenuazione, NON raggiunti da questo modello: non si può dichiarare sufficiente la reiezione senza una specifica completa di sensibilità, blocker e dinamica mixer/LNA.

## Filtri FI per modalità, solo requisiti di progetto

- AM: BW nominale candidata 6 kHz; FM: 12 kHz (richiede controllo adiacenti e deviazione reale). USB e LSB: 2,7 kHz. CW: 0,5 kHz.
- A 10,695 MHz il Q caricato idealizzato `f0/BW` arriva a circa 21.390 per CW: **serve tecnologia adeguata** (quarzo/ceramica/DSP con architettura adatta), non è un banco LC convenzionale già fattibile.
- Non sono ancora stati selezionati i modelli filtro, il BFO/demod SSB/CW, gli impedenziamenti, il blocco AGC o il demod FM: **vengono sviluppati nelle prossime revisioni**.
- `J504` è un contratto di controllo, non un'assegnazione GPIO; serve allocazione pin STM32 e priorità PA/retune/PLL ready, per non rompere la V6.1.

## Condizioni di avvio e guasti

Il modello `rx_frontend_guard_v65.py` mantiene audio e ricezione muted in caso di PA, retune, PLL non pronto, interblocco alimentazione assente, filtro non selezionato o fault. Ricezione riabilitata solo con tutte le condizioni valide. **TX sempre FALSE**.

## Decisioni bloccanti per schemi/PCB

1. Ricavare rete BPF fisica 50Ω, componente RF, Q/carico, layout e budget blocker; simulare S21/S11, Monte Carlo su valori L/C e perdite e testare strumentalmente.
2. Misurare LO +7 dBm alla porta ADE-1+ con carico reale e spur/isolamento, progettare stadio driver e filtro; aggiornare correnti V6.3.
3. Selezionare realmente filtri FI 10,695 MHz e architettura di demod/doppia conversione con gestione AM/FM/SSB/CW e controllo interferenze adiacenti.
4. Progettare amplificatore FI e AGC con rumore/IP3/dinamica, verificare compatibilità front-end V5.8; senza questo non si può calcolare la sensibilità completa.
5. KiCad schemi ERC / PCB DRC non eseguiti; nessuna produzione, TX non collegata.

Fonti: https://www.minicircuits.com/pdfs/ADE-1%2B.pdf ; https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B ; https://www.ti.com/product/LMX2572 .
''')
put(P/'ECO_INTEGRAZIONE_RX_V6.5.md','''
# ECO interconnessioni V6.5 — integrazione V5.8/V6.0/V6.1/V6.2/V6.3/V6.4

- RX della V5.8: non modificare PCB del test 50 Ω; il modulo J501 richiede uscita 50 Ω qualificata della catena RX, non un collegamento inventato a un pad già esistente. Filtro immagine da collocare prima di U501, verificare se meglio prima/dopo ADL5535 nel bilancio blocker.
- PLL V6.4: J402 → J502, LO +7dBm sul pin U501. I pin LMX esistenti non cambiano. Rete/driver/filtro LO BLOCCANTE per la realizzazione; non contare due volte corrente PLL su V6.3.
- Supervisore MCU V6.1 e PLL V6.4: solo dopo lock stabile e PA non attiva, abilita IF audio; selezione del banco filtri IF ancora da assegnare su MCU (risorsa pin da riesaminare).
- PA V6.0 e interblocco V6.2: sempre RX muted durante PA, TX non disponibile e nessuna uscita RF TX; non utilizzare TX-permitted del piano storico.
- Alimentazioni V6.3: ADE-1+ mixer passivo senza rail proprio, ma stadi U502/U503 non sono stati dimensionati; budget alimentazione da aggiornare soltanto quando sono scelti.
- Collegamento audio V6.0: la FI 10,695 MHz **non è un segnale audio**; serve demodulazione e conversione a banda base PRIMA di TMUX1308. Non collegare FI direttamente all'ingresso audio.

**STATO: NESSUNO DEI BLOCCANTI QUI SOPRA CONFERISCE FAB APPROVAL.**
''')
put(V/'PROCEDURA_V6.5.md','''
# Ripetizione dei test V6.5

Da cartella radice ZIP estratto (Python ≥3.10, numpy, matplotlib):

```bash
python -B 03_Verifiche/V6.5/simula_mixer_fi_v65.py
python -B 03_Verifiche/V6.5/test_mixer_fi_v65.py
```

Il simulatore usa risposta ideale Butterworth e FFT di un prodotto di coseni. **Nessuna soluzione SPICE, S-parameter, misura fisica o validazione di prestazione hardware**. La tabella CSV contiene tutte le 270 frequenze e la reiezione soltanto ideale. Il tester esegue 50 assert di test indipendenti, con 128 combinazioni logiche esaustive e 10.000 ingressi pseudo-casuali; non è una misura RF.

Suite regresse selezionate, modalità immutabile (`-B` e `PYTHONDONTWRITEBYTECODE=1`): V5.9/V6.0/V6.1×2/V6.2/V6.3/V6.4. I vecchi test geometrici e il KiCad nativo rimangono nel progetto ma **non si dichiara qui di avere eseguito l'intera storia**.
''')

# SVG functional block diagram
nodes=[('J501 ANTENNA RX',80,170,168),('F501 PRESELETTORE',280,170,182),('U501 MIXER ADE-1+',498,170,184),('FI FILTER BANK',724,170,174),('DEMOD / AUDIO',933,170,175),('PLL V6.4',280,345,180),('DRIVER LO +7dBm',500,345,185)]
s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1190 500" width="1190" height="500">',
'<rect width="1190" height="500" fill="#fafcff"/>',
'<text x="60" y="52" font-size="28" font-family="Arial,sans-serif" fill="#102b46" font-weight="bold">Superstar 3900 — RF / prima FI V6.5</text>',
'<text x="60" y="80" font-size="15" font-family="Arial,sans-serif" fill="#a13535">STUDIO FUNZIONALE · LO +7 dBm da verificare · BPF IDEALE · NO FAB / NO TX</text>',
'<defs><marker id="arr" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto"><polygon points="0 0,9 3.5,0 7" fill="#426c9e"/></marker></defs>']
for name,x,y,w in nodes:
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="72" rx="12" fill="#e7effb" stroke="#527cae" stroke-width="2"/>')
 s.append(f'<text x="{x+w/2}" y="{y+32}" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="bold" fill="#163457">{html.escape(name)}</text>')
 if name=='F501 PRESELETTORE':s.append(f'<text x="{x+w/2}" y="{y+54}" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#163457">25–29 MHz ideale</text>')
 if name=='FI FILTER BANK':s.append(f'<text x="{x+w/2}" y="{y+54}" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#163457">10,695 MHz TBD</text>')
 if name=='U501 MIXER ADE-1+':s.append(f'<text x="{x+w/2}" y="{y+54}" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#163457">RF3 · IF2 · LO6</text>')
for x1,x2 in [(248,280),(462,498),(682,724),(898,933)]:s.append(f'<line x1="{x1}" y1="206" x2="{x2-5}" y2="206" stroke="#426c9e" stroke-width="2.4" marker-end="url(#arr)"/>')
s+=['<line x1="460" y1="381" x2="495" y2="381" stroke="#426c9e" stroke-width="2.4" marker-end="url(#arr)"/>',
'<path d="M 593,345 L 593,252" fill="none" stroke="#426c9e" stroke-width="2.4" marker-end="url(#arr)"/>',
'<text x="613" y="294" font-family="Arial,sans-serif" font-size="14" fill="#426c9e">LO: 36,31–39 MHz</text>',
'<text x="282" y="268" font-family="Arial,sans-serif" font-size="13" fill="#41536b">Immagine 47,005–49,695 MHz: rigetto da qualificare</text>',
'<rect x="80" y="440" width="1030" height="32" rx="6" fill="#ffeae8"/>',
'<text x="596" y="462" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="#8f3030">Solo ricezione: filtro fisico e interfaccia audio ancora non progettati. TX = OFF.</text>',
'</svg>']
put(P/'DIAGRAMMA_MIXER_FI_V6.5.svg','\n'.join(s))
print('CREATED',len(bom),'BOM',len(netlist),'functional netlist', 'SVG')
