# Accettazione CAD V3.9 — procedura operativa (NON ESEGUITA)

## Oggetti di lavoro
- PCB baseline: `04_KiCad/Modulo_RX_Test_50ohm_V3.8/S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb`
- Schema e crosswalk reti V3.1: `04_KiCad/Modulo_RX_Test_50ohm_V3.1/`
- Risultato indipendente: `03_Verifiche/V3.9/Esito_Confronto_Footprint_V3.9.json`

## Documenti primari (verificati il 2026-11-08)
1. TE product page, **CONSMA002-SMD-G**: https://www.te.com/en/product-CONSMA002-SMD-G.html
2. TE Customer Drawing **C-CONSMA002-SMD-X-X rev D**, foglio 2 (link `Product Drawings` nella pagina precedente). Il disegno include le varianti nickel e oro. Il foglio 2 indica Ø2,05, Ø4,56 e 7,76 mm: controllare tutte le quote e il significato esatto dei contorni con il CAD di fabbrica prima di modificarli.
3. TE CAD: link `Customer View Model` 2D DXF e 3D STEP nella stessa pagina; risorse del produttore da acquisire secondo le condizioni d'uso.
4. Analog Devices ADL5535 datasheet rev A: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
5. KiCad 9 CLI: https://docs.kicad.org/9.0/en/cli/cli.html
6. KiCad 10 CLI: https://docs.kicad.org/10.0/en/cli/cli.html

## Fasi e criteri di chiusura
1. **Footprint SMA**: importare DXF/STEP ufficiali, confermare punto d'origine, centro RF, contorni GND, passo, Mask/Paste, courtyard, altezza e corpo fuori bordo. In V3.8 le quattro pad GND candidate occupano 7,40 mm in Y, a fronte dei 7,76 mm indicati nel disegno consigliato: lo scostamento e l'interpretazione della sagoma sono **bloccanti**.
2. **U101 ADL5535**: approvare land SOT-89 e paddle 1,80 × 3,48 mm contro datasheet e linee di assemblaggio. Esaminare la riduzione pasta -0,10, assenza di via aperti sul paddle, percorso di dissipazione e temperatura; non equiparare la traccia al pad a prova termica.
3. **Caricamento in KiCad**: lavorare su una COPIA del PCB; registrare versione KiCad, esito di caricamento e delle librerie. Verificare mapping di tutte le reti e presenza di zone, stack-up e vincoli.
4. **Refill delle 4 zone**: in KiCad 9 effettuare refill in PCB Editor e SALVARE la copia. Esaminare isole orfane, via GND, clearance e continuità dei ritorni. Il solo comando DRC CLI KiCad 9 non preserva il refill.
5. **DRC nativo**: su copia salvata, eseguire per KiCad 9:

   `kicad-cli pcb drc --severity-all --exit-code-violations -o report_drc_v39.txt "copia_validazione.kicad_pcb"`

   Per KiCad 10, previa conferma da `kicad-cli pcb drc --help`, sono documentate opzioni `--refill-zones --save-board` (usare solo su copia). Salvare log, output JSON se necessario, numero errori/avvisi e giustificazione di esclusioni. Nessuna violazione bloccante può essere accettata.
6. **ERC e schema**: `kicad-cli sch erc --severity-all --exit-code-violations -o report_erc_v39.txt "schema.kicad_sch"` sullo schematico vero; controllare pin/footprint e confronto nets PCB-vs-schema. Le 31 assegnazioni testate da Python non sostituiscono l'ERC.
7. **Stack-up e RF**: ottenere da PCBWay stack-up fisico L1-L2, rame e dielectric reale, finitura e specifica impedenza 50 Ω; ricalcolare geometrie microstrip/coplanari. Validare interfaccia SMA, ritorni di massa, S11/S21 con VNA e segnali di laboratorio a bassa potenza.
8. **Produzione**: solo dopo accettazione CAD, DFM e test hardware, autorizzare Gerber, drill, BOM e pick-and-place. RX di banco con TX fisicamente scollegata.

## Evidence pack richiesto
Allegare: screenshot KiCad della footprint e della scheda, report ERC/DRC nativi dopo refill, vista 3D quotata, tabella di corrispondenza pad-cad TE, stack-up approvato, verifica mask/paste e log di test VNA/RX. Una casella senza prova resta **APERTA**.
