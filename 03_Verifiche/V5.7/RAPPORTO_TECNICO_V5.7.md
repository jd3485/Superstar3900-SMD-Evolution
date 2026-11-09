# Rapporto tecnico V5.7 — Studio geometrico dei piani GND prima del riempimento

**Progetto:** Superstar 3900 SMD Evolution — modulo RX test 50 Ω; **data:** 8 novembre 2026.  
**Stato:** NON PER FABBRICAZIONE; ERC/DRC KiCad nativi non eseguiti; zero hardware validato; NO TX.

## Scopo e risultati riproducibili

Il PCB candidato della V5.2 conserva quattro zone `GND_RF` **non riempite** su `F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`. Nella V5.6 erano stati rilevati 64 gruppi di GND sul rame F.Cu non riempito (24 con almeno una piazzola, 40 di soli via). In V5.7 l'audit `audit_piani_gnd_v57.py` misura la possibilità **soltanto geometrica** di creare una zona continua, senza effettuare un riempimento KiCad.

**Calcolo:** per ciascuno strato si parte dal contorno della zona (108,6 × 60,6 mm = 6.581,16 mm²); su F.Cu si sottrae l'unione dei pad e segmenti di reti diverse da GND dilatati di **0,30 mm**. È un'approssimazione permissiva e monostrato: non include termiche, filtri per larghezze minime, rimozione delle isole, regole del progetto prevalenti, tensioni, geometria del foro e stack-up. Sugli strati interni e inferiore non sono presenti piste/vie di rete diversa dalla massa nel sorgente analizzato, e perciò il modello restituisce l'intero contorno; ciò NON implica che KiCad lo riempirà integralmente.

| Strato | Superficie ideale stimata | Regioni ideali | Vie GND geometricamente nel contorno | Vie con intersezione nella maggiore regione ideale |
|---|---:|---:|---:|---:|
| F.Cu | 6.323,1039 mm² (96,08%) | 1 | 70/70 | 70/70 |
| In1.Cu | 6.581,16 mm² (100% geometrico) | 1 | 70/70 | 70/70 |
| In2.Cu | 6.581,16 mm² (100% geometrico) | 1 | 70/70 | 70/70 |
| B.Cu | 6.581,16 mm² (100% geometrico) | 1 | 70/70 | 70/70 |

La distanza minima fra **bordo del rame del via GND** e contorno della zona è **2,05 mm**. Le **24 piazzole GND F.Cu** toccano il poligono ideale principale secondo il modello. Questo evidenzia che non è stato rilevato un problema macroscopico di collocazione degli ancoraggi di massa. **Non certifica nessuno dei 64 collegamenti effettivi:** anche un semplice pad che interseca il poligono ideale può risultare scollegato se una termica non viene generata o viene rimossa da regole DRC.

## Requisiti del modello, fallimenti controllati e test

- Controllo presenza di quattro zone corrette, non riempite, con i parametri attuali (clearance 0,30 mm; gap termico 0,40 mm; ponte termico 0,50 mm).
- Controllo anelli in rame delle 70 vie entro il contorno delle quattro zone e margine del contorno rispetto al bordo scheda.
- Controllo assenza nel modello di rame non-GND su piani interni; se i sorgenti lo introducono, il programma va in stato `STATIC_ENVELOPE_FAIL` anziché fingere di modellarlo.
- Rilevamento di geometrie alterate nei test (via fuori zona, net errata, zone duplicate, layer errato, parametri termici modificati, zone dichiarate già riempite, contorno vicino al bordo, pista spostata su interno).
- **30/30 nuovi test** superati; **18/18 suite software dalla V4.0 alla V5.7** superate, incluso il supervisore a 2.400 combinazioni.
- Il runner V5.7 ha registrato `NOT_RUN_KICAD_MISSING` con uscita di blocco. L'automazione GitHub Actions V5.7 è presente soltanto come file locale; non è stata caricata né avviata.
- Nessun file `.kicad_pcb`, `.kicad_sch` o libreria originale è stato modificato.

## Cosa significa davvero il risultato

L'esito `STATIC_ENVELOPE_PASS_NATIVE_PENDING` significa esclusivamente che l'analisi delle sagome **non trova ostacoli macroscopici** nella porzione di rame considerata. La superficie interna al contorno è un *limite geometrico superiore*, non un'area del rame realmente riempita, verificata o producibile. Rimangono completamente aperti: riempimento reale, thermal spokes su U101 e sui piccoli pad di massa, rimozione delle isole, clearance reale e fabbricante, parità schema-PCB, controllo interlayer, integrità RF e messa a terra.

Il comando KiCad 10 necessario è `kicad-cli pcb drc --refill-zones --schematic-parity ...` sulla copia di lavoro, più ERC nativo. I report completi devono essere verificati in particolare per `unconnected_items`, errori, warning e parità. Cfr. [KiCad 10 PCB Editor — zones](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) e [KiCad 10 CLI](https://docs.kicad.org/10.0/en/cli/cli.html).

**Gate produttivi:** restano aperti tutti i 9 gate definiti in V5.0. Il CAD ufficiale TE dello SMA CONSMA002-SMD-G, la valutazione VIPPO/stencil U101, lo stack-up 50 Ω, la dissipazione termica e il collaudo fisico non sono stati approvati. PCBWay/TX vietati. Percentuale globale documentale storica 37% (non misura di avanzamento hardware).

## File di prova

- `03_Verifiche/V5.7/audit_piani_gnd_v57.py` — sorgente calcolo.
- `03_Verifiche/V5.7/AUDIT_PIANI_GND_V5.7.json` e `SINTESI_PIANI_GND_V5.7.csv` — risultati calcolati.
- `03_Verifiche/V5.7/test_piani_gnd_v57.py` e `TEST_V5.7.txt` — 30 prove.
- `03_Verifiche/V5.7/run_piani_e_kicad_v57.py` e `NATIVE_NOT_RUN/STATUS_V5.7.json` — runner fail-closed locale.
- `.github/workflows/kicad_native_v57.yml` — workflow CI **solo predisposto, non eseguito**.
- `03_Verifiche/V5.7/run_regressioni_v57.py` e `REGRESSIONI_V5.7.json` — regressioni.
