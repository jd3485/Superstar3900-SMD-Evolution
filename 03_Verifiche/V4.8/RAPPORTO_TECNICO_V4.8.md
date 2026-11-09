# Superstar 3900 SMD Evolution — relazione V4.8

**8 novembre 2026 · Stato: ESCLUSIVAMENTE STUDIO; NO FAB / NO PCBWAY / NO TX.**

## Avanzamento effettivo

Creata una **copia reversibile** del progetto KiCad V4.5, denominata `04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB`, contenente unicamente sei nuove vie GND sul pad esposto U101 ADL5535. Il progetto originale V3.8, la variante SMA V4.3 e il candidato portabile V4.5 rimangono **inalterati**. Schema e footprint (pad, mask, paste) sono invariati anche nella variante V4.8; cambia solo il numero delle vie sul PCB.

La modifica nasce dalla Figura 17 del datasheet ADL5535 Rev. A, pagina 11: per ridurre l'impedenza termica occorre collegare paddle esposto e pin 2 a GND, con vias che colleghino i piani multilayer. Il disegno ADI mostra una matrice di fori/vie, ma **non** autorizza automaticamente la misura e lavorazione proposta sotto.

## Via-in-pad: proposta reversibile, non dimensionamento approvato

| Parametro | Valore di studio |
|---|---:|
| Paddle U101 | 1,80 × 3,48 mm |
| Vie aggiunte | 6 (2 colonne × 3 righe) |
| Posizioni X | 67,64 e 68,36 mm |
| Posizioni Y | 32,50, 33,65 e 34,80 mm |
| Diametro rame / foro | 0,55 / 0,25 mm |
| Rete | GND_RF (net 1) |
| Margine rame più piccolo entro il paddle | 0.265 mm |
| Passo minimo tra centri | 0.720 mm |
| Frazione geometrica dei sei fori sul rame paddle (solo indicativa) | 4.7% |

**AVVERTENZA DI FABBRICAZIONE:** in presenza di via-in-pad NON tapparle con una supposizione sullo stencil. Il produttore e l'assemblatore devono approvare diametro/fattibilità, eventuale riempimento e cappatura (VIPPO), piano di massa, aperture F.Paste/F.Mask, vuoti sotto componente e profilo di reflow. Le via non sono garantite supportate dal processo standard. Il pad conserva un'unica apertura di pasta del progetto precedente, ora da **ripensare**. In questa revisione non sono stati calcolati θJA/θJC, il ΔT reale né l'impedenza RF delle transizioni.

### Come ripristinare il PCB senza vie aggiunte

Usare il file originale in `04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB`. Il candidato è byte-identico al PCB V4.5 dopo aver tolto esattamente le sei definizioni `(via ...)` riconoscibili dalle coordinate; questo viene controllato automaticamente.

## KiCad e connettore TE

- `kicad-cli` ancora **assente**: il tentativo di `apt-get update` non ha raggiunto i repository. **ERC/DRC nativi, refill zone e parità non eseguiti.** Consultare la procedura `03_Verifiche/V4.6/RUN_KICAD_RX_V46.sh` e adattare solo la copia candidata V4.8.
- La pagina ufficiale TE elenca i CAD `ENG_CVM_CVM_CONSMA002-SMD-G_D.2d_dxf.zip` e `ENG_CVM_CVM_CONSMA002-SMD-G_D.3d_stp.zip`. I link sono documentati, ma il servizio ha restituito a questa sessione un contenuto ZIP non acquisibile. **Non è stato importato né verificato un DXF/STEP originale.** Il footprint SMA resta un'ipotesi di studio e non va modificato sulla base di quote non allineate.
- Gli SMA estendono il courtyard oltre i bordi del PCB e richiedono validazione meccanica/3D.

## Gate prima di ordinare un prototipo

1. Acquisire CAD TE DXF/STEP; allineare datumi/pad/mask/paste/courtyard e ingombri.
2. Caricare il candidato V4.8 in KiCad 10, verificare formato/librerie, fare ERC/DRC nativi con `--schematic-parity` e `--refill-zones` su COPIA; analizzare ogni errore e warning.
3. Ottenere da fabbricante stack-up controllato RF, limiti diametro via, annular ring e processi di riempimento/cappatura delle vie.
4. Progettare stencil U101, area di pasta e vuoti termici con assemblatore. Verificare termica su scheda reale.
5. Effettuare test S11/S21/VNA e poi assemblare con distinta componenti certificata; nessuna trasmissione RF in questo modulo.

**Conclusione:** abbiamo un'alternativa termica specifica da valutare, non una soluzione collaudata. Avanzamento complessivo conservato al 37% stimato, zero hardware testato.

### Fonti
- Analog Devices, *ADL5535 Rev. A*, Figure 17, p. 11, https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- TE, `CONSMA002-SMD-G`, https://www.te.com/en/product-CONSMA002-SMD-G.html
- KiCad 10, CLI docs, https://docs.kicad.org/10.0/en/cli/cli.html
