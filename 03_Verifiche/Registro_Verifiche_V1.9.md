# Revisione V1.9: verifiche effettuate e mancanti

## Verifiche software
- Test V1.9 sui nomi della nuova rail e MPN candidati, polarizzazione LDO_SELECT e passivi AFE; log in `LOG_Test_V1.9.txt`.
- Calcolo RC in `Calcoli_AFE_Alimentazioni_V1.9.json`. Modello ideale, non SPICE.
- Test di regressione in `Regressione_V1.9.json`. Risultati devono essere letti per file, senza dichiarare passati quelli falliti.

## NON verificato
- KiCad ERC/DRC e netlist, perché `kicad-cli` non disponibile; layout non presente.
- Collegamento reale del 5V da buck al nuovo modulo: fogli KiCad distinti.
- Correnti e stabilità LDO + bead, spunto e risonanze.
- Analog front-end a livelli massimi e noise-floor, RF e EMI.
- Firmware del codec, STM32 SAI slave, DCS.
- Collaudo elettromagnetico, ricevitore e trasmettitore.
