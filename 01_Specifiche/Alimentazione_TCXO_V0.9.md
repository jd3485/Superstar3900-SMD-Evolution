# S3900E V0.9 - Alimentazioni PLL e TCXO (BOZZA)

## Novita, fonte e campo di applicazione

**NON FABBRICABILE.** Modulo alimentato da una rete esterna protetta 5.0 V, non da 13.8 V diretti.
Il preregolatore 13.8 -> 5.0 V e le protezioni di ingresso non sono ancora progettati.

Scelta: **due TPS7A2033PDBVR** 3.3 V, SOT-23-5, 300 mA massimi
- U2 alimenta i sei pin VCC PLL (net `3V3_PLL_INPUT_FROM_LDO`).
- U3 alimenta soltanto TCXO 12.8 MHz (`3V3_REF_LDO`).
- EN collegato alla rete +5V per avvio simultaneo nella bozza; sequenziamento non definito.
- Ogni regolatore: C_IN=2.2uF X7R 10V 0805, C_OUT=4.7uF X7R 10V 0805, Cbulk=10uF X7R 10V 0805.
- TI TPS7A20 richiede **almeno 1uF effettivo in uscita**: perdita di capacita per DC bias/tolleranze da controllare sui codici esatti, non solo nominale.
- I bypass 1u V0.8 sono integrati da sei 100n X7R 0402 vicini ai pin VCC PLL, coerentemente con raccomandazione TI. Materiale e posizione fisica da definire sulla PCB.

## TCXO

Y1 TXC `7N-12.800MBP-T`, CMOS, 3.3V, 12.8MHz, <10mA (fonte serie TXC e catalogo DigiKey).
- Pin 4 GND, 5 OUT, 8 OE/Tri-State, 9 VCC; pad NC: 1,2,3,6,7.
- R60=10k pull-up enable; il comportamento esatto OE e pin **10 AFC/GND sono PUNTI BLOCCANTI** prima della PCB.
- U1 LMX2572 pin 8 OSCinP riceve dal TCXO via R61=33R e C58=100nF in serie;
  pin 9 OSCinM lasciato esplicitamente NC per ingresso single-ended,
  registro R5: `IPBUF_TYPE=1`. Valore R/C e segnale risultante da verificare al banco.
- C56=100nF, C57=1uF su alimentazione TCXO; posizionare vicino a Y1.
- Il footprint TCXO nel file KiCad e un **segnaposto NON presente in libreria valida**.

## Vincoli elettrici e termici (non misurati)

- LMX2572 VCC consentito 3.0-3.5V. 3.3V nominale del TPS7A20, tolleranza max +/-1.5%, entro gamma nominale.
- TPS7A20 VIN max 6V: e vietato il collegamento a 13.8V.
- Esempio P dissipata U2 (5.0-3.3)*0.090=0.153W; U3 0.017W con 10mA.
- Caso di studio U2 a 5.25V e 100mA: 0.195W; con thetaJA ipotizzata 199.6 C/W, +38.9C.
  Valori di corrente e thetaJA sono stime conservative e variano con PCB, configurazione PLL e temperatura.
- TCXO +/-0.28ppm STABILITA TERMICA nominale corrisponde a +/-10.92Hz su LO 39MHz,
  senza includere tolleranza iniziale, invecchiamento e altri errori.

## Sorgenti, da ricontrollare all'approvazione BOM
- TI LMX2572 https://www.ti.com/lit/ds/symlink/lmx2572.pdf (p.15, p.64, p.79)
- TI TPS7A20 https://www.ti.com/lit/ds/symlink/tps7a20.pdf (p.1, p.4, p.27-32)
- Specifico part number TPS7A2033PDBVR: https://www.ti.com/product/TPS7A20/part-details/TPS7A2033PDBVR
- TXC 7N 10-pin: https://www.nyang-tech.com/datasheet/1164170051/TXC-Corporation/7N-12.800MBP-T.pdf
- DigiKey 7N-12.800MBP-T: https://www.digikey.com/en/products/detail/txc-corporation/7N-12-800MBP-T/5222401

**Stato**: file schematico modificabile, solo controllo sintattico Python e controllo nonnetlist dei riferimenti; no KiCad-cli, nessun ERC, nessuna simulazione SPICE, nessun PCB.
