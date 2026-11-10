# Superstar 3900 RX 50Ω — KiCad project V7.14 (STUDIO, NO FAB)

Aprire **`S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pro`** con KiCad 9, non solo il foglio `.kicad_sch`. Nella stessa cartella si trovano schema `.kicad_sch`, PCB `.kicad_pcb`, copia immutata della libreria `S3900E.kicad_sym`, `sym-lib-table` e `fp-lib-table`. Le librerie footprint `.pretty` restano nella cartella archivio RX V5.2 e sono referenziate con path relativi al progetto.

La registrazione delle librerie **via progetto** è indispensabile: il CLI KiCad9 senza file `.kicad_pro` produceva 30 warning ERC, pur trovando i sorgenti. Ora il vero `kicad-cli sch erc` è **0 errori /0 warning** sulla sola RX; netlist di tutti i pin identica alla V7.13. Non sono state modificate le proprietà elettriche né alcuna pista o via: il file `.kicad_pcb` è byte per byte quello della V7.12.

**PCB NON APPROVATO:** DRC KiCad **72 violazioni**, precisamente **70 via GND_RF dangling +2 footprint SMA J9102/J9104 divergenti dalla libreria**, oltre **63 unconnected items**. Il fatto che la libreria sia leggibile non implica che i footprint corrispondano al componente acquistabile. NON correggere i due SMA automaticamente: confrontare dimensioni/pin/terre con la tavola vendor. Verifica KiCad GUI, producibilità via-in-pad, sbroglio, RF ed EMC NON ESEGUITI.

Rapporto: `../../Superstar3900_Rapporto_Tecnico_V7.14.md`. Test: `.github/workflows/v714_rx_library_native_erc.yml`. **NO FAB / NO TX**.
