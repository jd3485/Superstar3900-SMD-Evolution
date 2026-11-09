# V0.7 - Modulo PLL: primo file KiCad di studio

**NON FABBRICABILE.** Per la prima volta esiste un file `.kicad_sch` con il simbolo U1 del LMX2572 a 40 pin + exposed pad modellato come pin CAD 41.

## Creato
- `04_KiCad/Sorgenti_Modulo_PLL_V0.7/S3900E_PLL_V0_7_DRAFT.kicad_sch`: prima bozza, apertura in KiCad NON verificata in questo ambiente.
- `S3900E_v07.kicad_sym`: libreria proposta per ispezione.
- `Pin_to_Net_V0.7.csv`: tracciabilità degli 41 punti di connessione.
- `Anteprima_Strutturale_V0.7.svg`: anteprima indipendente, NON rendering KiCad.
- Rete analogica del filtro di anello C1/C2/C3/R2/R3 solo come candidato *matematico* V0.6.

## Verifica TI sul bypass
La scheda TI EVM SNAU217B Figure 19 (p.13) usa pin 3 VbiasVCO -> 100nF e pin 27 VbiasVCO2 -> 470nF. La V0.6 li aveva scambiati. La V0.7 li corregge in tabella e indica i rimanenti valori TI come riferimenti, NON come approvazione.

## Importanti limiti aperti
1. Non sono ancora cablati condensatori di bypass/alimentazione: 3V3_PLL_PENDING_DECOUPLING è un'etichetta di *lavoro*, non un rail approvato.
2. TCXO di 12.8MHz: da definire circuito d'accoppiamento, swing e pinout fisico; OSCinP/M richiedono accoppiamento AC secondo TI.
3. Uscite RF A/B: richiedono accoppiamento AC e rete di terminazione/buffer; uso B da stabilire.
4. GPIO CE, SYNC, SYSREF, RampClk/Dir: stato a reset e comportamenti definiti dal firmware da finalizzare, eventualmente pull resistors.
5. Riferimenti elettrici per alimentazione a basso rumore, test-points e connettori assenti.
6. La libreria e il footprint proposto sono un **placeholder da controllare** con la land-pattern TI prima del layout.
7. Non è stato eseguito KiCad ERC / export netlist / DRC (KiCad CLI non installato). Solo controllo automatico di struttura e completamento pin.
8. Nessun progetto `.kicad_pcb` e nessun file PCBWay.
9. **Non** interpretare le etichette di rete come cablaggio completo di supporto o scheda pronta.

## Fonti
- TI LMX2572 datasheet SNAS740B: https://www.ti.com/lit/ds/symlink/lmx2572.pdf (p.4, pinout; sezioni applicative)
- TI LMX2572 EVM SNAU217B: https://www.ti.com/lit/ug/snau217b/snau217b.pdf (p.13-14, schematic)
- Formato schema KiCad: https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/

## Gate V0.8
Aprire realmente file in KiCad, correggere eventuali incompatibilità, disegnare il bypass e alimentazioni con parts scelti, circuiti TCXO e control/reset, eseguire ERC, simulare filtro con PLLatinum/TICS e dati reali TI.
