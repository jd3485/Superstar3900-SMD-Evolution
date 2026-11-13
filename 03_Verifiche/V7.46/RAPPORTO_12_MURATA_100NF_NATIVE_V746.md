# V7.46 — ECO CAD reale di 12 condensatori bypass 100nF GRM15 Murata (NO FAB)

**Data:** 13 novembre 2026. Baseline V7.45 [PR #49](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/49) integrata. Si completa un blocco di **12 assegnazioni native KiCad reali** in una sola PR invece di aprire 12 revisioni separate; nessuna modifica alla topologia dei sette fogli.

## Identificazione componente e impronta verificata già in V7.36

Murata **GRM155R71C104KA88D**, MLCC **100nF (0.1µF) ±10%, X7R, 16V, EIA 0402 / 1005 metrico**. Fonti: Murata scheda MPN originale https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM155R71C104KA88-01.pdf , DigiKey SKU esatto https://www.digikey.it/it/products/detail/murata-electronics/GRM155R71C104KA88D/675947 . La classe 16V copre nominalmente 5V e 3.3V, ma **la sola targa tensione e il valore nominale NON qualificano Ceff** con DC-bias, aging, temperatura, ripple o sequenza reale. Per uso su rail è necessaria verifica di stabilità/attenuazione e requisiti minimi del vendor di ciascun IC.

Si riutilizza la libreria **già integrata e testata KiCad9 in V7.36**, senza copiarne una seconda: `S3900E_MURATA_GRM15_V736_HOLD:MURATA_GRM15_0402_REFLOW_REVIEW` → `04_KiCad/Librerie_Footprint_V7.36_MURATA_GRM15_HOLD/S3900E_Murata_Review.pretty/MURATA_GRM15_0402_REFLOW_REVIEW.kicad_mod`, **due pad da 0.40×0.50mm ai centri ±0.40mm**, gap interno 0.40mm; pad lands provenienti dal catalogo Murata GRM15. La verifica DFM finale rimane HOLD.

## Elenco delle 12 modifiche di schema

Unica modifica prevista ai componenti:
`C6201, C6203, C6205, C6207, C6209, C6210, C6211, C6212, C6214, C6217, C6220, C6227`.

Tutti precedentemente `Value=100nF` e `Footprint=""`. Dopo ECO, tutti preservano `100nF`, aggiungono `Footprint=S3900E_MURATA_GRM15_V736_HOLD:MURATA_GRM15_0402_REFLOW_REVIEW` e proprietà `MPN=GRM155R71C104KA88D` nascosta; il già qualificato **C6231** resta invariato. Non modificare `1µF`, `10µF`, `4.7nF` e `10nF`: capacità effettive e requisiti funzionali più severi richiedono qualificazione separata, senza scegliere a caso una 0402.

Nuova copia dello schema `04_KiCad/Modulo_MCU_CODEC_V7.46_12_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` e nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.46_12_MURATA_GRM15_REVIEW_NOT_FOR_FAB/`. Lo schema elettrico **NON ha fili o pin nuovi**, il root continua a contenere AUX/MCU/RX isolati. La libreria esistente è referenziata dal `fp-lib-table` senza duplicazioni.

## Gate nativo KiCad9 prima/dopo

`03_Verifiche/V7.46/test_twelve_murata_caps_native_v746.py` contiene **8 test** e un gate fail-closed: controllo sorgente che ammette esattamente 12 cambi di footprint e MPN; `pcbnew.FootprintLoad` per i due pad e dimensioni; netlist gerarchica KiCad9 prima/dopo, **134 componenti**, **101 reti identiche**, **zero delta pin/rete**, differenze nei campi footprint solo dei 12 Ref attesi; footprint mancanti previsti **32→20**, ERC base **36 errori/221 warning**, nessun aumento di errori e warning fuori tolleranza. Nessun wire, library symbol o part number di altri componenti può cambiare. Questi numeri sono **criteri di accettazione**, NON un PASS prima di osservare CI effettiva.

**Ottimizzazione Actions:** aggiornata la pipeline esistente `.github/workflows/v743_six_ldo_thermal_budget.yml`, includendo i paths V7.46 e, nello stesso job già dotato di KiCad9, export nativi before/after e 8 test. Conservati anche i 36 test termici V7.43 e 20 test netlist V7.45. **Nessun workflow nuovo**, runner e installazioni non duplicati. La modifica YAML è controllata anche da `actions_policy_quick.yml`. Conservare artefatti di netlist/ERC e report test per la PR.

## Stato HOLD

Le MLCC hanno solo footprint/MPN **REVIEW, non valori efficaci approvati**; layout fisico e spacing/distanze delle piazzole non possono essere validati senza una PCB reale. Restano 15 interfacce OPEN/HOLD, GND_MAIN/GND separati, SG48 HOLD, TXC Y1 pin10 AFC/GND HOLD, eFuse/buck, startup, termica e reverse-current TPS7A20 HOLD. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. La percentuale di progettazione PCB globale ~10% storica non va aumentata per sole assegnazioni footprint.
