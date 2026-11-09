# Revisione elettrica V1.4 - AUX POWER

## Verifiche statiche, non ERC

A) Controllare la completezza delle librerie di simboli, UUID, coordinate dei pin e labels.
B) Per ogni pin verificare che coincida con una label, un filo o un `no_connect`.
C) Non confondere `GND_MAIN` con `EFUSE_RTN`, altrimenti la protezione inversione eFuse puo diventare inoperante.
D) Verificare sui 3 fogli figli che pin gerarchici e label siano esattamente corrispondenti.
E) Verificare se il riferimento 12.8 MHz richiede AFC oppure GND sul pin 10 e controllare l'identico package prima di scegliere il footprint.

## Miglioramenti allo schema
- J100: nuovo connettore sul root (solo elettrico). Da selezionare con revisione meccanica e specifica di corrente.
- 6 nodi PLL: divisione del filo di 206.08..218.92 mm nel punto 212.50 mm, preservando la rete elettrica nominale.

## Bloccanti per la fabbricazione
1. Native ERC / netlist: in questo ambiente `kicad-cli` non installato. **NON ESEGUITI**.
2. Scelta e verifica del package del connettore J100, del fusibile F200 e del TCXO Y1.
3. Test di accensione/spegnimento e transitori, coordinamento eFuse-TVS, EMI buck.
4. Progetto PCB e routing RF su 4+ layer ancora assenti.
5. Calcoli su prestazioni ricevitore, emissioni, TX e uso radio ancora da validare al banco.

## Fonti tecniche
- TI TPS2660x datasheet: https://www.ti.com/lit/ds/symlink/tps2660.pdf
- TI TPS54202 datasheet: https://www.ti.com/lit/ds/symlink/tps54202.pdf
- TXC 7N 10 pad datasheet: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/4732/7N_Series_10_Pad_DS.pdf
- KiCad CLI ERC: https://docs.kicad.org/9.0/en/cli/cli.html
