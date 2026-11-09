# Verifiche V0.7

## Eseguite
- Confronto manuale pin LMX2572 e TI SNAS740B Fig. pin configuration: numeri 1..40 e pad esposto (CAD 41).
- Controllo manuale rete di bypass TI SNAU217B Fig.19: correzione pin3 100nF; pin27 470nF.
- Controllo Python di parentesi/commenti/stringhe `.kicad_sch` e unicità 41 pin: PASS; non equivale a import KiCad.
- Controllo automatico integrità ZIP tramite `ZipFile.testzip`: PASS.
- Suite software precedenti: da rieseguire nella release.

## Non eseguite
- Apertura KiCad reale; ERC; netlist KiCad; verifiche del footprint; DRC; circuit simulator o misure RF; valutazione rumore di fase effettiva; test PCBWay.

## Nota
La compatibilità del file con KiCad è PROPOSTA secondo la specifica del formato; non verificata con `kicad-cli` assente da questo ambiente.
