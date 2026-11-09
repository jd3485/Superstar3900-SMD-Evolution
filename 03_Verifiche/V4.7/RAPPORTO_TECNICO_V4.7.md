# Superstar 3900 SMD Evolution — rapporto tecnico V4.7

**Data:** 8 novembre 2026 · **Ambito:** modulo RX RF sperimentale 50 Ω · **Stato:** NON RILASCIATO / NON FABBRICABILE.

## Risultato in sintesi

La V4.7 aggiunge un confronto **statico tracciabile** del footprint del connettore SMA `CONSMA002-SMD-G` con alcune quote del *disegno originale del produttore* TE `C-CONSMA002-SMD-X-X`, rev. D. Non modifica il PCB candidato V4.5 (derivato dall'ipotesi V4.3), il PCB originale V3.8, lo schema elettrico o le librerie. La geometria TE DXF/STEP del part-number preciso è elencata sul sito ma non è stata scaricata/importata. Il produttore avverte di usare il **Product Drawing** per la progettazione.

## Confronto dimensionale limitato

| Elemento | Quote TE / riferimento | Risultato sul footprint di studio | Esito |
|---|---:|---:|---|
| Numero e tipo | CONSMA002-SMD-G, diritto angolo, 50 Ω | 4 posizioni J101–J104 con libreria personalizzata | Identificazione verificata nel modello |
| Disco/pad centrale indicato nel disegno | Ø **2,05 mm** | disco Cu Ø **2,05 mm** | Corrispondenza di UNA quota |
| Inviluppo verticale della zona GND | **7,76 mm** | Y -3,88…+3,88 = **7,76 mm** | Corrispondenza di UNA quota |
| Altre dimensioni disegno TE | **2,44 mm; 2,88 mm; Ø4,56 mm** | Quattro isole sagomate; larghezza locale in X **1,87 mm** | **Da registrare con corretti datumi su DXF TE**; NON approvato |
| F.Mask/F.Paste sulle 4 isole | Profilo stencil/mask da approvare | Per ciascuna isola F.Cu + F.Mask + F.Paste senza riduzione esplicita | **Da approvare con montatore** |
| Courtyard e ingombro corpo | STEP/quote fisiche | Envelope solo di studio; sbalzo oltre il bordo già segnalato | **Da confrontare in 3D** |
| Giunzione RF e 50 Ω | Stack-up e transizione ottimizzati | Piste di studio e piani non qualificati | **Da simulare/misurare** |

**Nota importante:** la quota TE 2,44 mm **non viene automaticamente equiparata** all'estensione X di una singola isola di rame. La figura del produttore include geometrie/tagli e datumi che non sono stati registrati su un DXF. Non concludere conformità né non-conformità definitiva dalla differenza numerica apparente. Il disegno/figura `GEOMETRIA_SMA_STUDIO_V4.7.png` rappresenta **solo** il nostro footprint, non una copia del disegno TE né un overlay CAD.

## Dissipazione ADL5535 — nota stencil

- U101: pad esposto di rame **1,80 × 3,48 mm**, area nominale **6,264 mm²**.
- Il pad espone `solder_paste_margin_ratio = -0,100`: secondo la formula nominale dimensionale del modello, ciò porta a frazione d'area di pasta **81%** (circa **5,0738 mm²**) per un'unica apertura. È un dato di modellazione della pasta, NON una verifica del volume depositato e del processo di saldatura.
- Il via GND più vicino è esterno alla piazzola: distanza rame-rame **0,50 mm**, nessun centro di via nel pad (audit V4.6). Non si è eseguito calcolo di resistenza termica del PCB, misura termica o approvazione dello stencil.
- ADI chiede che exposed paddle e pin 2 siano saldati a un piano GND a bassa impedenza e che i piani di massa multilayer siano connessi mediante vias. **Blocco termico invariato.**

## Verifiche software e CAD

- `audit_te_sma_v47.py`: legge l'originale, pubblica un rapporto JSON, calcola quote locali e hash; non modifica le sorgenti.
- `test_audit_te_v47.py`: **28/28 test superati**, inclusi test su regressione/dati corrotti e invarianza byte della scheda.
- Regressioni rieseguite, senza fallimenti: V4.0 (2.400 combinazioni di supervisione), V4.1 (12), V4.2 (19), V4.3 (21), V4.4 (20), V4.5 (26), V4.6 (24).
- Lanciatore KiCad 10 V4.6 lanciato di nuovo: exit code **3**, stato **NOT_RUN**. Nessun `kicad-cli` nell'ambiente; tentativo di aggiornare i repository pacchetti impossibile per connettività. **ERC, DRC, parity, riempimento zone e 3D CAD NON ESEGUITI.**
- Nessun Gerber, ordine PCBWay, hardware validato o trasmissione RF.

## Gates per la V4.8 / primo prototipo

1. Acquisire DXF 2D e STEP 3D **del part-number esatto** da TE, mantenere URI/Rev/hash e verificare diritto di uso/redistribuzione. Sovrapporre profili F.Cu, F.Mask, F.Paste e courtyard; verificare sagoma, orientamento, datumi, tolleranze e sporgenza oltre il bordo. Se incompatibili, modificare SOLO una nuova copia del PCB con distinta revisione.
2. Eseguire KiCad 10 ERC, DRC con `--refill-zones`, `--schematic-parity`, librerie locali e rapporti JSON nativi; bloccare rilascio con violazioni. Riesaminare warning, false positive e pin-to-pad.
3. Definire stack-up da fabbricante e trasmissione a 50 Ω delle piste/transition SMA; richiedere VNA e misure S-parameters sul prototipo.
4. Dimensionare via/pad termico ADL5535 e definire stencil con assemblatore, poi misurare temperatura e corrente su scheda reale.
5. Verificare disponibilità commerciale del part-number; la pagina TE lo dichiara *Active* ma segnala indisponibilità sul proprio sito al momento della consultazione, dunque non è prova di approvvigionamento.

**DECISIONE:** proseguire in studio. **NO FAB / NO PCBWay / NO TX** fino a chiusura dei gate e approvazione ingegneristica.

## Fonti primarie

- [TE — pagina prodotto CONSMA002-SMD-G](https://www.te.com/en/product-CONSMA002-SMD-G.html) (disegno `C-CONSMA002-SMD-X-X`, rev. D; link DXF/STEP).
- [TE — Product Drawing C-CONSMA002-SMD-X-X](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=C-CONSMA002-SMD-X-X&DocType=Customer+Drawing&PartCntxt=CONSMA002-SMD-G) (foglio 2 di 3: footprint consigliato).
- [Analog Devices — ADL5535, Rev. A](https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf) (connessioni e land pattern).
- [KiCad 10 — CLI reference](https://docs.kicad.org/10.0/en/cli/cli.html) (opzioni per ERC, DRC, refill e parity).

**Avanzamento complessivo:** resta 37% stimato; **0 moduli hardware validati**. L'archivio della V4.7 rimane cumulativo e contiene tutti i manuali e gli storici.
