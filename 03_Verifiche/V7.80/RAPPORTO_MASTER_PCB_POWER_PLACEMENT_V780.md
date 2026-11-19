# V7.80 — PRIMO MASTER PCB KiCad, posizionamento alimentazioni (WIP, NO FAB)

**Ambito reale:** `03_Verifiche/V7.80/build_master_power_placement_v780.py` carica la netlist **KiCad9 nativa a sette fogli** del master V7.79 (141 componenti /103 reti). Per il **medesimo PCB master**, colloca 25 footprint reali fisici della catena **J100 → F200 → U200 eFuse → U100 TPS54202 → L100 → C103/C104 uscita 5V**, e gli elementi eFuse/buck relativi (resistenze soglia/ILIM/MODE, bootstrap, bypass). Associa ogni pad alla rete effettiva del circuito sorgente, senza inventare nomi o ponti fra domini. La cartella di output definitiva prevista è `04_KiCad/PCB_MASTER_V7.80_POWER_PLACEMENT_WIP/S3900E_MASTER_V780_STAGING_NO_FAB.kicad_pcb`. **È una prima PCB unica INCOMPLETA, non un coupon e non un layout di radio assemblabile.**

## Decisioni fisiche preliminari

- Distribuzione provvisoria per flusso di potenza da sinistra a destra; piazzamento di C200 vicino ingresso eFuse, C100/C101 vicino ingresso buck, L100 tra SW e uscita, C103/C104 a valle. Posizioni provvisorie; verificare dimensioni di courtyard, loop ad alta di/dt, termica, distanza da RF/PLL, rientri ground e regole meccaniche prima di routing.
- Ogni footprint viene caricato tramite **pcbnew KiCad9** dalle librerie reali standard/vendor del repository. `U200` usa il nuovo TI PWP0016H candidato V7.78, con `EP17` su `EFUSE_RTN`, separato da `GND_MAIN` pin9. F200 effettivamente in serie, non shuntato. I componenti con pad senza rete (NC) restano NC.
- `D200` TVS DNP non viene incluso nel posizionamento finché protezione transitori non qualificata; `J6201` SWD esiste nel master schematico V7.79 ma posizione meccanica da decidere con la MCU.
- **Non sono presenti** outline `Edge.Cuts`, stack-up approvato, piste, via, zone, piani di massa, Gerber, drill per produzione, clearance finale, enclosure/antenna o moduli RX/MCU posizionati. 25/141 è solo un **conteggio di impronte piazzate**, non percentuale progettuale.

## Verifiche e blocchi

Il test genera, salva e **ricarica** con pcbnew una vera `.kicad_pcb`, conta footprint e reti, assicura ogni pin dello schema presente nei pad e conserva `J100`, `F200`, `U200` e `U100` esistenti; verifica esplicitamente separazione `EFUSE_RTN`/`GND_MAIN`. La CI esegue **DRC nativo** come report diagnostico intenzionalmente **NON RELEASE**: possono e devono rimanere errori (unrouted, board outline assente), che NON vengono waived, mascherati o chiamati superati. Output/test devono risultare in CI prima del merge; il PCB generato va **salvato nel repository**, non soltanto negli artifact di CI.

**Gate fabbricazione:** RIMANE BLOCCATO: sorgente 13,8V, F200 thermal/I²t e fusibile-eFuse, TVS D200 DNP, reset SHDN e ESD, Ceff/loop TPS54202, carichi LDO, ritorni 5V/3,3V/PLL separati, 15 interfacce OPEN/HOLD, pin TCXO, filtraggio RF, RX/TX, schema completo, board outline, DRC reale e revisione indipendente. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

**Prossimo lavoro:** stabilire vincoli PCB reali (contorno e fissaggi, passaggi cavi, massa chassis, stackup, antenna e thermal), qualificare BOM mancante e completare lo schema, quindi portare gli elementi in board uno per volta con prove pin-net/DRC. Non collegare masse o domini unicamente perché le etichette coincidono.

## Verifica DRC e correzione fisica V7.80 (19/11/2026)

CI tecnica [44494157209](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/44494157209) **SUCCESS**. PCB native pcbnew KiCad9 rigenerata da netlist 7sheet, controllo anche sul file realmente versionato: **25 footprint**, **0 piste / 0 zone / 0 Edge.Cuts**, **50 connessioni elettriche non instradate**. Primo DRC aveva **1 errore invalid_outline e 1 warning silk_overlap U100**. Spostato **solo** il testo reference U100 a (113,36) mm: DRC diagnostico risultante **1 errore invalid_outline** e **50 unrouted**, zero altri warning segnalati; è intenzionalmente **NON PASS DRC**, non è fabbricabile. Il file PCB definitivo del ramo deve coincidere con il byte stream del job tecnico e superare nuova verifica dopo il commit. Nessun falso waiver o cambio di rete.
