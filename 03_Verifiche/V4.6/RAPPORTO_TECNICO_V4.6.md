# Superstar 3900 SMD Evolution — Rapporto tecnico V4.6

**Data:** 8 novembre 2026. **Ambito:** solo modulo RF sperimentale RX a 50 Ω.
**Classificazione:** audit geometrico statico + preflight KiCad portabile, **NON PER FABBRICAZIONE**.

## Risultato

1. Analizzato senza modifiche il PCB del candidato V4.5, SHA-256 `a49a4fa9370573192dfa4f3da0b16f9936cf580491280621a4ea30d24349848f`.
2. ADL5535 U101: pad di massa esposto nominale 1,800 × 3,480 mm = 6,264 mm² di rame; nessun centro di via GND all'interno del rettangolo. Via GND più vicino a (68,00; 31,05) mm, diametro rame Ø0,70 mm, foro Ø0,30 mm. Gap geometrico tra rame di pad e rame di via: **0,50 mm**. Queste grandezze **non** misurano la resistenza termica né la reale continuità dei piani, essendo zone non riempite nativamente.
3. Quattro zone dichiarate: F.Cu, In1.Cu, In2.Cu, B.Cu; 64 via nominati GND nel file. Il riempimento e la connessione globale rimangono NON PROVATI.
4. SMA J101–J104: ciascuno ha un pad centrale e quattro forme custom di massa. La correzione di inviluppo V4.3 è **ipotesi**: il CAD TE DXF/STEP è elencato sul sito ufficiale, ma download non riuscito nell'ambiente di lavoro; nessun confronto dimensionale completo, nessuna approvazione.
5. Definita procedura `RUN_KICAD_RX_V46.sh`: lavora su copia temporanea, verifica `kicad-cli pcb drc --help` e la presenza di `--refill-zones` (richiesto e documentato in KiCad 10, non documentato in KiCad 9), `--schematic-parity`, `--exit-code-violations`, `--format`. Se la funzione non esiste, **FAIL-CLOSED** senza finti risultati. ERC e DRC sono eseguiti solo se il tool è effettivamente presente e compatibile. Non esporta Gerber, non usa `--save-board` e non modifica gli originali.
6. Qui KiCad non è installato: il test effettivo è **NOT_RUN, codice 3**. I test di sostituzione binaria KiCad 9/10 sono **mock**, servono soltanto a verificare il comportamento della procedura e NON dimostrano alcun ERC o DRC.

## Test della revisione

- **24/24 test V4.6 superati**: identificativi, quote e posizione, anomalie deliberate (via nel pad), hash della scheda, quantità e livelli delle zone, pannello SMA, supervisione opzioni KiCad assenti/presenti in mock e assenza di modifiche ai sorgenti.
- Regressioni del codice originale V4.0–V4.5 rieseguite con esito positivo, con log separati. Non si deduce da esse alcuna prestazione hardware.
- Gli esiti sono in `TEST_V4.6.txt`, `AUDIT_TERMICA_SMA_V4.6.json`, `REGRESSION_*.txt` e `PROVA_NO_KICAD/STATUS.txt`.

## Decisione di conformità

| Controllo necessario | Stato V4.6 |
|---|---|
| ERC schema in KiCad nativo | NON ESEGUITO |
| DRC, refill, parity in KiCad nativo | NON ESEGUITO |
| Geometria TE CONSMA002-SMD-G vs footprint | NON APPROVATA |
| Pasta, solder mask, stencil, 3D e bordo connettore | NON APPROVATI |
| Thermal pad, via GND, θ termica e temperatura U101 | NON APPROVATI |
| Stack-up del produttore e calcolo 50 Ω | NON DEFINITI |
| Misure VNA S11, S21, rumore, corrente, temperatura | NON ESEGUITE |
| Hardware validato | 0 moduli |
| Rilascio PCBWay / fabbricazione | **NO-GO** |

**Prossimo checkpoint V4.7**: acquisire fisicamente STEP/DXF e disegno di montaggio TE; calcolare/meccanizzare il footprint con il componente esatto, poi KiCad 10 reale su macchina adatta con `RUN_KICAD_RX_V46.sh`, rapporto su zone ricaricate e parità schema/PCB. Analisi termica U101 con condizioni ambientali e dati di PCB verificati. Solo dopo queste attività si può valutare un prototipo RX di misura, senza TX.

## Fonti ufficiali consultate 08/11/2026

- TE Connectivity, `CONSMA002-SMD-G`, sezione **Product Drawings / CAD Files** e nota **Use the Product Drawing for all design activity**: https://www.te.com/en/product-CONSMA002-SMD-G.html
- Analog Devices, datasheet **ADL5535 Rev. A**, p. 11, Figure 17, pad esposto e pin 2 verso piano GND, via di collegamento degli strati: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- KiCad **9.0 CLI**, `pcb drc`, elenco opzioni senza refill: https://docs.kicad.org/9.0/en/cli/cli.html
- KiCad **10.0 CLI**, `pcb drc` con `--refill-zones` e `--save-board` opzionale: https://docs.kicad.org/10.0/en/cli/cli.html

## Riproduzione

```bash
python3 03_Verifiche/V4.6/audit_rischi_v46.py
python3 03_Verifiche/V4.6/test_rischi_v46.py
bash 03_Verifiche/V4.6/RUN_KICAD_RX_V46.sh ./KICAD_V46_NATIVE_REPORTS
```

Il terzo comando deve partire da una macchina con KiCad 10; un codice di uscita 0 conferma soltanto l'esecuzione tecnica senza violazioni segnalate dal comando, **non** l'approvazione per la produzione.
