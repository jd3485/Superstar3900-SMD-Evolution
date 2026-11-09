# Decisioni V6.3 — alimentazione generale 13,8 V

- D-V63-01: LM74900-Q1 candidato a 2 MOSFET per polarità inversa e protezione primaria; dimensionamento e SOA restano aperti; fusibile 5 A provvisorio soltanto per servizi, NON TX RF.
- D-V63-02: buck LM61460 5 V/400 kHz (4.7µH, 4x22µF, 100k/24.9k), 3.3 V/1MHz (2.2µH, 3x22µF, 100k/43.2k), LDO TPS7A20 3V3_A e 1V8_CODEC.
- D-V63-03: S901 SPST hardware EN→VS; EN dei buck dal bus protetto, così non esiste boot circolare attraverso 3V3_D; PGOOD dei buck pull-up su 3V3_D.
- D-V63-04: Q903 high-side audio da scegliere; J907 finale RF fisicamente NON collegato e J902 bypass test DNI. Nessuna produzione, TX sempre disabilitata.
- D-V63-05: 25.000 scenari numerici di carico, calcolo inrush e brownout solo ideali; nessuna misura, SPICE native o KiCad.
- D-V63-06: segnalare nominali DCM/PFM e possibile interferenza RF 26–28MHz; verifica quantitativa EMI rinviata alla qualifica dell'intero progetto.
- ECO-V63-01: normalizzare alias V6.2 +13V8_PROTECTED → V6.3 13V8_PROTECTED; POWER_GOOD_HW → PWR_GOOD_HW prima dei progetti KiCad unificati.
- D-V63-07: primario progetto radio completa prima della revisione KiCad finale; restano test incrementali.

---

## Storico registro V6.2

# Decisioni V6.2 — interblocchi alimentazioni PA/TX

- D-V62-01: supervisore 3V3 con watchdog TPS3823A-33 candidato; RESET alto = permesso di sola logica, non autorizzazione TX.
- D-V62-02: finestra 13,8 V con TPS3700, partitori 287k/10k e 374k/10k, soglie nominali 11,88–15,36 V; Monte Carlo numerico ≠ approvazione hardware.
- D-V62-03: ECO obbligatoria V6.1 S742 PA: contatto hardware SPDT separato (NC RX, NO PA, break-before-make). Nessuna modifica retroattiva ai sorgenti V6.1.
- D-V62-04: MCU U201 PB11/pin33 -> WDI_HEARTBEAT; PB4/pin57 -> TX_ARM_REQUEST, senza interferire con PA9/WCLK/SWD.
- D-V62-05: amp SD e PA relay passano obbligatoriamente da AND con power/codec/fault/PA, non da uscite MCU dirette.
- D-V62-06: J801 jumper TX di prova DNI aperto; J802 loop termico/SWR NON implementato. TX real RF mai connessa; NO FAB.
- D-V62-07: 31 test software + 50k campioni della simulazione registrati; ERC/DRC nativi e SPICE analogico non eseguiti.
- D-V62-08: prossima V6.3 ingresso/alimentazioni 13,8 V e conversioni, conservando tutto lo storico.

---

# Decisioni V6.1 — scheda MCU / pannello vintage

- D-V61-01: mantenere STM32G474RET6 LQFP64 e mappare i 64 pin ST DS12288 Rev6, senza toccare contratto SAI V2.1 (PA9/43 WCLK) e PLL.
- D-V61-02: due MCP23017 0x20/0x21 su I²C del codec, GPA7/GPB7 solo uscite LED per DS20001952D, 14 ingressi a espansore, selettori one-hot. 100 kHz solo nominale sul bus 4,7k+150pF.
- D-V61-03: CH9, PA, PTT ed encoder direttamente su STM32; PA doppio polo con segnale di blocco HW ancora da progettare; AMP_SD_REQUEST non è uscita AMP_SD fisica.
- D-V61-04: 270 frequenze RX dalla tabella storica, CH9 diretto 27.065 MHz AM, ALFA fisico, PA>CH9>RX; qualsiasi stato pannello ambiguo = mute, NO TX. 40 vecchi marcatori `SI` della banda D NON sono permessi automatici.
- D-V61-05: simulazione ideale RC + sweep tolleranze + 2.000 bounce e test firmware sono eseguiti; non sono ERC/DRC KiCad o misura. Parti e layout restano candidati.
- D-V61-06: continua con V6.2 alimentazioni/interblocchi veri e tutte le altre sezioni, preservando le revisioni storiche integralmente e verificando ogni archivio.

---

# Decisioni V6.0 — modulo AUDIO/PA, fase progettazione radio completa

- D-V60-01: scegliere TMUX1308 PW16 (5 demod RX + 3 ingressi parcheggiati), TLV9062 SOIC8 (VMID + buffer) e TPA3111D1 PWP28 (mono BTL) come candidati, con pinout verificato TI. Nessuna validazione prestazioni.
- D-V60-02: microfono elettrete ADC_L, demod RX ADC_R, codec remoto TLV320AIC3204; DAC LOL alimenta amplificatore, DAC LOR TX non connesso a questa scheda.
- D-V60-03: relais DPDT due poli per BTL, radio NC, PA NO; niente GND sulle uscite audio. Mute durante ogni commutazione e PA PTT con gate voce.
- D-V60-04: AMP_SD pulled low, mux disabilitato di default, PA_MODE_HW dovrà inibire RF mediante circuito indipendente V6.2; non considerare completata la sicurezza HW in V6.0.
- D-V60-05: specifica JSON/CSV a pin e parti è uno schema preliminare di connessioni, NON uno schema KiCad validato. 35 test statici; TX OFF, no FAB, nine gates still OPEN.
- D-V60-06: progettazione radio globale PRIMA delle simulazioni e dei report KiCad, su richiesta utente; preservare tutto lo storico e gli snapshot integrali.

---

# Decisioni V5.9 — 9 novembre 2026

- **D-V59-01 (METODO):** mantenere revisioni incrementali cumulative ma passare alla progettazione dell'intera radio; simulazioni formali, KiCad ERC/DRC e campagne di verifica SOLO dopo il raggiungimento della progettazione completa, senza ignorare errori evidenti lungo il percorso.
- **D-V59-02 (INTERCONNESSIONI):** introdurre contratto logico 26 blocchi / 54 segnali, architettura e responsabilità; i collegamenti non costituiscono pinout fisici o schema fabbricabile.
- **D-V59-03 (AUDIO):** MIC su codec ADC_L, RX su ADC_R, con mux audio candidato cinque ingressi AM/FM/USB/LSB/CW; codec DAC_L audio ascolto/PA, DAC_R modulazione TX ma default MUTE. Sezione da progettare.
- **D-V59-04 (SICUREZZA):** PA disabilita RF HW; routing software non concede mai TX; 9 gate V5.0 sempre OPEN e nessuna produzione.
- **D-V59-05 (CONSERVAZIONE):** mantenere CAD, manuali, software e storico V5.8; snapshot integrali dei tre documenti attivi aggiornati e verifica cumulativa SHA-256.

---
## Registro V5.8 e precedenti

# Decisioni V5.8 — 9 novembre 2026

- **D-V58-01 (MISURA):** distanza centrolinea pista RF ↔ centro via GND come metrica diagnostica, non DRC/impedenza/corrente di ritorno. Soglia 5 mm solo per ordinare le verifiche; nessuna prescrizione automatica di inserimento via.
- **D-V58-02 (PRIORITÀ):** esaminare in KiCad nativo e successivamente in collaudo il piano di riferimento lungo l'attenuatore: RF_ATTEN_IN max 9,5811 mm, RF_ATTEN_OUT 6,9385 mm (campioni 0,20 mm). Valutare l'ADI EVAL-ADL5535 come riferimento di layout, non come sostituto del nostro DFM.
- **D-V58-03 (RELEASE):** non considerare i piani ideali V5.7 come piano RF vero. Con 4 zone UNFILLED, mancano ERC/DRC/refill/parità nativi, CAD SMA TE e processo VIPPO/stencil; 9/9 gate OPEN; NO FAB, NO PCBWay, NO TX.
- **D-V58-04 (CONSERVAZIONE):** PCB V3.8 e V4.8/V5.2 invariati. 30 test nuovi, 19 suite regressive; snapshot esatti dei 5 documenti attivi, archiviazione cumulativa integra.

---
# Decisioni V5.7 — 8 novembre 2026

- **D-V57-01 (MODELLO):** usare l'analisi delle sagome potenziali dei quattro piani solo come **upper bound** geometrico; nessuna assimilazione a `--refill-zones` o DRC.
- **D-V57-02 (GND):** le 70 vie GND cadono interamente nei quattro contorni e su F.Cu 24 pad raggiungono la regione ideale nel calcolo; queste intersezioni non validano thermal spokes o connettività reale. Le 64 isole pre-refill della V5.6 restano aperte fino a riempimento e ispezione nativi.
- **D-V57-03 (RELEASE):** nessuna approvazione TE/PCBWay/assemblatore e nessun collaudo RF. Tutti i nove gate V5.0 ancora aperti: NO FAB, NO PCBWay, NO TX.
- **D-V57-04 (INTEGRITÀ):** conservare originali e snapshot integrali dei 5 documenti aggiornati, eseguire 30 test nuovi e 18 suite software senza modificare i CAD.

---
# Decisioni V5.6 — 8 novembre 2026

- **D-V56-01 (SCREEN):** richiedere verifica topologica F.Cu oltre al solo clearance: 7 reti di segnale continue, massa in 64 isole sul rame senza zone riempite. È misura preliminare, NON DRC.
- **D-V56-02 (GND):** non dichiarare 64 errori DRC: le quattro zone GND sono ancora UNFILLED. La continuità effettiva dipende dal riempimento, dalle termiche e dai via tra piani; rilasciare soltanto dopo controllo KiCad nativo completo.
- **D-V56-03 (CONSERVAZIONE):** nessuna modifica a schema/PCB della V5.2 o ai precedenti; rame V5.2 identico alla V4.8. Archivi precedenti preservati byte per byte; documenti gestionali archiviati come snapshot.
- **D-V56-04 (GATE):** nove gate V5.0 restano OPEN. NO FAB, NO PCBWay, NO TX. Non equiparare pass statici a convalida hardware.

---
# Decisioni V5.5 — 8 novembre 2026

- **D-V55-01 (VERIFICA):** usare screening Shapely di pad/segmenti/vie F.Cu solo come controllo geometrico preliminare; NON equipararlo a KiCad DRC con refill delle zone.
- **D-V55-02 (METROLOGIA):** distanza minima calcolata 0,45mm su cinque coppie di pad, non approvazione per soglia di fabbricazione; la soglia 0,30mm è analitica e da confrontare con stack-up/regole del fornitore.
- **D-V55-03 (REPORT):** richiedere sempre tutte e tre le classi DRC e la struttura ERC prima di considerare un report completo. JSON strutturalmente valido non comprova da solo esecuzione KiCad.
- **D-V55-04 (BLOCCO):** nove gate V5.0 ancora OPEN; nessun ordine PCB, Gerber approvato o TX autorizzata.

---
# Decisioni V5.4 — 8 novembre 2026

- **D-V54-01 (PROCESSO):** introdurre un runner KiCad 10 su copia e una procedura GitHub Actions solo manuale, per consentire report nativi quando l'infrastruttura sarà disponibile. Il workflow non è stato eseguito.
- **D-V54-02 (GATE):** l'esito favorevole dei test software con CLI simulate **non** vale come ERC/DRC; gli stati ERC/DRC/refill/parità sono attualmente NOT_RUN.
- **D-V54-03 (PROTEZIONE):** non autorizzare Gerber, PCBWay, assemblaggio, prototipo TX o TX senza chiusura documentata di tutti i nove gate.

---
## Registro V5.2 e precedenti

# Nota decisionale V5.2 — 8 novembre 2026

- D-V52-01: evidenziato disallineamento dei nomi delle istanze KiCad: V4.8 contiene il nome del progetto V4.5; creare solo copia non FAB con nomi allineati.
- D-V52-02: associare i 15 footprints ai 15 simboli mediante cammini UUID **solo nella copia V5.2**, da verificare con KiCad 10 nativo. Nessuna modifica a rame, pad o piste.
- D-V52-03: proibito dichiarare la parità verificata in assenza dei report nativi; gate produzione R-01...R-09 restano tutti OPEN.

---
## Registro V5.1 e precedenti

## V5.0 — studio stencil e gate di rilascio (8 novembre 2026)

- **DEC-V50-01 (STUDIO):** confronto U101 fra apertura attuale (81%) e due finestre alternate fra le file di vie (29,69%); non promuovere la seconda a stencil finale senza analisi saldatura/termica e consenso assemblatore.
- **DEC-V50-02 (GATE):** la variante V4.8 a sei via-in-pad è selezionata solo come ipotesi primaria per valutazione VIPPO riempimento/cappatura; nessuna approvazione ufficiale dal fabbricante è ricevuta.
- **DEC-V50-03 (CONTROLLO):** procedura native KiCad 10 su copia e report verificabili; l'assenza della CLI deve risultare NOT_RUN e non autorizzare produzione.
- **DEC-V50-04 (RILASCIO):** nove gate obbligatori OPEN. Non emettere Gerber/ordini; non abilitare TX; non aumentare il 37% senza evidenza progettuale/hardware misurata.
- **DEC-V50-05 (COLLAUDI):** validare il guadagno/adattamento ADL5535 nella fascia 25,615–28,305 MHz con misure reali, perché vicina al limite inferiore di banda del componente; piano RX-B01…B08 redatto, nessun test eseguito.

---
## V4.9 — DFM stencil/vie U101 (8 novembre 2026)

- **DEC-V49-01 (STUDIO, NON APPROVATO):** mantenere separate la V4.8 a sei vie e la V4.5 senza vie termiche nel pad; *nessuna* modifica a rame/maschera/pasta finché non sono concordati fabbricazione e assemblaggio.
- **DEC-V49-02 (BLOCCANTE):** i 6 fori via-in-pad della V4.8 attraversano geometricamente tutta l'apertura F.Paste in corrispondenza dei fori. Chiedere al fabbricante un processo di riempimento/cappatura planare e al montatore nuova validazione dello stencil; tenting non automaticamente equivalente a VIPPO.
- **DEC-V49-03 (BLOCCANTE):** la corrispondenza con capacità pubblicate PCBWay (foro Ø0,25 mm su PCB 1,6 mm) non è approvazione del nostro progetto. Richiedere conferma scritta di processi, tolleranze, stack-up e costi; non è stato inviato alcun ordine o documento.
- **DEC-V49-04 (GATE):** non rilasciare produzione senza DXF/STEP TE, ERC/DRC KiCad, parità schema-PCB, stack-up 50 Ω, analisi termica, stencil e BOM approvati. TX resta disabilitata.

---
## V4.8 — Esperimento via-in-pad ADL5535 (8 novembre 2026)

**Decisione**: creare una copia sperimentale e interamente reversibile del PCB con 6 nuove vie GND Ø0,55/foro0,25 mm all'interno del paddle U101; nessuna sostituzione del PCB di riferimento V3.8 o della V4.5, nessuna autorizzazione di produzione.

**Ragione**: Figura 17 ADL5535 Rev A richiede connessione termica con vias su piani GND; layout precedente non ha via con centro nel paddle. La variante è geometrica preliminare, non qualificata, e richiede via fill/cap, nuovo stencil, DRC/stack-up e misura termica.

**Blocchi**: KiCad native ERC/DRC non eseguiti, TE DXF/STEP non acquisiti, via-in-pad/stencil e stack-up non approvati, zero hardware collaudato. **NO FAB / NO PCBWAY / NO TX**.

---

# Registro decisioni (cumulativo)

| ID | Decisione | Stato | Motivo / Vincolo | Revisione |
|---|---|---|---|---|
| DEC-001 | Ricostruzione concettuale Superstar 3900 prevalentemente SMD | Confermata | Nuova radio con carattere vintage | V0.1 |
| DEC-002 | AM, FM, USB, LSB | Confermata | Continuità funzionale dell'originale | V0.1 |
| DEC-003 | Sei bande A–F, 270 frequenze RX | Confermata | 6 × (40+5) | V0.1 |
| DEC-004 | Interruttore ALFA fisico separato | Confermata | Usabilità vintage; Alfa su 3/7/11/15/19 | V0.1 |
| DEC-005 | Interruttore CH9 prioritario | Confermata | Richiamo 27,065 MHz AM; ripristino dello stato | V0.1 |
| DEC-006 | Ricevitore molto sensibile, selettivo e silenzioso | Confermata come obiettivo | Da dimostrare con budget e prove | V0.1 |
| DEC-007 | Frequenzimetro, wattmetro, ROS e modulometro | Confermata | Misure da calibrare | V0.1 |
| DEC-008 | Accordatore automatico con bypass | Confermata | Rete LC RF e protezioni da dimensionare | V0.1 |
| DEC-009 | PCB SMD ove tecnicamente appropriato | Confermata | Eventuali eccezioni motivate | V0.1 |
| DEC-010 | Assemblaggio previsto tramite PCBWay | Confermata | Richiederà DFM/BOM/posizionamenti compatibili | V0.1 |
| DEC-011 | Produzione documentazione cumulativa a ogni milestone | Confermata | ZIP intero, changelog, stato, verifiche | V0.1.1 |
| DEC-012 | Quattro fascicoli manuale finali e rapporti di collaudo | Confermata | Indici presenti, contenuto ancora in lavorazione | V0.1.1 |
| DEC-013 | RX 270, TX soggetto a limitazioni di legge e conformità | Vincolo preliminare | TX interbloccato anche via hardware | V0.1 |
| DEC-014 | PCB 4 layer, struttura modulare | Da validare | Potrebbero servire più schede o stack-up diverso | V0.1 |
| DEC-015 | Montaggio esterno identico all'originale | Da decidere | Servono telaio, forature, foto e misure | V0.1 |

Quando si cambia una decisione: aggiungere un record di modifica e indicare gli elaborati dipendenti da aggiornare.

## Decisioni/valutazioni introdotte in V0.2
- **D-020 (ipotesi di progetto, REVERSIBILE):** prima FI 10,695MHz, LO high-side da 36,310 a 39,000MHz, possibile seconda FI 455kHz per AM/FM.
- **D-021 (candidato non approvato):** ADF4351 SMD in Integer-N, 12,8MHz TCXO, R=20, PFD=640kHz, feedback VCO fondamentale, uscita /64, N=3631..3900. Misura phase-noise/spurie prima della scelta definitiva.
- **D-022 (candidato non approvato):** mixer primo stadio Mini-Circuits ADE-1+; LO +7dBm richiesto, prevedere buffer dopo filtro LO, matching da verificare.
- **D-023 (architettura di prova):** attenuazione RF selezionabile 0/10/20dB, LNA bypass, preselettori di banda, doppio sensore proposto ai lati dell'ATU.
- **D-024 (validato SOLO software):** modello CH9 (AM prioritaria) + ALFA fisico + interlock logico TX fail-closed: richiede scheda hardware e firmware collaudati prima di trasmettere.

## V0.4, decisioni provvisorie
- D-021 (PROVVISORIA) Filtro d'anello R2/C2,C1,R3/C3 6.8n/1.2k/120n/270R/4.7n su modello PFD+VCO linearizzato; non approvato per produzione.
- D-022 (PROVVISORIA) ADL5611 come buffer LO candidato: l'intervallo 36-39MHz e' incluso nella specifica. PHA-1+ rimosso dalla rosa primaria (min 50MHz).
- D-023 (APERTA) Qualificare rumore di fase e reciprocal mixing prima di approvare ADF4351; verifica importante ad fPFD=640kHz/N circa 3750.
- D-024 (APERTA) TCXO T200F-012.8M favorito SOLO per accuratezza, non approvato senza datasheet phase-noise e modello.

- **DEC-05, 2026-11-06, PROVVISORIA:** scegliere LMX2572 quale opzione principale di sintesi a basso rumore; non dismettere ADF4351. Motivazione: figure of merit bianco normalizzato di -232 anziche' -220 dBc/Hz e fPFD 1.28 anziche' 0.64 MHz, vantaggio modellato ~15.01 dB solo IN-BAND, con 270 canali esatti in Integer-N. Condizioni: progetto nuovo filtro d'anello, prova phase noise/spurie VCO/reference/buffer, verifica hardware prima di chiudere lo schema.

### V0.6 - 2026-11-06
- LMX2572 resta candidato principale, non approvato per PCB. Nuovo filtro di terzo ordine a valori ipotetici, vietato riciclare valori ADF.
- TCXO TXC 7N-12.800MBP-T candidato; selezione non vincolante finche non si verifica il phase noise e il datasheet originale.
- In VCO nominali TI, primo e secondo canale banda A sotto 4.65 GHz => core VCO3; tutti gli altri => core VCO4. Usare autocalibrazione, non forzare core.
- Interlock TX previsto se synthesizer unlock.

### DEC-V09-01 - due LDO separati (2026-11-06)
BOZZA: U2 3V3_PLL, U3 3V3_REF; entrambi da 5V pre-regolati. Non permettere ingresso 13.8V su TPS7A20.
### DEC-V09-02 - riferimento CMOS (2026-11-06)
BOZZA: Y1 TXC 7N 12.8MHz, LMX2572 OSCinP AC-coupled, OSCinM NC, pin10 e footprint bloccanti.


## V1.1 - 2026-11-06
- CW e PA aggiunti alla baseline dei requisiti; non ancora implementati.
- TPS26600PWPT scelto come candidato eFuse per il solo ramo ausiliario 5V, con nodi GND e RTN separati; fuses/TVS e controllo fault aperti.
- Schema KiCad di studio, non sottoposto a ERC. Non inviare a PCBWay.


## V1.2
- Fuse F200: Littelfuse 045101.5MRL **candidato**, non scelto definitivamente. Togliere footprint 1206 errato e tenere CUSTOM NON VALIDATO.
- TVS D200: SMBJ18CA **candidato DNP**, VRWM 18V; non dichiarare surge approvato.
- Uniformazione etichette 3 sottoschemi: `GND_MAIN`, `BUCK_VIN_PROTECTED`, `5V_RF_PREREGULATED`. `EFUSE_RTN` separato.
- TCXO: non connettere pin10 senza conferma part specifica AFC/GND.

## V2.4
Nessun preselettore approvato: HP5+LP9 resta solo candidato analitico; prossimo passo confronto con filtro commutato per bande e verifica S-parameters reali a 27 MHz.

## V3.8 — 2026-11-07
- Pad custom SMA sagomati: solo ipotesi, NON APPROVATI finche' mancano CAD ufficiale e confronto col part number.
- U101 PAD GND: nuova traccia verso via esterno, paste -0,10 provvisoria; test termici assenti.
- Non rilasciare PCB fino a KiCad DRC/zone refill reali; avanzamento 37% invariato.

## V3.9 — 2026-11-08
- Il disegno TE `C-CONSMA002-SMD-X-X rev D` comprende le varianti standard e `-G` (corpo oro). Non costituisce approvazione geometrica del footprint custom V3.8.
- Differenza nominale dell'inviluppo GND V3.8 (7,40 mm) rispetto a dimensione TE 7,76 mm: richiede revisione su CAD ufficiale. **NO FAB / NO PCBWAY**.

## V4.0 - 2026-11-08
- DEC-V40-01 (SCELTA SOFTWARE PROVVISORIA): modello di supervisione con 8 guard booleani strettamente tipizzati, tutti in stato negato per default; priorita' input invalidi, PA RF-OFF, CH9 AM, DW A/B solo RX secondario, TX mai CW. **Non costituisce autorizzazione RF e non e' firmware MCU.**
- DEC-V40-02 (DOCUMENTAZIONE): MU-01 illustrato BOZZA; non usare come manuale di un apparato validato. Tabelle RX generate da `02_Piano_Frequenze/Tabella_270_canali.csv`.
- Restano invariate le decisioni RF/PCB delle revisioni precedenti e il blocco NO FAB.

## V4.1 — 2026-11-08 — decisione di processo (approvata a livello documentale)

1. **Rilasci RF bloccati** finché la conformità meccanica TE del CONSMA002-SMD-G, la dissipazione ADL5535, il refill e DRC/ERC nativi, lo stack-up 50 Ω e i collaudi di laboratorio non hanno prove reali. Il verificatore statico V4.1 è documentazione, non approvazione.
2. **Conservare PCB V3.8 byte-identico**; la differenza geometrica SMA -0,36 mm non autorizza a correggere a mano la sagoma senza confronto con CAD produttore.
3. **Conservare lo storico e l'handoff cumulativo**: la V4.1 incorpora il contenuto V4.0 e tutta la catena precedente, oltre a snapshot dei documenti attivi modificati.
4. **Attenuatore RX sperimentale**: R201=150 Ω, R203=37,4 Ω, R202=150 Ω risulta teoricamente circa 6 dB su 50 Ω nel modello ideale; tolleranze/BOM, PCB e prestazioni RF rimangono da validare.

## V4.2 - 2026-11-08 - decisioni di processo

- DEC-V42-01 (APPROVATA DOCUMENTALE): usare audit geometrico shapely dei pad custom e rotazioni come filtro statico iniziale, **mai** come sostituto del DRC KiCad. 19 test con 0,45 mm minima inter-reti; 4 zone GND restano non riempite.
- DEC-V42-02 (APERTA/INGEGNERIA): non correggere a tentativi il footprint `CONSMA002-SMD-G` fino a import/approvazione CAD ufficiale; il disegno TE raccomanda 7,76 mm contro 7,40 mm nominali custom, differenza -0,36 mm.
- DEC-V42-03 (APERTA/INGEGNERIA): proibire dichiarazione impedenza 50 Ω per piste RF da 0,28 mm senza stack-up PCBWay approvato e modello CPWG. Simulazione microstrip illustrativa non è prova.
- DEC-V42-04 (APERTA/INGEGNERIA): ADL5535 thermal pad senza via-in-pad sul PCB V3.8 non certifica dissipazione; scegliere termica/paste con montatore, poi prova fisica.
- DEC-V42-05 (APPROVATA DOCUMENTALE): conservare PCB V3.8 immutato e tutti gli archivi/snapshot; NO FAB / NO PCBWAY / NO TX resta vincolante.

## V4.3 — 2026-11-08

- DEC-V43-01 (STUDIO, **NON APPROVATO**): la variante PCB V4.3 che allarga a 7,76 mm il solo inviluppo verticale GND degli SMA mediante ±0,18 mm ai centri delle 16 piazzole e' una prova di sensibilita' geometrica, **NON** un footprint TE verificato. Non sostituisce PCB V3.8.
- DEC-V43-02 (APERTO): CAD DXF/STEP TE non acquisito in questa sessione; non usare la corrispondenza di una sola dimensione per rilascio.
- DEC-V43-03 (APERTO): pad esposto ADL5535 ancora senza via interno; geometria termica e stencil da approvare col montatore.
- DEC-V43-04 (PROCESSO): controlli statici V4.3 non sono KiCad DRC. Eseguire DRC nativo con refill su copia, sincronizzare lo schema RX V3.1 obsoleto con V3.8/variante e richiedere stack-up approvato.
- DEC-V43-05 (GESTIONE): conservare tutte le sorgenti e snapshot; NO FAB / NO PCBWAY / NO TX.

## V4.4 — 2026-11-08

- **DEC-V44-01 (DOCUMENTALE/APPROVATA):** il modello schema RX V4.4 è un *candidato* generato dai pin sul PCB V3.8 e compatibile staticamente con le otto reti del PCB V4.3; mantiene 15 riferimenti, 31 pin e i valori/ID footprint. NON è netlist esportata da KiCad e non è uno schema rilasciato.
- **DEC-V44-02 (PROCESSO):** per accettare la sincronizzazione servono ERC, DRC refill, verifica parità KiCad UUID/pin e librerie di footprint complete; 20 test Python non sostituiscono tali prove.
- **DEC-V44-03 (APERTO):** acquisire/confrontare DXF/STEP e disegno TE del CONSMA002-SMD-G; non approvare V4.3 in base alla sola dimensione 7,76 mm.
- **DEC-V44-04 (APERTO):** qualificare pad exposed ADL5535, via stitching, piano massa, stencil e collaudo termico; ADI richiede paddle e pin 2 collegati al piano GND.
- **DEC-V44-05 (GESTIONE):** conservare V4.3 e tutte le revisioni precedenti, manuali e snapshot; **NO FAB / NO PCBWAY / NO TX**.

## V4.5 — 2026-11-08

- **DEC-V45-01 (APPROVATA COME PROCEDURA):** conservare le librerie di impronte portabili derivandole dal PCB candidato V4.3; le geometrie estratte restano non conformate CAD TE e NON approvate per fabbricazione. I footprint mantengono gli ID storici per collegare lo schema, ma la coincidenza di ID non qualifica il componente.
- **DEC-V45-02 (VERIFICA):** librerie V4.5 e schema/PCB candidato impiegano `fp-lib-table`, `sym-lib-table` e `${KIPRJMOD}`; per validare occorre l'apertura nativa KiCad, ERC, DRC con refill e parità schema-PCB. Test statici 26/26 non equivalgono a check nativi.
- **DEC-V45-03 (SICUREZZA):** nessuna modifica ai file sorgente storici, nessun Gerber, ordine PCBWay, TX, o dichiarazione di idoneità termica/RF. Conservare storico e handoff cumulativo.


## V4.6 — Decisioni di controllo (2026-11-08)

- **DEC-V46-01 (vincolante):** nessun DRC dichiarato come eseguito senza file di rapporto reale prodotto da KiCad; la procedura KiCad 10 si arresta se manca la funzione di refill delle zone.
- **DEC-V46-02 (rischio aperto):** U101 ADL5535 resta senza via-in-pad; il via esterno a 0,50 mm dal rame del paddle non prova la dissipazione. Nessuna modifica PCB approvata.
- **DEC-V46-03 (rischio aperto):** STEP/DXF ufficiali TE elencati sul sito ma non scaricati; niente approvazione SMA o fabbricazione.
- **DEC-V46-04 (continuità):** aggiornare anche il RIPRENDI secondario in `00_Gestione_Progetto/` quando cambia la versione, mantenendo snapshot dei documenti modificati.

## V4.7 — Decisioni di controllo (2026-11-08)

- **DEC-V47-01 (OPEN/NO FAB):** il disegno TE `C-CONSMA002-SMD-X-X` rev. D è la fonte dimensionale primaria; il confronto statico V4.7 conferma solo Ø2,05 mm del pad centrale e 7,76 mm di inviluppo verticale. Il CAD DXF/STEP esatto non è stato importato; resta non approvato il footprint personalizzato.
- **DEC-V47-02 (OPEN/ASSEMBLY):** per gli SMA controllare F.Paste/F.Mask e profili delle quattro isole con il montatore. Per ADL5535 qualificare pasta sul pad esposto e percorso termico (ratio -0,10 equivale a 81% area nominale di pasta nel modello, non volume misurato).
- **DEC-V47-03 (FAIL-CLOSED):** il rilascio richiede artefatti KiCad reali per ERC/DRC-refill/parità. `kicad-cli` mancante, quindi test nativi `NOT_RUN` anche nella V4.7.
- **DEC-V47-04 (GESTIONE):** proteggere schemi, PCB e librerie esistenti; conservare copie byte-esatte dei documenti attivi sostituiti e tutto lo storico; mantenere divieto **NO FAB/NO PCBWAY/NO TX** e stima 37%.


## V5.1 — Decisioni di continuità e gate (2026-11-08)

- **NON** modificare geometria del modulo RX; la BOM V5.1 è una lettura statica della variante V4.8, non una BOM approvata per acquisti.
- Conservare tutte le 9 condizioni di rilascio `OPEN`, vietare ordini PCB, generazione CAM esecutiva e abilitazione TX finché non arrivano verifiche native e autorizzazioni.
- Non attribuire al produttore accettazioni basate solo su capacità pubbliche: richiesta DFM V5.1 **non inviata** e nessuna risposta ricevuta.
- Richiedere su computer KiCad 10 veri report ERC/DRC/parità/refill, oltre ai modelli CAD TE per il footprint SMA e all'approvazione assemblaggio VIPPO/stencil U101.
- Continua obbligo revisione cumulativa con copie byte-identiche dei documenti gestionali sostituiti.

## V5.3 — Decisioni di controllo (2026-11-08)

- **DEC-V53-01 (controllo):** confrontare geometricamente i pin, fili, label e pad mediante parser indipendente; la V5.2 passa il controllo statico 15 componenti / 31 pin / 8 reti e tutte le 15 librerie locali corrispondono, ma non si dichiara ERC/DRC.
- **DEC-V53-02 (sicurezza):** `kicad-cli` assente; mantenere ERC/DRC/parità/refill `NOT_RUN` e 9 gate aperti. Nessun ordine PCBWay né abilitazione TX.
- **DEC-V53-03 (gestione):** nessun file CAD alterato, conservare originali V5.2, snapshot integrali dei 5 documenti aggiornati, manifest SHA-256 e istruzioni di ripresa V5.3.
