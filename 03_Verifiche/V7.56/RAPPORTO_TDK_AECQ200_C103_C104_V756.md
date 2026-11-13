# V7.56 — TDK CGA6P3X7R1E226M250AB AEC-Q200 22µF 25V as reviewed C103/C104

13 novembre 2026 — **REVIEW_NOT_FOR_FAB**. Nuova copia KiCad reale, solo MPN e stato review di **C103/C104** modificati rispetto a V7.55. La scelta è fondata su fonti dirette del produttore, non su una semplice equivalenza stimata.

## Qualifica comparativa ufficiale

TDK [C3225X7R1E226M250AB — commerciale](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3225X7R1E226M250AB) indica espressamente per l'uso automotive il codice [CGA6P3X7R1E226M250AB](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA6P3X7R1E226M250AB). Specifiche pubblicate del candidato **CGA6P3**: 22µF ±20%, 25VDC, X7R ±15% (-55...+125°C), package TDK CGA6(3225)/1210, body 3.2±0.4 ×2.5±0.3 ×2.5±0.3mm, AEC-Q200 **YES**, prodotto in produzione. TDK riporta land pattern PA 2.0–2.4 mm, PB 1.0–1.2 mm, PC 1.9–2.5 mm; tali quote non sono qui trasformate in una nuova impronta né approvate dal punto di vista assemblaggio. Le caratteristiche DC bias pubblicate sono indicative; mancanti curve vincolanti per Ceff peggiore (DC bias, ±20%, temperatura e aging) e reale load-step dell'intero ricevitore.

**Alternativa eventuale per flessione PCB:** TDK [CGA6P3X7R1E226M250AE](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA6P3X7R1E226M250AE), automotive AEC-Q200 con *soft termination*, che richiede a sua volta un controllo di land, disponibilità e curva sotto bias. Non sostituirlo automaticamente nel BOM: la variante AB resta candidata corrente, AE opzione da indagare.

## ECO nativa versionata

- Nuovo AUX: `04_KiCad/Gerarchico_Alimentazioni_V7.56_TDK_AECQ200_C103_C104_REVIEW_NOT_FOR_FAB/`, C103/C104 `MPN=CGA6P3X7R1E226M250AB` e `Qualification=V7.56 AEC_Q200_CANDIDATE DC_BIAS_THERMAL_HOLD`. Manufacturer TDK, Value 22uF 25V X7R, `Capacitor_SMD:C_1210_3225Metric`, fili e labels invariati.
- Nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.56_TDK_AECQ200_MLCC_REVIEW_NOT_FOR_FAB/` con sola destinazione AUX aggiornata, senza collegamenti cross-module. Altri tre file AUX e gli altri tre file del master identici byte-per-byte a V7.55.
- Gate `03_Verifiche/V7.56/test_tdk_aecq200_candidate_native_v756.py`: sorgente esatta, 139 componenti, 102 reti, pin-net identici, safety return eFuse, 28 ERC errors / 222 warnings nativi; un'unica ambiguità di report preesistente U6202 MCU pin15/16 può essere normalizzata esclusivamente nel **confronto** delle due liste, non nei report originali (Issue #63). Tutti gli altri findings devono corrispondere.

## Bloccanti non risolti

AEC-Q200 su questo componente **non qualifica automaticamente** il sistema, la sicurezza eFuse o la risposta dinamica TPS54202. **Ceff minima reale**, ESR/ESL, carico, ripple, thermal, geometria produttore del land pattern, disposizione PCB e opzione soft termination restano aperti. Issue #57 ripristino eFuse indipendente dal 5V aperto, SHDN NC; 15 interfacce OPEN/HOLD; ERC 28 errori esistenti e 222 warnings. Senza PCB completa non esiste un DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX, SG48 HOLD, Y1 PIN10 HOLD.**
