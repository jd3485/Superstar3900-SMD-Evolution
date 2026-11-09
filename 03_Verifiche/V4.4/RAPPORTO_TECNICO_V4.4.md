# Superstar 3900 SMD Evolution — Rapporto tecnico V4.4
**Data:** 8 novembre 2026 · **Stato:** BOZZA / NO FAB / NO PCBWAY / NO TX

## Obiettivo e risultato verificato

Questa revisione crea uno **schema RX sperimentale V4.4** che ricostruisce le reti del modulo a 50 Ω dai pad del PCB **V3.8 originale**. La variante SMA V4.3 mantiene invariata la netlist: i collegamenti ricostruiti sono equivalenti per entrambi i PCB. Il nuovo schema è una **copia di studio**, non una scheda elettrica approvata.

| Parametro | Esito statico V4.4 |
|---|---:|
| Riferimenti presenti su PCB e schema | **15/15** |
| Pin elettrici univoci confrontati | **31/31** |
| Reti distinte | **8** |
| Valori / ID footprint riportati | **15/15** |
| Errori di mapping individuati | **0 nel modello** |
| Test unitari V4.4 | **20/20 PASS** |
| Regressione V4.3, V4.2, V4.1 | **21/21, 19/19, 12/12** |
| Supervisore software V4.0 | **2.400 stati verificati** |
| ERC, DRC nativi, parità con PCB | **NON ESEGUITI** |
| Collaudo hardware | **0 moduli** |

**Differenze sistemate nella nuova copia, non nel vecchio schema:** le etichette `RF_LNA_IN` → `RF_LNA_INPUT` e `RFOUT_BIAS` → `RF_BIAS_OUT` sono ricostruite direttamente dalle reti del PCB; vengono valorizzati i campi `Footprint` dei 15 simboli, e il valore visualizzato J105 ora coincide con il PCB. Lo schema originario V3.1 non è modificato.

## Circuito di prova documentato

**Tratto LNA (J101 → J102):** `J101.1 RF_LNA_INPUT` → `C101 100 nF` → `RF_LNA_IC_IN` → `U101 ADL5535` → `RF_BIAS_OUT` → `C102 100 nF` → `RF_LNA_OUT` → `J102.1`. Alimentazione di U101 dal nodo `+5V_BENCH` mediante `L101 470 nH` verso `RF_BIAS_OUT`; condensatori verso massa `C103 68 pF`, `C104 1,2 nF`, `C105 1 µF`. Massa di U101: pin 2 e pad exposed paddle, con lo stesso numero di pad 2 nel PCB.

**Tratto attenuatore indipendente (J103 → J104):** `J103.1` su `RF_ATTEN_IN` con `R201 150 Ω` a `GND_RF`; `R203 37,4 Ω` in serie a `RF_ATTEN_OUT`, e `R202 150 Ω` a massa su uscita; `J104.1` in uscita. I due percorsi sono fisicamente circuiti di prova separati, non un ricevitore completo. Nessun percorso di trasmissione RF.

Le connessioni corrispondono allo schema di collegamento di base riportato nel datasheet ADI, Fig. 16 e Tab. 5 (20–1000 MHz); non dimostrano stabilità RF, adattamento o integrità alle frequenze d'uso. Riferimento: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf

## File creati

- `04_KiCad/Modulo_RX_Test_50ohm_V4.4_SCHEMA_MATCH/S3900E_RX_TEST_50R_V4_4_MATCH_NETS_NOT_FOR_FAB.kicad_sch`: schema sperimentale v20231120, 15 simboli copiati dai modelli V3.1 e 31 collegamenti nominati ricostruiti dai pad PCB.
- `03_Verifiche/V4.4/NETMAP_RX_PCB_V4.4.csv`: matrice pin-per-pin (31 righe).
- `03_Verifiche/V4.4/sincronizza_schema_rx_v44.py`: generatore riproducibile che si blocca se cambia l'hash del PCB originario o se le netlist V3.8/V4.3 divergono.
- `03_Verifiche/V4.4/test_schema_pcb_v44.py`: test e prove di rilevamento degli errori introdotti intenzionalmente.
- `03_Verifiche/V4.4/VERIFICA_SCHEMA_PCB_V4.4.json` e regressioni: prove del confronto **statico**, non ERC.
- `03_Verifiche/V4.4/RUN_KICAD_RX_V4_4.sh`: esegue ERC e DRC su copie di schema e PCB, senza Gerber. In questa sessione produce `BLOCKED` perché `kicad-cli` non è installato.

## Criticità non risolte (bloccanti)

1. **ERC e DRC nativi:** KiCad non disponibile, 4 zone GND nel PCB non riempite. L'esistenza dei file sorgenti **non equivale** alla verifica native.
2. **Parità KiCad e associazioni simbolo/footprint:** confronto di 31 pin/8 reti positivo, ma non sono ancora verificati gli identificatori schematica-PCB, l'integrazione di progetto e il risultato `--schematic-parity`. Lo schema usa simboli locali con pin definiti `passive`; vanno qualificati i tipi elettrici prima di validare ERC.
3. **Librerie di footprint:** il PCB contiene footprint incorporati. I riferimenti `S3900E_v33` e `S3900E_v35` non risultano tutti accompagnati da una libreria `.pretty` autonoma nell'archivio; non sono ancora garantiti aggiornamenti dal progetto schematico senza ricostruzione della libreria. Non sostituire automaticamente con footprint generici.
4. **SMA TE CONSMA002-SMD-G:** il disegno prodotto Rev. D e DXF/STEP sono elencati sul sito TE, ma il confronto CAD quotato **non** è stato eseguito. La geometria SMA V4.3 resta sperimentale; l'originale V3.8 conserva l'ingombro precedente. Riferimento: https://www.te.com/en/product-CONSMA002-SMD-G.html
5. **ADL5535:** exposed paddle U101 1,80 × 3,48 mm, senza via sotto il pad nel PCB studiato; pin 2 e paddle sono GND, ma rete termica, via, paste e temperature di giunzione non sono approvati. ADI Fig. 17 richiede paddle + pin 2 saldati al piano di massa e cucitura dei piani con via. Per 5 V e 97 mA tipici, la potenza assorbita elettrica è circa 0,485 W (non è una misura della dissipazione nel die). Valutazione termica basata su PCB reale e test di banco ancora indispensabile. Fonte: datasheet ADI citato sopra.
6. **Stack-up / 50 Ω:** mancano spessori rame e dielettrico, epsilon_r, gap coplanare, modello della via/transizione SMA, parametri effettivi PCBWay e misure VNA.
7. **Assemblaggio e prova:** BOM/MFR, via-in-pad o via esterne, stencil, reflow, test plan RF, alimentazione protetta 5 V e limiti di temperatura ancora da approvare.

## Procedura di avanzamento consigliata (V4.5)

1. Stabilizzare le librerie di footprint in una cartella `.pretty` autonoma, riconciliando dimensioni/pad con il PCB, senza alterare l'originale.
2. Importare i CAD ufficiali TE e confrontare footprint SMA con tutte le quote (incluse mask/paste, segnale e bordo scheda).
3. Progettare e valutare la dissipazione dell'ADL5535 su variante di studio; definire parametri termici e criterio di collaudo.
4. Eseguire l'ERC nativo sulla copia V4.4, DRC con refill su copia PCB; ricollegare correttamente i simboli ai footprint e ottenere report di parità.
5. Solo dopo: definire stack-up e dimensionare realmente le linee RF, poi prototipo, misure e eventuale fabbricazione autorizzata.

**Controllo amministrativo:** tutte le revisioni precedenti e il manuale illustrato V4.0 sono mantenuti nello ZIP cumulativo; nessun sorgente PCB V3.8 o V4.3 è modificato. Avanzamento complessivo rimane **37% stimato**; zero hardware collaudato, nessun file di produzione fabbricabile.
