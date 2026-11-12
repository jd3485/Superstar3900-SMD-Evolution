# V7.35 — Qualifica land TI DBV0005A per U6207 TPS3840PL30DBVR (REVIEW / NO FAB / NO TX)

Data 12 novembre 2026. La revisione **V7.34 è integrata su main**: PR#37 squash `5e744addf40040f074980323e38156ec88bba4de`, native run 43256127182 e policy run 43256126821 **SUCCESS**, 134 componenti, 101 reti, ERC 36 errori +221 warning. V7.35 è una ECO **meccanica/simbolo-footprint soltanto**, NON cambia la funzione del supervisore o la netlist.

## Produttore, package e fonte dimensionale

- TI TPS3840PL30DBVR, variante **PL push-pull active-low**, soglia 3.0V nominale, package **SOT-23 (DBV) 5-pin**, status **ACTIVE**: https://www.ti.com/product/TPS3840/part-details/TPS3840PL30DBVR .
- Datasheet primario TI SNVSB03E Rev. E maggio 2026, §5, Fig. 5-1 / Table 5-1 (p4): https://www.ti.com/lit/ds/symlink/tps3840.pdf .
- **Land pattern TI DBV0005A**, drawing 4214839/K, 08/2024, *Example Board Layout* (p2): https://www.ti.com.cn/lit/ml/mpds018t/mpds018t.pdf . Pad Cu reflow TI: **5 × (1.10 mm x 0.60 mm)**, pitch verticale **0.95 mm**, centri colonne x = **±1.30 mm** (separazione x2.60 mm), distanza tra righe estremali y1.90 mm. Numerazione in vista dall'alto: **1/2/3 a sinistra dall'alto verso il basso, 5/4 a destra alto/basso**. Solder mask NSMD preferita, disegno fornisce R0.05mm corner.
- Footprint review nel repository: `04_KiCad/Librerie_Footprint_V7.35_TI_TPS3840_DBV5_HOLD/S3900E_TPS3840_Review.pretty/TI_DBV0005A_5PAD_REFLOW_REVIEW.kicad_mod`, footprint ID `S3900E_TPS3840_DBV5_V735_HOLD:TI_DBV0005A_5PAD_REFLOW_REVIEW`.

| Pad | Funzione del supervisore TPS3840PL | Centro X/Y (mm) | Copper (mm) |
|---|---|---|---|
| 1 | RESET_N push-pull | −1.30, −0.95 | 1.10 × 0.60 |
| 2 | VDD | −1.30, 0 | 1.10 × 0.60 |
| 3 | GND | −1.30, +0.95 | 1.10 × 0.60 |
| 4 | MR/NC (aperto intenzionalmente) | +1.30, +0.95 | 1.10 × 0.60 |
| 5 | CT (aperto intenzionalmente) | +1.30, −0.95 | 1.10 × 0.60 |

La numerazione fisica resta coerente con la V7.34 (U6207 pin1→`CODEC_LDOIN_EN_SUPERVISED`, pin2→`3V3_CODEC_IO`, pin3→`GND`). Solo `U6207` riceve la nuova proprietà `Footprint` nello schematic MCU V7.35. `C6231`, 100nF bypass, **rimane senza MPN/footprint** in quanto richiede una qualifica separata della capacità effettiva, del dielettrico e dell'assemblaggio.

## Gate tecnici obbligatori

Workflow singolo mirato `.github/workflows/v735_tps3840_dbv5_native.yml` usa KiCad9 preinstallato senza apt/pip, esporta i master **sette fogli** V7.34 e V7.35, ERC + netlist prima/dopo, `pcbnew.FootprintLoad` nativo e `unittest` su:
1. 5 pad numerati 1–5, geometria TI esatta fino a 4 decimali;
2. 134 componenti e **101 reti identiche** prima/dopo, **zero differenze sui nodi (ref,pin,net)**;
3. Solo footprint `U6207` da vuoto a TI candidate, valori dei 134 componenti invariati;
4. Missing footprint attesi 35→34, ERC 36 errori baseline, nessun nuovo errore; analisi completa delle warnings conservata;
5. Nessuna approvazione di PCB, DFM, fabbricazione o TX.

**HOLD non risolti:** caratteristiche di soft-start e brownout con VDD sotto VPOR, sequenza analog LDO/RESET, DFM/pasta/mask reali, requisiti EMI e return GND, posizione fisica vicino C6231, simulazioni e validazione hardware. Sottosistemi RX/PLL/power, 15 interfacce OPEN/HOLD, SG48 HOLD e Y1 TXC pin10 HOLD invariati. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Avanzamento percentuale globale PCB da non alterare per ECO footprint: ~10% storico.
