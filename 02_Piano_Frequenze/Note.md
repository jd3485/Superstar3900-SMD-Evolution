# Piano canali

La tabella comprende 240 canali ordinari (6 × 40) e 30 canali Alfa (6 × 5): 270 frequenze uniche. La manopola normale seleziona 1–40, mentre il comando ALFA separato aggiunge 10 kHz nei soli canali 3, 7, 11, 15 e 19. Nei restanti il comando non modifica la frequenza.

**Attenzione:** alcuni apparati espansi usavano collegamenti o firmware diversi; confrontare con la specifica variante storica prima di fissare la grafica del pannello.

Eccezione storica: in ogni banda, i canali 23, 24, 25 non sono in ordine crescente di frequenza. Non usare una semplice formula `freq_inizio + (canale-1)*10 kHz`.

Il richiamo CH9 ha priorità su banda/canale/ALFA e seleziona 27,065 MHz, AM, ripristinando lo stato precedente quando viene rilasciato. Il ripristino della modalità viene implementato nel firmware completo.

Le colonne TX sono soltanto vincolo di progettazione: non dichiarano l'apparato già conforme e non abilitano automaticamente la trasmissione.
