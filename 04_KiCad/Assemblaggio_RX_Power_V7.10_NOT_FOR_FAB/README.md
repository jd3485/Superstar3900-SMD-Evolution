# V7.10 — Primo indice di integrazione KiCad reale RX / POWER / MCU

**10 novembre 2026. NO FAB / NO TX.**

Questo è un file **KiCad .kicad_sch gerarchico reale**, non un diagramma disegnato a mano. Il suo scopo è riutilizzare le basi già presenti nel repository e iniziare a diagnosticare, tramite KiCad CLI *nativo*, la vera distanza da un progetto elettrico completo.

## Aprire in KiCad

Aprire con l'editor schemi di KiCad il file:

`S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch`

Il nuovo foglio superiore punta **senza copiare o modificare** ai file originari:
- `../Gerarchico_Alimentazioni_V1.5/S3900E_AUX_POWER_V1_5.kicad_sch`, al suo interno 3 pagine efuse → buck 5V → LDO/TCXO/PLL;
- `../Modulo_MCU_CODEC_V2.1/S3900E_MCU_CODEC_AFE_V2_1_DRAFT.kicad_sch`;
- `../Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB/S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_sch`. Esiste anche un **PCB KiCad vero V5.2**, ma è soltanto un *coupon* RX 50ohm in stato non fabbricabile, NON il PCB dell'intera radio.

**IMPORTANTE:** i tre fogli figli sono deliberatamente senza pin di collegamento al livello superiore. La gerarchia è un *indice CAD apribile*, NON uno schema elettricamente interconnesso. Local labels simili non autorizzano alimentazioni o GND comuni. Non esiste un `.kicad_pcb` della radio completa e la catena TX non è stata incorporata.

## Matrice dei collegamenti ancora aperti

`MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv` registra 15 interfacce da validare. Ogni riga ha `physical_connection=OPEN`, `qualification=HOLD` e `tx_permission=0`. In particolare:
- `5V_RF_PREREGULATED` NON è automaticamente equivalente alla `+5V_BENCH` del modulo di prova RF (filtro, corrente e noise budget da validare).
- La `3V3_CODEC_IO` non può essere collegata direttamente al rail 5V senza un regolatore verificato.
- Il cablaggio SPI fra MCU e PLL va prima controllato pin-per-pin.
- Il modulo RF da banco non contiene conversione RF→IF2 completa e non viene collegato a PA o antenna TX.

## Come viene fatto il controllo *vero*

Workflow `.github/workflows/v710_kicad_native_rx_audit.yml`:
1. Installa `kicad-cli` reale e registra versione (non interpreta solo il testo).
2. Esegue 12 test statici di gerarchia, inventario board e interfacce aperte.
3. Esegue **KiCad sch export netlist** sul foglio di integrazione: l'export deve riuscire; non è una verifica di correttezza elettrica.
4. Esegue **KiCad sch erc** sui tre moduli preesistenti e sul foglio aggregatore.
5. Esegue **KiCad pcb drc** sul coupon RX V5.2 con rapporti non filtrati e pubblica file di output nella sezione **Artifacts** del run.

**Non si disabilitano errori ERC/DRC**: i file legacy sono incompleti; il successo del comando diagnostico è distinto da 0 violazioni. Non si esportano Gerber, forature o file pick-and-place. La sintesi DSP/firmware V7.1–V7.9 rimane valida come lavoro separato e non viene abbandonata.

## Gate successivi, senza sovrastimare lo stato

- **V7.11:** correggere *su copie versionate* le incompatibilità KiCad native e i veri errori ERC/DRC del primo modulo RX, mantenendo gli originali.
- Solo dopo: interfacce power/ground/MCU verificate, vero schema elettrico unico, piano componenti e footprint MPN, modulo ricezione completo con lo stadio IF e PLL, quindi layout e routing della scheda integrata.
- I blocchi TX sono ancora tutti DNP; prima di una futura integrazione TX servono protezioni fail-closed indipendenti, verifiche elettriche e normative. Nessuna fabbricazione o RF emissione.

**Le revisioni V7.0–V7.9 e le loro simulazioni/firmware/test vengono preservati. NO FAB / NO TX.**
