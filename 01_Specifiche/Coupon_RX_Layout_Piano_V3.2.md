# V3.2 — Piano fisico coupon RX 50 Ω / NON APPROVATO PER FABBRICAZIONE

**Scopo limitato:** progetto sperimentale di banco ricevitore (nessun circuito TX, antenna diretta o protezione TX/RX).
**Stato:** proposta di posizionamento 110 × 62 mm, SENZA piste in rame, file `.kicad_pcb` o Gerber. Non è una scheda elettricamente verificata.

## Sezioni
- LNA: J101 → C101 → U101 ADL5535 → C102 → J102. Bias RF tramite L101 e condensatori C103/C104/C105; Pin 2 e pad inferiore di U101 a massa.
- PAD 6 dB: J103 → R201 (shunt) → R203 (serie) → R202 (shunt) → J104.
- Alimentazione: J105 5 V **da sorgente da banco limitata in corrente**, non collegata a 13,8 V. No interfaccia TX.
- Ingombro proposto 110 × 62 mm, 4 strati, coordinate in `Piano_Posizionamento_V3.2_PRELIMINARE.csv`.

## Scelte footprint (da completare in CAD)
- Connettore **TE/Linx CONSMA002-SMD**, 50 ohm, SMA femmina a 90°, SMT; 4 pezzi. Nelle immagini del produttore sono mostrati quattro pad massa e un contatto centrale. **Footprint non disegnato definitivamente:** confermare separazione pin, fori/area meccanica, parete di montaggio e saldatura contro il drawing REV D prima di qualsiasi Gerber.
- U101 **ADL5535ARKZ-R7**, SOT-89, 20 MHz–1 GHz, 5 V, 97 mA tipici. Il datasheet richiede saldare pin 2 e paddle a massa, con via di collegamento ai piani di massa. Verificare pattern ADI vs KiCad `Package_TO_SOT_SMD:SOT-89-3` prima del commit.
- L101 470 nH: impronta 0603 candidata, **codice e caratteristiche RF (Q, SRF, corrente) da confermare**.
- R201/R202 150 ohm, R203 37,4 ohm, impronte 0402 candidate. Componenti da selezionare per tolleranza e potenza.
- C101/C102 100 nF 0402; C103 68 pF e C104 1,2 nF 0603, C105 1 uF 1206 (basati su ADI EVAL): codici e package reali ancora non approvati.
- J105 5 V/GND: cablaggio/footprint da definire, **non inventare** footprint.

## Stack-up preliminare PCBWay
- L1: componenti, RF, corti collegamenti di bias.
- L2: piano massa **continuo**, nessuna spaccatura sotto RF, ritorni di corrente.
- L3: distribuzione lenta di +5 V locali su isola e massa nel resto.
- L4: piano massa e segnalazioni lente, evitare ritorni attraversanti.
- Per un *esempio* di PCBWay 4-layer da 1,6 mm, il dielettrico L1–L2 dopo laminazione è circa **0,1855 mm**, er nominale **4,74** del prepreg. È soltanto **uno** stack-up disponibile, NON confermato per ordine.
- Modello analitico microstrip a spessore di rame nullo e senza solder-mask: con h=0,1855 mm ed er=4,74, larghezza 50 ohm **0.338 mm**, e pista da 0,34 mm circa **49.8 ohm**. **Non trasformare questi numeri in regola finale di layout!** Spessore rame, solder mask, topologia CPWG, pad SMA e tolleranze devono essere verificati con stack-up confermato e field solver.
- Studiare fence di via massa e via termiche intorno a U101 senza creare corti o compromettere i piani. Quantità e fori ancora da definire.

## Dissipazione e prove
- A 5,0 V e 97 mA tipici, potenza elettrica assorbita di ordine **0,485 W**; non coincide con la dissipazione di giunzione certificata. Verificare caso peggiore, resistenza termica e temperatura in collaudo.
- Ispezione visiva/polarità, continuità e isolamento 5 V-GND a scheda non alimentata.
- Alimentazione limitata in corrente e solo generatore RF debole. VNA SOLT ai piani di riferimento dei connettori e misure S11/S21; NF e IIP3 con strumenti appositi. Nessuna potenza TX.

## Bloccanti
1. ERC nativo KiCad e corretta connettività schematico;
2. Footprint/SMA meccanici verificati contro drawing in scala;
3. PCB `.kicad_pcb` con stackup PCBWay ordinato e routing calcolato;
4. DRC nativo, netlist e controllo geometrico delle via;
5. BOM e fornitura dei componenti verificati;
6. Protezione RX/TX / ESD, non presente sul coupon;
7. Fabbricazione, calibrazione e misure VNA/NF/IIP3 sul prototipo.

## Fonti
- ADL5535 datasheet/prodotto: https://www.analog.com/en/products/adl5535.html
- EVAL ADL5535, PCB 4 layer: https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-adl5535.html
- TE/Linx CONSMA002-SMD drawing REV D: https://www.ic-components.kr/files/17/CONSMA002-SMD.pdf
- PCBWay stackup: https://www.pcbway.com/multi-layer-laminated-structure.html
