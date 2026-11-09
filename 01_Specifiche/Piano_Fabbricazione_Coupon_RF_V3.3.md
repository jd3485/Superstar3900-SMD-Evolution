# Coupon RX 50 Ω V3.3 — piano di fabbricazione, NON autorizzato

## Scopo
Due percorsi RF separati: ADL5535 + polarizzazione a 5 V e attenuatore resistivo a π da 6 dB. Il progetto **non** è collegabile alla trasmissione né all'antenna durante un PTT.

## PCB sperimentale
- Ingombro preliminare: 110 × 62 mm, spessore ipotizzato 1,6 mm.
- 4 strati previsti: L1 RF/SMD, L2 massa continua, L3 alimentazione/ausiliaria, L4 massa.
- Il file `.kicad_pcb` contiene 15 footprint, 8 reti, il bordo e le coordinate; **zero tracce e zero zone di rame**. Non generare Gerber per fabbricazione.
- Larghezza RF da 50 Ω **non ancora fissata**: richiede stack-up PCBWay finale e calcolatore del campo elettromagnetico.
- La seconda faccia della scheda non contiene attualmente alcun rame dedicato. I piani saranno definiti in routing.

## Bloccanti prima di fabbricare
1. Conferma al 100% del land pattern SMA CONSMA002-SMD, orientamento, quota dalla fresatura e ingombro meccanico.
2. Verifica geometrica pad SOT-89-3 contro figura 17 del datasheet ADL5535, inclusa dissipazione e via stitching sul tab GND.
3. Correzione dello schema V3.1: assegnare footprint e verificare la concordanza pin/net; aggiornare da KiCad la PCB.
4. Completare routing F.Cu con piste controllate 50 Ω; pianificare massa In1.Cu e raccordi SMA.
5. Inserire condensatori e induttore esatti con MPN, e controllare SRF, tolleranza e ingombro.
6. Controlli nativi KiCad ERC + DRC senza violazioni bloccanti, e verifica visiva Gerber/fori prima di PCBWay.
7. Simulazione e misura almeno S11, S21 e corrente a 5 V su carico fittizio, alimentatore limitato in corrente.
8. La protezione TX/RX del ricetrasmettitore finale resta fuori da questo coupon.

## Riferimenti primari
- Analog Devices ADL5535: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- Linx CONSMA002-SMD: https://www.ic-components.kr/files/17/CONSMA002-SMD.pdf
- KiCad formato PCB: https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/
