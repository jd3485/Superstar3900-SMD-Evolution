# V7.41 — Vendor footprint TDK MPZ2012S601ATD25: prova geometria SMD 0805

**Data:** 13 novembre 2026. Baseline V7.40 [PR#43](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/43) integrata (squash `42a92cb5eeadf72285ee9130bab684c01916d329`). FB6201 è già identificata come **TDK MPZ2012S601ATD25** 600Ω±25%@100MHz, 2A e DCR max100mΩ; in questa revisione si definisce **soltanto il footprint**.

## Fonte primaria verificata visivamente

**Catalogo ufficiale TDK MPZ2012 (Automotive)**: https://product.tdk.com/en/system/files/dam/doc/product/emc/emc/beads/catalog/beads_automotive_power_mpz2012_en.pdf , pagina stampata **3/4, RECOMMENDED LAND PATTERN**: 2 pad rettangolari **0.8 mm** di lunghezza (X), distanza fra i bordi interni **1.0 mm**, altezza (Y) **1.2 mm**. La figura e il prodotto principale sono coerenti con i parametri A=0.80, B=1.00, C=1.20 mm elencati dal produttore sulla pagina https://product.tdk.com/en/search/emc/emc/beads/info?part_no=MPZ2012S601ATD25 . Pertanto i centri pad in KiCad sono `x=±0.90mm, y=0.00mm`, size `0.80×1.20mm`; gap interno=1.00mm. **Non** confondere il pattern di saldatura con la dimensione corpo 2.0×1.25mm. La figura ufficiale è stata visionata direttamente (non dedotta solo da lettere A/B/C).

| Pad | X (mm) | Y (mm) | Cu L×H (mm) | Nodo elettrico nello schema |
|---:|---:|---:|---|---|
| 1 | −0.90 | 0 | 0.80×1.20 | `5V_RF_PREREGULATED` |
| 2 | +0.90 | 0 | 0.80×1.20 | `5V_DIGITAL_FILTERED` |

Ferrite non polarizzata, numerazione 1/2 scelta da progettazione KiCad: il produttore non assegna una polarità. Sono comunque conservate la corretta distinzione dei due lati e tutte le connessioni native.

## Modifica fisica

- Libreria `04_KiCad/Librerie_Footprint_V7.41_TDK_MPZ2012_HOLD/S3900E_TDK_Mpz_Review.pretty/TDK_MPZ2012_0805_POWER_BEAD_REFLOW_REVIEW.kicad_mod`: due pad Cu `0.8×1.2mm`, coordinate ±0.9/0, courtyard e fab outline nominali REVIEW.
- Modulo `04_KiCad/Modulo_MCU_CODEC_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/`: assegnata **solo a FB6201** proprietà footprint `S3900E_TDK_MPZ2012_V741_HOLD:TDK_MPZ2012_0805_POWER_BEAD_REFLOW_REVIEW`, mantenendo MPN TDK e valore `600R@100MHz_TDK_2A_REVIEW`. Nessun altro valore/MPN o collegamento modificato.
- Nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/`, lib table aggiornata. Il root AUX/MCU/RX rimane a sottosistemi **isolati**: nessuna introduzione di pin gerarchici o unione di `GND_MAIN` con `GND`.

## Verifica nativa prevista

Il test `03_Verifiche/V7.41/test_fb6201_tdk_footprint_native_v741.py` effettua `pcbnew.FootprintLoad`, controlla due pad numerati e la geometria TDK, differenza source-only ammessa solo sul `Footprint` di FB6201, confronto delle sette sheet in KiCad9, 134 componenti, 101 reti identiche, **zero delta di nodo pin-rete**, missing footprint **33→32**, ERC 36 errori/221 warning baseline e nessun aumento di errori. **Nove test** mirati con una sola pipeline PR, senza apt/pip. Registrare run e artefatti solo ad esecuzione avvenuta.

## Vincoli residui

Il land pattern del produttore è un punto di partenza; l'assegnazione **non** approva solder mask/paste applicata al processo reale, footprint DFM del fornitore, temperatura, ripple e comportamento Z(f,I_dc), oscillazioni con MLCC lato uscita, o layout PCB. MPN `MPZ2012S601ATD25` resta in **REVIEW** finché non si dimostrano power budget e sollecitazioni ambientali. L'interfaccia elettrica fra AUX e MCU resta una delle **15 crossmodule OPEN/HOLD**. Non accorciare le attese con un power net bridge. Nessuna radio PCB completa, nessun DRC globale, SG48 HOLD, Y1 TCXO pin10 HOLD, **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Avanzamento storico 10% stimato e invariato.
