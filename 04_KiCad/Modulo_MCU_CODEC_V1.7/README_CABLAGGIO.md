# Schema KiCad V1.7: bozza concettuale verificabile

Lo schema e' una bozza con simboli **embedded** generati da questo progetto; tutti i pin dei due circuiti integrati sono rappresentati.
Le etichette locali con lo stesso nome costituiscono reti collegate logicamente. Gli altri pin sono marcati intenzionalmente NC in questa versione, NON una decisione di produzione.
I passivi R/C sono rappresentati e collegati logicamente con etichette ai terminali, ma i loro footprint non sono assegnati: nessuna parte e' autorizzata per la produzione.
La netlist/validazione ERC nativa KiCad non e' stata eseguita per indisponibilita' dell'eseguibile `kicad-cli` in ambiente. I test Python non sostituiscono ERC o SPICE.
Verificare in KiCad sul proprio PC, controllare rotazione/label/simboli prima di aggiungere al progetto gerarchico e prima di scegliere footprint.
