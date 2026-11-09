# Richiesta DFM: da sottoporre a PCBWay e all'assemblatore

**BOZZA NON INVIATA · non è un ordine PCB · progetto NON PER FABBRICAZIONE**

Oggetto: verifica preventiva processo via-in-pad e stencil — modulo test RF Superstar 3900

Buongiorno, stiamo studiando un PCB sperimentale a **4 strati e 1,6 mm nominali**, ancora non validato per la produzione. Sul pad di massa esposto di un ADL5535 in package SOT-89 sono previste **6 vie passanti GND**, con Ø rame 0,55 mm, Ø foro 0,25 mm, in una matrice 2×3. La piazzola esposta misura 1,80×3,48 mm; la finestra unica F.Paste proposta misura 1,62×3,132 mm. Tutte le sei vie ricadono all'interno della finestra di pasta.

Chiediamo una **valutazione di fattibilità senza avviare ordini** e una risposta scritta su:

1. Possibilità di riempimento con resina / pasta di rame e successiva **planarizzazione e cappatura in rame** per le 6 vie (specificare processo, spessore minimo della cappatura, tolleranze e verifica di assenza di vuoti).
2. Limiti del foro Ø0,25 mm, compatibilità con stack-up a 4 strati e 1,6 mm, processo metallizzazione, eventuale cambio diametro necessario.
3. Indicazioni per lo stencil del pad termico U101, percentuale consigliata di copertura, pattern di apertura e spessore stencil **da approvare con l'assemblatore**; no autorizzazione implicita all'uso della maschera attuale.
4. Indicazioni per ispezione e qualifica assemblaggio U101: vuoti, lift/off, planarità, gestione reflow e dissipazione, oltre alle verifiche elettriche.
5. Stack-up da proporre per trasmissione RF nominale 50 Ω a ~27 MHz e geometria delle piste; specificare materiali, costante dielettrica, rame e distanza del piano GND.
6. DFM di connettori SMA TE `CONSMA002-SMD-G` su bordo scheda: richiesta di confronto con il disegno CAD esatto. Non supponiamo che il footprint attuale sia approvato.
7. Costo/tempi indicativi delle diverse opzioni VIPPO, quantità minima e dati tecnici richiesti per un preventivo completo.

In questa fase chiediamo solo **indicazioni tecniche e accettazione dei requisiti**, non produzione, non assemblaggio e non file Gerber. I dati possono essere integrati dopo verifiche KiCad ERC/DRC e approvazione formale dei footprint.

**Stato risposta:** NON INVIATA / NESSUNA APPROVAZIONE RICEVUTA.
