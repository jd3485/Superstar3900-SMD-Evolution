# V7.48 — C6228 4.7nF e C6230 10nF C0G TDK, 0603 vendor land NO FAB

**Data:** 13 novembre 2026. Baseline V7.47 PR#51 integrata squash `28c3ed115360a96b972c849589c87b64f1d3bc4e` (134 componenti, 101 reti, 4 footprint missing, ERC36/221). V7.48 è una **ECO CAD limitata ai footprint/MPN** e non modifica fili, pin, nominale, top-level interfacce o radio.

## Vendor esatto e proprietà

TDK, prodotti **Production** alla verifica catalogo:
- `C6228` = **4.7nF ±5%, C0G, 50V, 0603**. MPN `C1608C0G1H472J080AA`, produttore https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608C0G1H472J080AA .
- `C6230` = **10nF ±5%, C0G, 50V, 0603**. MPN `C1608C0G1H103J080AA`, produttore https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608C0G1H103J080AA .

**Perché C0G?** Nei piccoli valori associabili a disaccoppiamento/filtraggio o RC il C0G riduce fortemente le variazioni termiche e con bias rispetto agli X7R, importante prima di conoscere le condizioni effettive di oscillatori e sequenze. **Non equivale a una verifica della frequenza di taglio, della stabilità di feedback o del transitorio**: mancano carichi, funzione del nodo e prove circuitali. Non sostituire resistenze o valori nominali per ottenere un test verde.

## Footprint e limite fisico

Entrambi i MPN appartengono alla serie TDK C1608 **1608 metrico / EIA0603**. Il disegno ufficiale TDK `GC11010023` agosto 2025 p18 https://product.tdk.com/info/en/catalog/spec/mlccspec_commercial_general_midvoltage_en.pdf raccomanda A=gap interno 0.60–0.80mm, B=lunghezza pad 0.60–0.80mm, C=altezza pad 0.60–0.80mm. **Nuovo** footprint generico per i due C0G `S3900E_TDK_C0G_V748_HOLD:TDK_C1608_0603_C0G_REFLOW_REVIEW` con **2 pad** 0.70×0.70mm a x±0.70mm. La geometria copia intenzionalmente il land già approvato come *candidato vendor* per il 0603 TDK V7.47, ma tiene separati i MPN e la classe C0G dalla libreria 1µF X7R, evitando un'impronta erroneamente nominata 1UF per condensatori in nF. File `04_KiCad/Librerie_Footprint_V7.48_TDK_C0G_HOLD/S3900E_TDK_C0G_Review.pretty/`.

## ECO, checks e residui

Nuova copia MCU `04_KiCad/Modulo_MCU_CODEC_V7.48_TDK_2_C0G_REVIEW_NOT_FOR_FAB/` e nuovo master 7 fogli `04_KiCad/Assemblaggio_RX_Power_V7.48_TDK_2_C0G_REVIEW_NOT_FOR_FAB/`. Solo nuove proprietà hidden MPN e footprint per C6228 e C6230. Invariate C6201–C6231, tutte le reti, le radici AUX/MCU/RX isolate e gli altri MPN. `03_Verifiche/V7.48/test_tdk_c0g_2caps_native_v748.py` **8 test** di differenza strict source-only, load footprint nativo, confronto KiCad9 134 componenti/101 reti ed ERC prima/dopo, obiettivo **4→2 footprint mancanti** con zero nuove violazioni. Lo stesso workflow KiCad9 preesistente V7.43 include la V7.48 e conserva le regressioni 36+20+8+12+8, **nessun workflow nuovo**. Nessun PASS dichiarato fino al run osservato.

I **2 footprint ancora da identificare** possono essere di altro tipo; non concludere che siano due MLCC, non aggiungerli in modo meccanico o alterare i collegamenti per far scomparire gli errori. ERC36/221 già presente, 15 interfacce OPEN/HOLD, SG48 HOLD, Y1 TCXO pin10 HOLD, TPS7A20 Ceff/stability/reverse, layout/DFM, power return AUX↔MCU ancora da qualificare. **NO FAB / NO GERBER / NO PCBWAY / NO TX**, nessuna PCB radio completa né DRC globale, avanzamento complessivo storico ~10%.
