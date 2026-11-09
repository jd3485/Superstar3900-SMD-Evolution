# V6.8 — 9 novembre 2026

Nuovo modulo IF1 AGC AD8338, roofing LC di studio e doppia conversione IF2=455kHz, tabella 270×5, simulazioni 12k, 60 test nuovi e regressioni selezionate; conservato storico V6.7. NO FAB / NO TX.

---

## V5.8 — 2026-11-09 — diagnostica geometrica prossimità via GND delle piste RF (NO FAB)

- Analizzati 13 segmenti di 6 reti RF e 70 via GND, campioni ≤0,20 mm su ciascun segmento, bound distanza ≤0,10 mm; max centro-via 9,5811 mm su RF_ATTEN_IN, 6,9385 mm su RF_ATTEN_OUT. Dato NON equivalente a un return path, una violazione RF, un DRC o una regola produttiva.
- Generati verificatore `audit_ritorno_rf_v58.py`, CSV per rete, SVG diagnostico e sorgente, 30 test (incluse mutazioni), lanciatore KiCad 10 fail-closed e rapporto riproducibile.
- 30/30 nuovi test e 19/19 suite di regressione software. KiCad CLI non disponibile: ERC/DRC/refill/parità `NOT_RUN`, 9 gate produttivi OPEN.
- Nessun file KiCad, schemi, librerie, firmware e manuali modificati. Copie integrali dei documenti di gestione aggiornati.

---
## V5.7 — 2026-11-08 — contorno teorico piani GND, nessuna modifica al PCB (NO FAB)

- Studio geometrico su zone UNFILLED dei quattro layer: stima permissiva F.Cu 6.323,1039 mm² / 6.581,16 mm² (96,08%), una regione ideale per layer, 70/70 via completamente entro ciascun contorno, margine minimo del bordo rame-via al contorno 2,05 mm.
- Il modello non calcola fill KiCad, spoke termici, clearance netclass prevalente, min-neck, isole rimosse; nessuna prova di connessione RF reale né produzione.
- Test V5.7 30/30, regressioni V4.0–V5.7 18/18, runner KiCad locale NOT_RUN_KICAD_MISSING, workflow CI soltanto predisposto.
- Sorgenti KiCad, firmware e manuale illustrato immutati; 9 gate di rilascio V5.0 aperti.

---
## V5.6 — 2026-11-08 — continuità topologica del rame F.Cu pre-refill (NO FAB)

- Aggiunto audit indipendente delle isole F.Cu e delle connessioni dei pad, segmenti e via; sette reti non GND continue; 64 gruppi GND sul rame non riempito, di cui 24 con pad e 40 composti solo da via. 4 zone GND da riempire; il numero di gruppi non equivale a violazioni DRC.
- Identità statica del rame V5.2 vs variante termica V4.8 confermata senza modificare CAD.
- Nuovi test 23/23 e regressioni storiche 17/17; runner nativo V5.6 registra NOT_RUN_KICAD_MISSING, GitHub Actions manuale solo predisposta.
- Non chiusi i nove gate V5.0; nessuna autorizzazione PCBWay, PCB o TX.

---
## V5.5 — 2026-11-08 — clearance top-copper e validazione dei rapporti (NO FAB)

- Analisi geometrica indipendente `F.Cu` per 44 pad, 44 segmenti, 70 vie; 5.267 coppie cross-net; distanza minima 0,45mm, test soglia 0,30mm superato. Quattro zone GND UNFILLED, NON DRC.
- Postvalidatore di JSON KiCad 10 con protezione su ERC sheets, DRC violations/unconnected_items/schematic_parity e metadati; riporta espressamente che un JSON valido non autentica la provenienza.
- Runner e workflow CI manuale V5.5 pronti ma **NON ESEGUITI su KiCad reale**; KiCad locale assente; NATIVE_NOT_RUN.
- Test software 22/22 nuovi, regressioni V4.0–V5.5 16/16. Nessuna modifica a PCB, schema, librerie o manuale.
- Tutti i nove gate di rilascio V5.0 restano OPEN. Fabbricazione PCBWay e TX bloccate.

---
## V5.4 — 2026-11-08 — automazione KiCad 10 (NON eseguita nativamente)

- Sviluppato runner con report JSON ERC/DRC/refill/parità su copia, in modalità fail-closed.
- Preparata azione manuale GitHub Actions con KiCad 10 PPA ufficiale; NON pubblicata o eseguita.
- Test automatici con CLI simulate: 8/8; regressioni software dalla V4.0 alla V5.4: 15/15.
- `kicad-cli` locale assente: ERC/DRC/refill/parità NOT_RUN; nove gate ancora OPEN, 0 prototipi.
- Nessuna modifica a circuito stampato, schema, librerie o manuale; V5.3 conservata integralmente.

---
# Cronologia revisioni — cumulativa

## V0.2 — 2026-11-06 — Primo studio RF/PLL e test sistema
- Aggiunto studio architettura ricezione supereterodina e sintesi ADF4351 Integer-N con riferimento 12,8MHz e prima FI 10,695MHz.
- Generata tabella completa PLL 270 posizioni (`Tabella_PLL_270_Integer_N.csv`) con frequenza LO, VCO, INT/FRAC, errori calcolati.
- Creato prototipo di modello di controllo CH9, ALFA, modalità, TX fail-closed e modello budget rumore Friis; suite test a 4 script eseguite con PASS.
- Registrati componenti candidati con stato NON APPROVATO, checklist di convalida, piano PCBWay, diagramma blocchi SVG/DOT e registri di rischio.
- Nessun circuito KiCad, SPICE/EM reale, ERC/DRC o prova di laboratorio in questa versione.

## V0.1.1 — 2026-11-06 — Struttura di continuità e manualistica
- Copiati integralmente i contenuti tecnici di V0.1.
- Aggiunti: `STATO_PROGETTO.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `REGISTRO_DECISIONI.md`, questo registro revisioni, indice master dei manuali, cinque schemi di struttura dei fascicoli, tabella tracciabilità requisiti e procedura di rilascio.
- Rieseguito il test del piano frequenze: PASS.
- Nessuna topologia elettronica nuova, nessuna simulazione RF, nessun file KiCad o output PCB prodotto in questa revisione.

## V0.1 — 2026-11-06 — Avvio tecnico
- Capitolo requisiti preliminari, modello 270 frequenze, tabella CSV, test automatici del modello, registro preliminare verifiche, note KiCad e produzione.

## V0.3 - 2026-11-06
- Pinout ADF4351 32+EP verificato da datasheet ufficiale e proposta reti di controllo/alimentazione.
- Nuova BOM PLL/LO **candidata**, non idonea all'ordine.
- Modellato filtro LO 7 poli con matrici ABCD e Monte Carlo; grafico, CSV, JSON, netlist ngspice NON eseguita.
- 2 suite test aggiunte, per un totale di 6.
- Nuovi disegni e dossier Fase 2; archivi precedenti V0.1, V0.1.1 e V0.2 conservati integralmente come file delle versioni.

## V0.4 - 2026-11-06
- Aggiunto modello linearizzato CPLF, analisi 4.000 casi di sensibilita con grafiche e file di verifica.
- Candidati filtro d'anello (C1 6.8nF, R2 1.2k, C2 120nF, R3 270ohm, C3 4.7nF).
- Scartato PHA-1+ (min dichiarato 50MHz) per LO 36-39MHz; candidato ADL5611 (30MHz min), P1dB basso a 30MHz attentamente considerato.
- Proposta pad regolabili 50ohm, TCXO 12,8MHz candidati.
- Nessuno schema KiCad/ERC, nessun PCB e nessuna misura fisica; non producibile.

## V0.5 - 2026-11-06
- Confronto ADF4351 e TI LMX2572 limitato al contributo bianco normalizzato in banda; differenza calcolata 15.01 dB, NON valore di phase noise totale.
- Nuovo elenco esatto dei 270 setpoint PLL LMX2572 Integer-N, nuovo script di riproduzione e test regressivi.
- Esempio mixing reciproco e piano misure per sensibilita'/dinamica RX.
- LMX2572 promosso a candidato, filtro loop V0.4 ADF4351 mantenuto ma marcato NON trasferibile.
- Dossier V0.5 PDF; tutti gli ZIP precedenti preservati, incluso V0.4.

## V0.6 - 2026-11-06
- Aggiunto studio filtro loop 3° ordine LMX2572 (valori non produzione), test 4.000 campioni e codice ripetibile.
- Nuova pinmap TI 40 pin+DAP e schema funzionale, BOM candidata, TCXO TXC 12.8MHz.
- Studio cambio core VCO3/VCO4 sulla gamma 270 frequenze, stato lock e interlock TX.
- Manuale tecnico e gestionale aggiornati. Nessuno schematico KiCad/PCB/gerber prodotto.


## V0.7 - 2026-11-06
- Primo documento `.kicad_sch` di studio, simbolo 40+1 e primi 5 passivi filtro loop; pin map e libreria custom.
- Correzione documentata bypass TI per pin 3 e 27 rispetto a V0.6.
- Controlli struttura Python, non KiCad ERC.
- Note manualistiche, PDF tecnico, anteprima SVG.


## V0.8 - 2026-11-06
- Inseriti fisicamente nello schema KiCad bozza 6 bypass VCC (0R + 1uF), 7 condensatori su nodi Vreg/Vref/Vbias e 10uF sul rail comune.
- Rete 3V3 proveniente da LDO esterno ancora da progettare; non dichiarato un circuito alimentatore completo.
- Aggiunti controllo strutturale riproducibile, audit netlist logica e stima avanzamento 18% con pesi.
- NON effettuati ERC, DRC o misure, non ordinarlo a PCBWay.

## V0.9 - 2026-11-06
- Aggiunti 2 LDO 3.3V SMD separati, bypass 100n ai sei Vcc LMX2572, TCXO TXC con R serie e C di accoppiamento.
- Corretto pin OSCinM: esplicito NC per configurazione single-ended, software R5 da definire.
- Schema KiCad solo DRAFT senza ERC; footprint TCXO non validato; preregolatore 5V non presente.
- Aggiunti test, BOM, nuovo dossier e metodo avanzamento.

## V1.0 - 2026-11-06
- Creato foglio KiCad separato BUCK TPS54202 (6 pin DDC) basato su Figura 7-1 datasheet TI.
- Valori TI EVM, distinta componenti con codici candidati, rete nominativa pin-pin e script di verifica.
- Documentato chiaramente che protezioni input e integrazione non sono approvate; Vout ideale circa 5.077V.
- Nessuna PCB, ERC, DRC o simulazione SPICE; conservato archivio V0.9 per ripresa.


## V1.1 - 2026-11-06
- eFuse protezione front-end 13.8V ausiliario (schema, BOM, netlist, modelli statici).
- Requisiti ufficiali CW e PA con verifiche future e blocco TX in PA.
- Percentuale stimata 20.99% (arrotondata 21%); non incremento hardware.


## V1.2 - 2026-11-06
- Candidati F200 Nano2 451 da 1.5A e D200 SMBJ18CA; D200 DNP, nessuna qualifica surge.
- CORREZIONE: il precedente footprint 1206 del fuse F200 era dimensionalmente incompatibile con 451, ora segnaposto CUSTOM NON VALIDATO.
- Copie schemi EFUSE/BUCK/PLL uniformate nei nomi rete, contratto e test statici.
- TXC 7N pin10 AFC/GND resta BLOCCANTE; +2ppm iniziali nel datasheet di serie distinti da +-0.28ppm termici.
- Avanzamento circa 22%, non fabbricabile.

## V1.3 - 2026-11-06
- Preparata una gerarchia KiCad effettiva sul ramo ausiliario, con 3 fogli figli referenziati, pin gerarchici e collegamenti di filo nel foglio principale.
- Conservate note TCXO/fusibile e tutte le criticità note.
- Aggiunti report, test statici riproducibili, dossier tecnico e aggiornamento 22.70% (23% arrotondato).
- NON effettuati ERC KiCad, estrazione netlist nativa, SPICE, collaudi e fabbricazione.

## V1.4 - 2026-11-06
- Inserito J100 ingresso AUX 2-pin nello schema gerarchico, footprint da selezionare.
- Segmentate le sei wire delle alimentazioni PLL in corrispondenza delle label.
- Nuovo controllo geometrico di etichette/pin, controllo coerenza gerarchica; avanziamo con cautela, ERC nativo non eseguito.
- Avanzamento 23%, invariato dalla V1.3.

## V1.5 - 2026-11-06
- Integrazione J101 HOST SPI 3.3V a 6 pin nel foglio root; footprint ancora da definire.
- Pin gerarchici reali e relative etichette sul foglio LMX2572 per SCK,SDI,CSB,CE,MUXout.
- Codificatore e decoder Python a 24 bit e controlli di errore; gate per profilo registri esterno validato.
- Nuovi test riproducibili sulle reti e frame; nessun ERC nativo.
- Stato 23.58% stimato = 24% arrotondato.

## V1.5.1 - 2026-11-07 - Ampliamento requisiti richiesto dall'utente
- Nuove funzioni accettate: VOX, Dual Watch, Roger Beep, Echo, CTCSS 50 toni, DCS 104 codici N/I.
- Definita compatibilita FM per codici subaudio, priorita CH9/PA, interblocco TX e trasmissione sempre su primario A durante DW.
- Aggiornati manuali, matrice priorita, piano di prove e modello Python **solo logico** con test automatici.
- Nessuna modifica agli schemi KiCad e nessuna funzione dichiarata implementata sull'hardware; avanzo complessivo invariato al 24% arrotondato.

## V1.6 - 2026-11-07
- Studio MCU STM32G474RE e codec TLV320AIC3204 con fonti ufficiali e vincolo core 1.8V.
- Matrice reti AF/SPI senza assegnazione pin fisici; diagramma funzionale.
- Prototipo numerico e test CTCSS 50 toni, VOX, DW. DCS ancora assente.
- Manuali e registro avanzamento aggiornati a 25% stimato.
- Nessuno schema hardware audio/codec, simulazione RF/analogica o nuovo ERC completato.

## V2.0 - 2026-11-07
- C227 mic accoppiamento ridotto 1uF -> 100nF; C229 FM mantenuto 1uF per CTCSS/DCS.
- Calcoli trasferimento RC e sweep tolleranze riproducibili; filtri **non** certificati.
- Contratto SAI, rischi e priorita codec PGA / preamplificatore opzionale.
- Test v2.0 6/6. Nessun ERC, SPICE o PCB.

## V2.3 - 2026-11-07 - Compromesso NF/IIP3 ricevente
- Modello Friis e IIP3 con due LNA SMD reali ADL5535/ADL5536, mixer ADE-1+ e alternativa ADE-1H+.
- Confrontate 7 configurazioni, pad RF dopo LNA, percorso bypass e filtri distribuiti.
- Segnalata l'impossibilita' di assumere la reiezione immagine V2.2 con filtri suddivisi.
- 2000 casi di sensibilita' parametri per 4 varianti, 13 test + 6 suite regressione superate.
- Nessuno schema KiCad RF finale, ERC, PCB o collaudo. Avanzamento stimato 31%.

## V2.4
Studio quantitativo LP7/LP9/LP11 e HP5+LPx (ABCD 50 ohm), 1200 test Q/tolleranze, 7 unit test, netlist SPICE NON eseguita; risultato nominale non soddisfa entrambi i requisiti RF. Nessuna validazione hardware/PCB. Stima 32%.

Verifiche selettive V2.4: 7 test rete, 13 test V2.3, test piano 270 frequenze e test LMX del piano frequenze superati. Nessun ERC/DRC o banco VNA.

Verifiche selettive V2.4: 7 test rete, 13 test V2.3, test piano 270 frequenze e test LMX del piano frequenze superati. Nessun ERC/DRC o banco VNA.

### V2.5 - 7 novembre 2026
- Studio preselettore commutato a sei bande con model-based S11/S21 e stima bilancio NF.
- Confronto due tecnologie commutazione, 3.000 campioni perturbativi, 15 test nuovi, 7 di regressione.
- NO-GO: prestazioni RF reali, impedenze dei dispositivi, perdita commutatori e topologia finale aperte.
- Documentati candidati e sorgenti industriali, percentuale stimata 33%.

## V2.7 (2026-11-07)
Valori E12/E24 e Q prudente; due netlist SPICE di studio, distinta provvisoria e piano VNA. 34% stimato; NO GO per fabbricazione.

## V2.8
- LP7 con due L||C in serie, HP3 opzionale, analisi di blocker HF, 2400 stress numerici, 11 test, dossier e BOM preliminare. Avanzamento stimato 35%; NO-GO PCBWay.

## V5.3 — 2026-11-08
- Parser indipendente dei simboli/collegamenti e footprint KiCad: 15 componenti, 31 pin, 8 reti, zero incongruenze statiche rilevate.
- 18 test nuovi + 14 suite di regressione. Nessun sorgente CAD modificato; KiCad native NOT_RUN.
- Documenti di handoff e registri aggiornati con snapshot originali. 9 gate OPEN, NO FAB / NO TX.
