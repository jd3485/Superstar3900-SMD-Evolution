# V7.36 — C6231 Murata GRM155R71C104KA88D 100nF/16V X7R 0402 — REVIEW / NO FAB

Data 12 novembre 2026. Baseline GitHub **V7.35 PR#38 MERGED** (squash `24ae2dd93fed694980dab1fe68e55fabf4ba9ebe`); 134 componenti, 101 reti, 34 footprint mancanti, ERC 36 errori / 221 warning. Qui si qualifica in modo preliminare **solo** C6231, bypass U6207 TPS3840PL30DBVR, senza altre ECO o varianti RX/TX.

## Identità e fonti

- **Murata MPN GRM155R71C104KA88D**: 0.1µF nominali, ±10%, X7R (−55 a +125 °C, deriva classe ±15%), 16VDC, dimensioni **1.0×0.5×0.5mm**, codice Murata **GRM155** / EIA **0402** (metrico 1005). Il suffisso D è la confezione reel. Fonte Murata serie/part number: https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM155R71C104KA88-01.pdf ; catalogo Murata aggiornamento 6 ottobre 2026 https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM155R71C104KA88J%22%5D&partnumbers=%5B%22GRM155R71C104KA88%22%5D&rgear=suaykx&rgearinfo=com (serie **In Production**). Distribuzione con variante completa GRM155R71C104KA88D su https://www.mouser.it/it/ProductDetail/Murata-Electronics/GRM155R71C104KA88D .
- **TI TPS3840 SNVSB03E**, §7.3.1: raccomanda bypass vicino a VDD **0.1–1µF** dove alimentazione rumorosa; C6231 nominale 100nF coerente con bordo inferiore del consiglio TI, non basta però provare il minimo sotto bias. Fonte https://www.ti.com/lit/ds/symlink/tps3840.pdf .
- **Murata JEMCGC-2701X p.26, Table2 Reflow**, fonte parte sopra, per GRM15 1.0×0.5 mm e toll. dimensionale entro ±0.10 mm: distanze consigliate `a=0.3–0.5mm` (gap interno tra pad), `b=0.35–0.45mm` (lunghezza pad), `c=0.4–0.6mm` (larghezza pad). Scelti nominalmente **a0.40, b0.40, c0.50** mm → centri pad **x=±0.40mm**, dimensioni **0.40×0.50mm**, gap 0.40mm. **Non** riutilizzato footprint di R6201–R6208 Yageo senza verifica. Murata richiede prova sulla PCB effettiva per stress e solder fillet.

## Modifica CAD reale controllata

- Footprint nuovo `04_KiCad/Librerie_Footprint_V7.36_MURATA_GRM15_HOLD/S3900E_Murata_Review.pretty/MURATA_GRM15_0402_REFLOW_REVIEW.kicad_mod` (2 pad numerati 1/2), id `S3900E_MURATA_GRM15_V736_HOLD:MURATA_GRM15_0402_REFLOW_REVIEW`.
- MCU V7.36 `04_KiCad/Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/`: modificata **solo** la proprietà Footprint di C6231 e aggiunta proprietà `MPN` nascosta. Valore nominale `100nF` mantenuto; un terminale su `3V3_CODEC_IO`, altro su `GND`; nessuna modifica delle reti. U6207 e tutti i componenti V7.35 invariati.
- Master 7 fogli V7.36 `04_KiCad/Assemblaggio_RX_Power_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/` e collegamento fp-lib-table: mantiene AUX/RX e tutti i precedenti 133 componenti.
- Test `03_Verifiche/V7.36/test_murata_c6231_native_v736.py` richiede **pcbnew.FootprintLoad** nativo 2 pad esatti, netlist/ERC prima e dopo: target 134 componenti, 101 reti, **zero delta nodi pin–rete**, sola assegnazione C6231, missing footprint **34→33**, nessuna crescita degli errori ERC (baseline 36/221), nessuna soppressione warning. CI mirata `.github/workflows/v736_murata_c6231_native.yml` senza apt/pip, con run e artefatto da riportare **solo dopo esecuzione effettiva**.

## Vincoli di qualifica irrisolti

**DC bias:** i 100nF non sono necessariamente **≥100nF effettivi** a 3.3V perché MLCC X7R subisce DC-bias, temperatura, tolleranza e aging. Murata fornisce curve tipiche su SimSurfing, ma non è stata ricavata una garanzia minima numerica verificabile per `GRM155R71C104KA88D` a tensione DC 3.3V e in tutto l'intervallo. Qualifica signoff **HOLD** su `C_eff(3.3V,T,aging)` e tolleranza; si può valutare 220nF/1uF in package adatto se il minimo TI deve risultare garantito anche nel peggiore caso (richiede una nuova ECO del valore e test startup). Non dichiarare 100nF garantiti per ogni condizione.

Rimane inoltre **HOLD** su posizione concreta C6231 vicino VDD pin2 U6207, ritorno GND corto/impedenza e loop area, CT pad5 parasitic, clearance/3D/DFM, comportamento del pin RESET_N in regione `VDD<VPOR`, compatibilità EN U6206 e sequenza ALDO/RESET in brownout. Nessuna reale PCB completa, DRC, misura hardware o simulazione definitiva. **NO FAB / NO GERBER / NO PCBWAY / NO TX; 15 interfacce crossmodule OPEN/HOLD, SG48 e Y1 TCXO pin10 HOLD**.

Impatto sul progresso generale stimato PCB: **nessuna variazione percentuale attribuita alla sola impronta** (~10% storico).
