# CHANGELOG V4.1 — 2026-11-08

**Revisione cumulativa, statica, NON per fabbricazione. Stima avanzamento 37% invariata.**

- Aggiunti audit RF V4.1 (Python stdlib + parser storico), 12 test, rapporto JSON, e rapporti tecnico/criteri di accettazione.
- Calcolato modello resistivo ideale attenuatore π su R201/R203/R202 con analisi ipotetica ±1%; no misure RF.
- Misurato staticamente via/paddle U101: nessun via sotto la piazzola, via esterno più vicino a 0,50 mm dal rame, percorso tramite pista F.Cu; resta aperta validazione termica.
- Acquisita e analizzata pubblicamente la pagina di prodotto TE e la Rev. A datasheet ADI; DXF/STEP TE non inclusi nel pacchetto, non sono stati importati/approvati.
- Aggiunto launcher per KiCad 10+ su **copia** dei file, non eseguito: kicad-cli assente nell'ambiente di creazione. Niente Gerber.
- Aggiornati README, handoff e registro decisioni conservandone snapshot V4.0.
- Il manuale d'uso V4.0 (11 pagine), tutte le versioni precedenti e il PCB V3.8 restano conservati.
