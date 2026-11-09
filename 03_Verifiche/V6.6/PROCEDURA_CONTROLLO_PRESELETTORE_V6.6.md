# V6.6 — Protocollo verifiche incrementali e futura validazione hardware

## Effettivamente eseguiti in chat

- Matrice nodale complessa a 2 porte per L/C con resistenze serie (QL/QC ipotizzati), capacità winding via SRF ipotizzata e bypass parassita ingresso-uscita C_FEED variabile.
- Calcolo di S21, S11 e reiezione relativa su 270 canali e 270 immagini, 4.000 prove esplorative di tolleranza indipendenti, sweep C_FEED=0..1pF.
- Confronto coerente con filtro ideale della V6.5 e nuova rete reale nominalizzata a 50Ω. Test unitari e test regressione V6.5.

## Da eseguire con modello vendor e strumenti (NON eseguiti)

1. MPN fisici L601–603: misurare Q effettivo e SRF almeno 20–150MHz, capacità C0G e tolleranze; estrarre modello S-parassita su footprint reale.
2. In ambiente KiCad: caricare schematico **nuovo** non ancora creato, footprint e land pattern dei connettori o SXBP; eseguire ERC, DRC, simulare RLC con ngspice/gestione ERC native.
3. VNA calibrato SOLT 50Ω ai connettori del filtro; S11 ed S21 su 20–70MHz, poi 270 frequenze RX e immagine, in almeno 3 punti temperatura. Mappare S21 in banda e stop e return loss (es. RL >=10dB preliminare).
4. RF injection separata: livelli di blocker realistici al filtro e prima del LNA; misurare desensibilizzazione, IMD, compression e NF del modulo completo. Nessuna stima dei 40dB come criterio normativo: soglia solo interna provvisoria.
5. Se SXBP-27R5+: validare specifica vendor nel punto 47–50MHz, footprint HF1139 (pad 1/8/2–7), schermatura, distanze, spazio chassis; il filtraggio anti-immagine nominale non autorizza una cascata dB senza misura S-parametri.
6. Protezione ESD/antenna e isolamento TX: accoppiamenti e transitori validati prima di qualunque fabbricazione; TX esclusa nel prototipo RX.

**Stop condition:** fabbricazione inibita finché source+load 50Ω, componenti, RF-layout e risultati VNA non sono stati qualificati (NO FAB / NO TX).
