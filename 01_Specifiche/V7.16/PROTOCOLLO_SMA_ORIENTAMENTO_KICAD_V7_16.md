# Superstar 3900 SMD Evolution — V7.16: verifica differenziale SMA in KiCad nativo

**10 novembre 2026. Studio tecnico non fabbricabile e senza RF TX.** Sorgente immutabile: `04_KiCad/Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB/S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pcb`, mantenuto identico alla V7.12. Stato corrente della baseline V7.15: clone temporaneo con refill KiCad, 2 errori `lib_footprint_mismatch` (J9102/J9104) e 0 unconnected, ma **nessuna revisione di PCB produttiva**.

## Origine primaria del componente

Il produttore è **TE Connectivity / Linx Technologies**, identificativo `CONSMA002-SMD`, jack SMA 50 Ω a 90°, montaggio SMD. Pagina vendor **https://www.te.com/en/product-CONSMA002-SMD.html**: contiene il disegno di prodotto `ENG_CD_C-CONSMA002-SMD-X-X_D.pdf` e CAD ufficiali elencati dal produttore: `ENG_CVM_CVM_CONSMA002-SMD_D.2d_dxf.zip`, `ENG_CVM_CVM_CONSMA002-SMD_D.3d_igs.zip`, `ENG_CVM_CVM_CONSMA002-SMD_D.3d_stp.zip`.

**Stato di qualificazione:** il produttore rende disponibili i nomi dei CAD, ma il DXF/STEP originale non è stato acquisito e confrontato geometricamente nella pipeline; inoltre non è stata ottenuta l'approvazione assembly, F.Paste/F.Mask, tolleranze, ingombro fisico e idoneità al bordo. Non scrivere `vendor footprint approved` oppure `DRC PASS = PCB pronto`.

## Ipotesi diagnostiche V7.16

Nel PCB la posizione J9102 = (122, 36) con rotazione 180°, J9104 = (122, 65) con rotazione 180°. J9101/J9103 hanno orientamento 0°. Il confronto V7.15 conferma che tutte le cinque forme locali dei pad (separate dai net/UUID) corrispondono ai pad della libreria candidata; questo non verifica la trasformazione completa e i disegni.

I quattro esperimenti sono eseguiti con **vero pcbnew + kicad-cli** su copie temporanee distinte, mentre il PCB sorgente è protetto con SHA256:
- `as_saved`: baseline, solo riempimento quattro zone + DRC;
- `reference_value_text_180_diagnostic`: modifica solo gli angoli dei testi Reference/Value delle due istanze SMA e controlla il mismatch;
- `orientation_0_diagnostic`: imposta 0° sulle due istanze **a puro scopo causale**. Questa prova sposta i pad in coordinate globali, invalida il routing fisico e NON è proponibile per la versione finale;
- `pad_rotation_180_diagnostic`: modifica soltanto l'orientamento locale dei pad di massa custom sulle istanze target. Potrebbe alterare il rame relativo e non è utilizzabile senza il confronto con la libreria/TE.

Per ogni variante si registra il report DRC vero e si preservano categorie **DRC vs unconnected**. Un eventuale `lib_footprint_mismatch=0` su una variante non è una soluzione qualificata: una prova causale non è autorizzazione di copper/footprint/layout né TX.

## Bloccanti e passaggi di rilascio

Controlli obbligatori prima di creare un PCB revisionato: CAD vendor DXF/STEP verificati, geometrie custom pad con orientamento corretto, posizione reale del connettore su bordo, clearance solder mask/paste, stack-up RF e massa/return paths, DRC nativo su PCB riempito e salvato in un percorso V7.16 distinto, ERC gerarchico (baseline 43 errori +340 warning), 15 interfacce OPEN/HOLD e pinout FPGA SG48 HOLD. Continuare test e firmware/DSP/PLL senza muovere lo storico.

**NO FAB, NO PCBWAY, NO GERBER, NO TX, nessun PA/antenna alimentati o collegati.**
