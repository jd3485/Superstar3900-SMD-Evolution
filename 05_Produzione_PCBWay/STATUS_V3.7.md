# PCBWay — V3.7 stato BLOCCATO

Questa PCB KiCad è un **coupon esclusivamente RX**; non è un dispositivo radio finale e **non deve essere connessa al trasmettitore**.

Motivi bloccanti:
- Footprint del connettore CONSMA002-SMD ancora NON conforme al disegno completo del produttore (contorno GND), assenza di verifica corpo/3D e edge overhang.
- ADL5535: impronta termica candidata, non convalidata paste-mask e vias-in-pad.
- Zone di massa NON riempite, quattro strati senza stack-up confermato.
- Esecuzione KiCad ERC/DRC nativi non effettuata, verifica della scheda in ambiente grafico non effettuata.
- RF S11, S21, rumore, termica e linearità mai misurati con hardware.

Non sono stati generati file Gerber, drill, pick-and-place per produzione. Ordine PCBWay NON approvato.
