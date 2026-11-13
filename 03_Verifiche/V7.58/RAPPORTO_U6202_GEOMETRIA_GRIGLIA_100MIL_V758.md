# V7.58 — ECO geometrica reale U6202 TLV320AIC3204 su griglia 100 mil

**13 novembre 2026 — REVIEW_NOT_FOR_FAB.** Questo è un intervento reale al simbolo KiCad MCU/CODEC, non ai soli metadati BOM. Baseline CAD [V7.57 integrata](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/67).

## Problema

I report KiCad9 rilevano un `endpoint_off_grid` associato in modo non deterministico al codec U6202 (a seconda dell'ordinamento pin7 IOVSS o pin15/16 ingressi). Issue [#63](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/63). Il simbolo in sorgente `04_KiCad/Modulo_MCU_CODEC_V7.48_TDK_2_C0G_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` aveva centro (400.0000,160.0000)mm; pin ai bordi x351.7400/448.2600mm e ordinate a passo 3.8100mm. Le ordinate e ascisse non erano tutte multipli del passo 2.54mm (100mil). Gli endpoint sono etichettati DIRETTAMENTE sul pin, senza tratti di filo: spostare solo il simbolo avrebbe perso la connettività.

## Modifica proposta nativa

La nuova copia versionata `04_KiCad/Modulo_MCU_CODEC_V7.58_U6202_100MIL_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` sposta **SOLO** il simbolo U6202 di +1.32 mm X e +0.02mm Y: centro (401.3200,160.0200)mm. Tutti e 33 i pin vengono riposizionati in Y con arrotondamento alla griglia 2.54mm, preservando numeri, funzioni, tipi, nomi e lunghezza 5.08mm. Le **24 label e 9 NC** già presenti ai pin sono riposizionate alle nuove coordinate reali su griglia (X=353.0600/449.5800mm). Nuova root `04_KiCad/Assemblaggio_RX_Power_V7.58_U6202_100MIL_GRID_REVIEW_NOT_FOR_FAB/` aggiorna solo il file del foglio MCU; AUX/RX, librerie e project tables identiche. Nessun pin/filo di altri componenti è mosso. La rappresentazione grafica potrebbe richiedere una successiva revisione estetica per spaziatura diseguale dei nomi; NON è un layout PCB.

## Criterio di integrazione

`03_Verifiche/V7.58/test_codec_u6202_100mil_grid_native_v758.py` richiede due veri `kicad-cli` KiCad9 sullo stesso runner: netlist/ERC precedente V7.57 e nuovo V7.58 a sette fogli. **139 componenti, 102 reti, esattamente identiche tutte le corrispondenze pin→rete**, EP33 e GND/codec, distacco U200 RTN/GND, SHDN NC; nessun cambiamento footprint e BOM. Necessaria RIDUZIONE DI UNO del warning `endpoint_off_grid` U6202: **28 errori/222 warning → 28 errori/221 warning**, con identità dei rilievi ERC rimanenti al di fuori di U6202. Il gate non sopprime nessun avvertimento né aggiunge `PWR_FLAG`; se i risultati nativi non soddisfano l'invariante, la PR resta BLOCCATA e la revisione va corretta.

**HOLD persistenti:** 28 errori ERC di cui label sospese e sorgenti alimentazione non qualificate; 15 interfacce crossmodule OPEN, eFuse reset indipendente Issue [#57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) ancora SHDN NC, capacità effettiva buck DC-bias non verificata, SG48 e Y1 pin10 HOLD. PCB completa assente, nessun DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
