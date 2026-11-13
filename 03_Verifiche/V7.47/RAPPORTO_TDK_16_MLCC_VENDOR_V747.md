# V7.47 — 16 condensatori SMD TDK 1µF/10µF, land pattern originali (REVIEW / NO FAB)

**Data:** 13 novembre 2026. **Baseline V7.46 integrata:** PR #50 squash `5247ad447a2a7e35102945fc3af9792b2a30419e`, 134 componenti, 101 reti, 20 footprint mancanti e ERC 36 errori + 221 warning. La revisione V7.47 è una vera **ECO CAD di 16 footprint e MPN**, non una certificazione di Ceff o degli alimentatori.

## Selezione e stato di produzione

1. **1µF 16V X7R ±10%, TDK `C1608X7R1C105K080AC`**, serie C1608, 0603 EIA (1608 metrico), **Production**. Scheda ufficiale https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1C105K080AC . Corpo 1.6±0.1 × 0.8±0.1 × 0.8±0.1 mm. Non usare il vecchio `GRM188R71C105KA12D` Murata obsoleto come nuova distinta di base.
2. **10µF 10V X7R ±10%, TDK `C2012X7R1A106K125AC`**, serie C2012, 0805 EIA (2012 metrico), **Production**. Scheda ufficiale https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X7R1A106K125AC . Corpo 2.0±0.2 × 1.25±0.2 × 1.25±0.2 mm. Non scegliere automaticamente Murata `GRM21BR71A106KE51L`: DigiKey segnala **obsolete** al controllo 2026. Entrambi i nuovi MPN sono targa X7R e tensione nominale compatibile con nodi 3.3V/5V, **non** un'approvazione del Ceff.

## Disegno dei pad, fonte e interpretazione

Fonte produttore TDK `GC11010023`, *MLCC commercial general*, agosto 2025, pag.18 stampata, screenshot esaminato: https://product.tdk.com/info/en/catalog/spec/mlccspec_commercial_general_midvoltage_en.pdf . Lo schema mostra **A=separazione interna dei pad**, **B=lunghezza di ciascuna piazzola Cu**, **C=larghezza del pad**. Intervalli raccomandati reflow:
- **C1608 / 0603:** A 0.60–0.80mm, B 0.60–0.80mm, C 0.60–0.80mm. Land scelto nel range: **A 0.70, B 0.70, C 0.70mm**, due pad centri **x ±0.70mm**, size **0.70×0.70mm**.
- **C2012 / 0805:** A 0.90–1.20mm, B 0.70–0.90mm, C 0.90–1.20mm. Land scelto nel range: **A 1.00, B 0.80, C 1.00mm**, due pad centri **x ±0.90mm**, size **0.80×1.00mm**.

I footprint `S3900E_TDK_MLCC_V747_HOLD:TDK_C1608_0603_1UF_REFLOW_REVIEW` e `S3900E_TDK_MLCC_V747_HOLD:TDK_C2012_0805_10UF_REFLOW_REVIEW` sono in `04_KiCad/Librerie_Footprint_V7.47_TDK_MLCC_HOLD/S3900E_TDK_MLCC_Review.pretty/`. Verificare nativamente footprint con `pcbnew.FootprintLoad`, pad 1/2, Cu/MASK/PASTE, dimensioni/gap, e non solo codice testuale. Courtyard e PCB assembly DFM/paste aperture finali da qualificare; nessuna PCB unica completa.

## Modifica esatta della schematica MCU/CODEC

Da `04_KiCad/Modulo_MCU_CODEC_V7.46_12_MURATA_GRM15_REVIEW_NOT_FOR_FAB/` a `04_KiCad/Modulo_MCU_CODEC_V7.47_TDK_16_MLCC_REVIEW_NOT_FOR_FAB/`. Solo sostituzione proprietà `Footprint=""` e aggiunta `MPN` nascosto per i seguenti **16 riferimenti**:
- **11 × 1µF 0603:** `C6213,C6215,C6216,C6218,C6221,C6222,C6223,C6224,C6225,C6226,C6229`.
- **5 × 10µF 0805:** `C6202,C6204,C6206,C6208,C6219`.

Nessun valore nominale, etichetta, wire, pin, MPN precedente né altri condensatori cambiati. Nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.47_TDK_16_MLCC_REVIEW_NOT_FOR_FAB/` con istanza di nuovo MCU, root AUX e RX isolati come prima, nuova libreria TDK registrata nel `fp-lib-table`. Il precedente MPN Murata 100nF nei 13 condensatori è preservato.

## Gate KiCad9 e criterio di accettazione

`03_Verifiche/V7.47/test_tdk_16_mlcc_native_v747.py` include **12 test**. Controlla esattamente 16 modifiche MPN/footprint, 2 footprint vendor caricati con `pcbnew`, confronto sette fogli KiCad9 export netlist + ERC **prima/dopo** su master V7.46/V7.47, 134 componenti, 101 reti completamente identiche, zero pin/net delta, footprint mancanti attesi **20→4**, ERC 36 errori e 221 avvisi precedenti **non peggiorati**. Nessun signoff sulla sola base di un esito verde. Il workflow KiCad9 esistente `.github/workflows/v743_six_ldo_thermal_budget.yml` è **esteso e riutilizzato**: nello stesso runner conserva i 36 test V7.43, 20 V7.45 e 8 V7.46, poi le due esportazioni KiCad9 e i 12 test V7.47. **Nessun nuovo workflow, nessun secondo container e nessun pip/apt**, safety-policy rapida su modifica YAML. Registrare run ID, esito e artefatto solo dopo prova reale.

## Rischi e qualifiche ancora aperte

**Particolarmente importante:** TPS7A20 richiede almeno **1µF di capacità ceramica effettiva sull'uscita** per stabilità; fonte TI TPS7A20 SBVS338H https://www.ti.com/lit/ds/symlink/tps7a20.pdf §1, §7.1.1–7.1.2, che avverte dell'effetto DC-bias sulla capacità. Un MLCC nominale 1µF 16V X7R da 0603, applicato a 3.3V, non dimostra Ceff≥1µF. Alcune reti hanno più condensatori (ad es. 100nF e 10µF), ma la capacità **effettiva e i minimi di stabilità** devono essere verificati nodo per nodo e con derating produttore: **LDO POWER SIGNOFF HOLD**. I 10µF su nodi codec/MCU, buck/filter e upstream devono essere controllati in startup/inrush, powerdown reverse-current TPS7A20, qualità audio, Ceff(3.3V/5V), ESR, ripple e configurazione firmware. Nessuna prova termica o configurazione reale del codec. Y1 TCXO pin10 AFC/GND ancora HOLD; nessun collegamento artificiale tra `GND_MAIN` e `GND`; 15 interfacce crossmodule OPEN/HOLD; SG48 HOLD.

Se il gate nativo passa, **i restanti 4 footprint vuoti NON vanno completati a caso**: 4.7nF e 10nF possono servire a filtri/temporizzazioni, altri componenti dovranno essere identificati in netlist. Rimangono 36 errori ERC, 221 avvisi preesistenti, power/PLL/termica e PCB unificata da progettare. **NO FAB / NO GERBER / NO PCBWAY / NO TX**; percentuale PCB globale storica ~10% stimata, non aumentarla automaticamente per i footprint.
