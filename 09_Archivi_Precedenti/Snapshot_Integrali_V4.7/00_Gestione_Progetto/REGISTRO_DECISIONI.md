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
