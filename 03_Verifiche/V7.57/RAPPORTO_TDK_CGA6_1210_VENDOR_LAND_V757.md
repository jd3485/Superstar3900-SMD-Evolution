# V7.57 — TDK CGA6 AEC-Q200 1210: piazzole CAD vendor reflow (HOLD, NO FAB)

13 novembre 2026. Nuovo footprint **fisico e versionato** per C103/C104 TDK `CGA6P3X7R1E226M250AB`, già selezionato come candidato AEC-Q200 in V7.56. Impronta CAD prova **solo la geometria raccomandata**, non la validazione termica o fabbricabilità complessiva.

## Fonte e interpretazione geometrica

TDK [scheda prodotto CGA6P3X7R1E226M250AB](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA6P3X7R1E226M250AB) conferma 22µF ±20% / 25V X7R / AEC-Q200 / corpo 3.20±0.40 ×2.50±0.30 ×2.50±0.30mm e i campi land `PA=2.00–2.40mm`, `PB=1.00–1.20mm`, `PC=1.90–2.50mm`. Il documento ufficiale TDK [delivery specification CGA6 soft termination AC110G0020, October 2025, §3 pagina 15](https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/specification/mlccspec_automotive_soft_en.pdf) contiene il disegno di orientamento della stessa famiglia 1210: **A = distanza interna fra le piazzole**, **B = estensione longitudinale di una piazzola**, **C = larghezza trasversale**. Per prudenza abbiamo scelto i punti centrali degli intervalli: A=2.20mm, B=1.10mm, C=2.20mm.

Nel footprint `S3900E_TDK_CGA6_V757_HOLD:TDK_CGA6_1210_AECQ200_C103_C104_VENDOR_LAND_HOLD` quindi i pad 1/2 sono rispettivamente a x=−1.65/+1.65mm, di dimensioni **1.10×2.20mm**; inner gap 2.20mm e span esterno 4.40mm. Il corpo F.Fab è nominale 3.20×2.50mm, F.CrtYd provvisorio 5.00×3.50mm. Non si sono previste aperture paste custom approvate o analisi DFM saldatura/reflow; geometria di review, no fab.

## Modifica CAD e garanzie del gate

Nuova libreria `04_KiCad/Librerie_Footprint_V7.57_TDK_CGA6_AECQ200_HOLD/S3900E_TDK_CGA6_Review.pretty/`, nuova AUX `04_KiCad/Gerarchico_Alimentazioni_V7.57_TDK_CGA6_VENDOR_LAND_REVIEW_NOT_FOR_FAB/`, nuovo root `04_KiCad/Assemblaggio_RX_Power_V7.57_TDK_CGA6_VENDOR_LAND_REVIEW_NOT_FOR_FAB/`. **SOLO footprint C103/C104 e reference AUX del root** cambiano rispetto a V7.56, oltre alla registrazione della libreria nel `fp-lib-table`. Capacità 22µF 25V, MPN automotive, eFuse, sorgenti, reti, MCU/RX e gli altri file restano identici.

`03_Verifiche/V7.57/test_tdk_cga6_land_native_v757.py` carica la libreria realmente con `pcbnew.FootprintLoad` KiCad9, verifica due pad e A/B/C, confronta netlist nativa prima/dopo con **139 componenti, 102 reti, solo due associazioni footprint modificate e 0 delta pin-rete**. Richiede ERC 28 errori/222 warning in entrambi i casi e stessi findings, salvo nota specifica U6202 offgrid report su MCU identica (Issue #63), senza sopprimerli. Nessun altro pad/pin aggiunto, niente connettività cross-module.

## Non approvato

AEC-Q200 non garantisce capacità minima in presenza di DC-bias, temperatura, aging, tolleranza e reale carico 5V; le curve TDK pubblicate sono illustrative. PCB unificata non esiste, non si conoscono dimensioni/piega/posizionamento, sensibilità MLCC a flex crack, eFuse reset Issue #57 ancora OPEN/SHDN NC. 15 interfacce OPEN/HOLD, SG48/Y1 pin10 HOLD, **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Nessuna stima avanzamento PCB aumentata per footprint senza PCB.
