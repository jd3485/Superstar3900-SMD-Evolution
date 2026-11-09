# Procedura release e tracciabilità

## Ogni rilascio
1. Aggiornare e numerare in `CHANGELOG.md` le nuove funzioni, le correzioni e i cambiamenti incompatibili.
2. Aggiornare `STATO_PROGETTO.md` e `REGISTRO_DECISIONI.md`.
3. Mantenere requisiti e documenti precedenti: i file precedenti non si considerano superati se non documentato.
4. Aggiornare la tabella requisiti → documento → verifica e conservare i report dei test con esito e limiti.
5. Eseguire i controlli pertinenti; archiviare report/esito nel registro verifiche.
6. Aggiornare `MANIFEST_SHA256.txt` e creare ZIP contenente l'intero albero, non solo i file nuovi.
7. Indicare chiaramente se la revisione è *studio*, *schema*, *prototipo*, *produzione* o *rilascio collaudato*.

## Porte di qualità (gate)
- G0 Specifiche: requisiti numerati e gap dichiarati.
- G1 Architettura: diagramma funzionale, budget RF, interfacce, power budget, safety, componenti candidati.
- G2 Schema: netlist KiCad + ERC pulito, calcoli/simulazioni sottosezioni, BOM provvisoria con datasheet.
- G3 Layout: regole stack-up, percorsi ritorno, simulazioni opportune, DRC, DFM/DFT, disegni meccanici.
- G4 Fabbricazione: Gerber/Excellon, IPC/ODB++ se disponibile, drill map, pick&place, BOM, drawing e revisioni allineate.
- G5 Collaudo: schema di taratura e misure effettive, anomalie, revisione HW/FW, test sicurezza/conformità.
- G6 Manuali finali: schemi completi, razionale tecnico, istruzioni per ogni componente e utente; coerenza con l'hardware rilasciato.

## Convenzioni
- Versione archivio: `Superstar3900_SMD_Evolution_Vx.y.z.zip`.
- File tecnici con revisione e identificativi PCB/FW quando presenti.
- Ogni misura riporti strumento, condizioni, taratura e data; non chiamare “testato” un modello solo simulato.
- Per il montaggio singolo componente: identificativo (es. R101), valore, tolleranza, package, polarità/orientamento, lato PCB, passo procedura e checkpoint visivo/elettrico.

- **Vincolo V0.9:** mai inviare il file KiCad a fabbricazione finche U2/U3/TXCO, pin 10, piedinatura, footprint, EMC e ERC non siano chiusi.
