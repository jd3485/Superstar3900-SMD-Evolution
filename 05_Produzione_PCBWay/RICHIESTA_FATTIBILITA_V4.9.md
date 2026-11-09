# Richiesta di fattibilità tecnica — NON È UN ORDINE

**Superstar 3900 SMD Evolution, modulo ricevente sperimentale 50 Ω, revisione V4.9.**

Destinatari previsti: reparto DFM PCBWay e responsabile assemblaggio SMT. Documento da inviare soltanto dopo autorizzazione dell'utente; non è un file di produzione né una quotazione approvata.

## Dati del prototipo candidato

- PCB rigido sperimentale: **4 strati**, spessore nominale **1,6 mm**, dimensioni schematiche del coupon **110 × 62 mm** (da riconfermare nativamente), rete RF a 50 Ω non ancora validata.
- U101: Analog Devices ADL5535, SOT-89 con pad termico esposto **1,80 × 3,48 mm**, rete `GND_RF`.
- Variante termica in studio V4.8: **6 vie passanti nel pad**, schema 2×3, diametro rame **Ø0,55 mm**, foro **Ø0,25 mm**, anello nominale **0,15 mm**. Non sono garantite tolleranze e valori dopo galvanica.
- Stencil attuale: apertura F.Paste rettangolare teorica **1,62 × 3,132 mm**, copertura geometrica **81%**, interseca completamente tutti e sei i fori: **richiede revisione DFM e ASM**.
- Quattro SMA `TE CONSMA002-SMD-G`, footprint non ancora validato con DXF/STEP ufficiali.
- Nessun ERC/DRC KiCad nativo; nessun Gerber autorizzato; nessun hardware testato.

## Domande da confermare per iscritto

1. È possibile produrre **6 via-in-pad Ø0,25 mm foro / Ø0,55 mm rame su un PCB 4L da 1,6 mm** con il processo da voi suggerito? Specificare limiti di foro finito, anello, registrazione, spessori e tolleranze.
2. Quale processo raccomandate: riempimento e cappatura con resina non conduttiva, rame, o altra soluzione **planarizzata e idonea a ricevere lega saldante**? Indicare definizione del processo, se c'è metallizzazione del tappo, criteri d'ispezione e costi aggiuntivi.
3. La vostra procedura VIPPO richiede Gerber/ODB++ o fab note specifiche per marcare le sole sei vie U101? Come distinguere queste vie da tutte le altre?
4. Confermate che la superficie è sufficientemente **planare per il SOT-89** e compatibile con montaggio SMT? Quali criteri di accettazione proponete per vuoti / difetti sotto il pad?
5. Il montatore approva l'apertura F.Paste attuale oppure raccomanda una matrice di aperture (*windowpane*)? Chiediamo disegno stencil, spessore, copertura e specifica pasta/reflow **per approvazione prima di fabbricare**.
6. È disponibile una ispezione della saldatura del pad termico (ad esempio X-ray, dove utile)? Definire limiti di accettazione e report.
7. Potete fornire uno **stack-up 4L controllato a 50 Ω** con spessori dielettrici, Dk/Df alla frequenza d'impiego, rame finito, solder mask, distanza F.Cu–piano GND e tolleranza impedenza misurabile? La pista RF da 0,28 mm è solo un'ipotesi: va calcolata sullo stack-up reale.
8. È necessaria un'alterazione al layout SMA, al bordo o agli assemblaggi per il montaggio TE? Il CAD ufficiale del connettore non è ancora stato validato in 3D.
9. Indicare costo/tempo indicativi **di fattibilità e revisione DFM soltanto**, non di produzione; chiarire quali documenti servirebbero per una futura quotazione.

## Gate obbligatori prima del via libera

Servono: risposta scritta del fabbricante; approvazione dell'assemblatore; stencil validato; CAD TE confrontato; stack-up RF approvato; ERC, DRC e parity KiCad nativi; verifica termica documentata; BOM completa. **Non autorizzare ordine o Gerber di produzione sulla base di questo documento.**

## Riferimenti

- https://www.pcbway.com/pcb_prototype/PCB_Via_in_Pad.html
- https://www.pcbway.com/capabilities.html
- https://www.pcbway.com/helpcenter/ordering_parameter_instruction/Via_Filled_with_Copper.html
- https://www.analog.com/en/products/adl5535.html
