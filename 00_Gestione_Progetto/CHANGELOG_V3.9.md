# V3.9 — verifica documentale del connettore SMA e trasferimento per CAD nativo
Data: 2026-11-08

**Avanzamento complessivo stimato: 37% (invariato). NO FAB / NO PCBWAY.**

## Attività realmente eseguite
- Ricontrollato l'archivio base V3.8: ZIP con CRC valido e 605 impronte SHA-256 corrispondenti al manifest originario; superati i test di regressione V3.8 (44/44) e V3.7 (17/17).
- Individuata la pagina ufficiale TE del codice esatto `CONSMA002-SMD-G`. Il disegno cliente **C-CONSMA002-SMD-X-X rev D** tratta sia la variante standard sia la `-G`; la tabella distingue la finitura del corpo (nickel vs oro), non definisce un footprint KiCad verificato.
- Verificato il disegno TE (foglio 2): centro Ø2,05 mm, figura circolare Ø4,56 mm e dimensione esterna verticale del footprint raccomandato 7,76 mm. Le quattro piazzole custom GND V3.8 hanno inviluppo totale verticale **7,40 mm**; scostamento nominale **-0,36 mm**. Non si assume equivalenza funzionale né capacità di saldatura: la geometria raccomandata deve essere tradotta/confrontata nel CAD ufficiale.
- Creato nuovo audit statico riproducibile `03_Verifiche/V3.9/review_v39.py` e risultato JSON, con riferimento all'hash del PCB V3.8.
- Preparata procedura d'accettazione V3.9 per KiCad 9/10, apparati RF e produzione.
- Nessun cambiamento alle piste o ai footprint del prototipo V3.8; nessuna approvazione produzione e nessun Gerber creato.

## Bloccanti rimasti
1. Footprint ufficiale e meccanica 3D `CONSMA002-SMD-G` da confrontare e approvare (disegno condiviso per finiture, ma land pattern V3.8 non approvato).
2. KiCad `kicad-cli` non presente nell'ambiente: no ERC/DRC native, no refill delle 4 zone GND.
3. Pad termico e processo pasta/reflow U101 ADL5535 non qualificati.
4. Stack-up e impedenza controllata PCBWay, prove VNA e collaudo RX non verificati.

**Decisione: V3.9 è una revisione di audit, NON un PCB V3.9 pronto alla produzione. Conservare il PCB di prova V3.8 come sorgente immutata.**
