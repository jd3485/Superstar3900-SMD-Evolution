# Superstar 3900 SMD Evolution — Rapporto V5.0

**8 novembre 2026 · Stato: ricerca e progettazione, 37% storico stimato, zero prototipi collaudati.** NO FAB / NO PCBWAY / NO TX.

## Obiettivo

Convertire il rischio via-in-pad/stencil U101 emerso nella V4.9 in un confronto misurabile fra soluzioni e in una procedura di verifica/rilascio fail-closed. Non viene modificato alcun file elettrico KiCad precedente.

## Risultati reali

- L'analisi V4.9 dal PCB candidato V4.8 ha confermato: pad 1,80×3,48 mm = 6,264 mm², stencil intero ridotto del 10% per lato = 1,62×3,132 mm = 5,07384 mm² = **81%** dell'area; sei fori Ø0,25 mm interamente sotto l'apertura.
- L'ipotesi alternativa V5.0 impiega **due aperture** da 1,50×0,62 mm fra le tre file di fori, per un totale di 1,86 mm², pari al **29,69%** del pad. La distanza minima geometrica bordo foro/apertura è **0,125 mm**. Questo dimostra il compromesso di copertura della pasta adottando questi rettangoli, **non** che ogni possibile alternativa sia impossibile.
- La copertura ridotta non può essere accettata come sostituto del VIPPO senza approvazione del montatore; opzione A con vie riempite e cappate resta ipotesi di lavoro prioritaria, comunque priva di approvazione.
- Creati `STUDIO_STENCIL_V5.0.json`, `CONFRONTO_STENCIL_U101_V5.0.svg` e lo script riproducibile `studio_stencil_v50.py`; sono tutti studi geometrici, NON CAM.
- Creato lanciatore per KiCad 10 `run_kicad_native_v50.py` con log e hash pre/post, sempre su copie. Qui `kicad-cli` manca e i controlli **ERC/DRC/refill/parità NON SONO STATI ESEGUITI**.
- Creato gate di rilascio `GATE_RELEASE_V5.0.json` con **9 condizioni aperte**, bloccante di default; nessun file di produzione è generato.
- Aggiunti un piano di collaudo RX e una richiesta DFM VIPPO/stencil che necessitano di fabbricante/assemblatore e strumenti reali; nessuna risposta scritta è stata ricevuta.

## Compiti bloccanti e priorità

1. Su macchina con KiCad 10: eseguire ERC/DRC con refill e parity; esaminare segnalazioni e risolverle su copia.
2. Ottenere il disegno DXF/STEP TE completo e approvare meccanicamente/elettricamente i quattro footprint SMA.
3. Chiedere a PCBWay e al montatore il processo di via-in-pad (riempimento/cappatura), stencil, tolleranze, ispezione e stack-up 50 Ω. Nessuna richiesta è stata inviata.
4. Valutare termica U101 sul PCB fabbricato, misurare S11/S21/S22 nell'intervallo d'uso, testare attenuatore e protezioni di alimentazione.
5. Dopo revisione ingegneristica e autorizzazione esplicita, valutare se preparare una revisione **separata** destinata al primo prototipo. Non usare V4.8/V5.0 per fabbricazione.

## Limiti delle prove

Misure esclusivamente nominali 2D; non includono registrazione delle maschere, tolleranze, riempimento materiale, simulazione termica, solder joint, affidabilità, EMC, prestazioni RF o certificazione normativa. I requisiti della radio finale (AM/FM/USB/LSB/CW RX, PA, sei bande A–F, 270 posizioni RX, ALFA/CH9, DSP/VOX/ATU) restano requisiti, **non** apparato funzionante. Il manuale V4.0 resta bozza.

**Riferimenti:** Analog Devices ADL5535 https://www.analog.com/en/products/adl5535.html · PCBWay via-in-pad https://www.pcbway.com/pcb_prototype/PCB_Via_in_Pad.html · TE SMA https://www.te.com/en/product-CONSMA002-SMD-G.html · KiCad 10 https://docs.kicad.org/10.0/en/cli/cli.html
