# V6.5 — mixer RF, immagini e prima FI (09-11-2026)

- Scelto candidato mixer ADE-1+ con 6 pin da produttore e LO livello +7dBm.
- Modellato il preselettore Butterworth idealizzato 25–29MHz N=3 / ordine analogico 6 e 270 frequenze immagine.
- Simulati 12.000 scenari fC/BW e FFT di moltiplicazione desiderato/immagine; 50/50 test e 8/8 suite selezionate PASS.
- Esplicitati requisiti banda FI AM/FM/USB/LSB/CW, pinout, BOM provvisoria e netlist funzionale separata dai pin fisici.
- Nessuna rete LC, driver LO, filtro IF, AGC o demod validati. KiCad/ERC/DRC non eseguiti; no FAB / no TX.
- La storia V6.4 preservata byte per byte; tre documenti attivi V6.4 con snapshot integrali in `09_Archivi_Precedenti/Snapshot_Integrali_V6.4`.
