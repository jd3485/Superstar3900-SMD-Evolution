# Superstar 3900 SMD Evolution — Rapporto tecnico CAD V7.16

**10 novembre 2026 · causalità footprint SMA J9102/J9104 misurata con KiCad 9 su copie effimere. NO FAB / NO TX.**

## 1. Revisione verificata sul ramo V7.16

Base: V7.15 integrata su `main`. Sono stati aggiunti il protocollo vendor `01_Specifiche/V7.16/PROTOCOLLO_SMA_ORIENTAMENTO_KICAD_V7_16.md`, gli script di diagnostica `03_Verifiche/V7.16/probe_sma_native_v716.py` e i test di conservazione del posizionamento `test_sma_orientation_v716.py`, con workflow KiCad9 nativo `.github/workflows/v716_sma_native.yml`. Nessun file schematico, PCB, footprint storico, firmware, Gerber o modello RF viene riscritto.

Il confronto differenziale nativo già verificato in [GitHub Actions run 42920407518](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42920407518) usa **quattro cloni temporanei** direttamente fratelli del progetto sorgente. È importante la collocazione: le tabelle `fp-lib-table` usano percorsi relativi; annidare i cloni introduce falsi `lib_footprint_issues` e invalida la diagnosi. Ogni clone viene caricato con `pcbnew.LoadBoard`, riempito con `pcbnew.ZONE_FILLER`, salvato *solo nella cartella temporanea*, quindi controllato con `kicad-cli pcb drc`. Lo SHA256 del PCB V7.14 sorgente è confrontato prima/dopo: **immutato**.

## 2. Risultati nativi (dopo il vero refill in ogni clone)

| Esperimento | DRC violations | Unconnected | Residuo `lib_footprint_mismatch` |
|---|---:|---:|---:|
| Scheda originale, conservando rotazioni e riempiendo zone | 2 | 0 | J9102 e J9104 (2) |
| Soli angoli testi Reference/Value impostati a 180° | 2 | 0 | J9102 e J9104 (2) |
| Rotazione locale dei quattro pad GND custom a 180° | 2 | 0 | J9102 e J9104 (2) |
| Rotazione impronte J9102/J9104 modificata 180° → 0° | 0 | 0 | Nessuno |

**Interpretazione limitata:** la variabile *orientamento dell'impronta* modifica in modo causale l'esito del confronto libreria KiCad. Non è prova che l'unico problema sia un bug di KiCad, né che l'orientamento a 0° sia fisicamente corretto. DRC=0 in un clone non sostituisce qualifiche vendor o RF.

## 3. Perché NON correggere la rotazione a 0° nel progetto

Il PCB RX ha bordo rettangolare da x=20 mm a x=130 mm. Le impronte SMA J9101/J9103 si trovano a x=28 mm, orientate 0°, e **sporgono sul lato sinistro**. J9102/J9104 sono a x=122 mm e **ruotate di 180° per sporgere sul lato destro**. Il candidato di libreria include un courtyard locale con asse X da -15,20 a +4,10 mm. Le coordinate proiettate sono:

| Connettore | Orientamento funzionale attuale | Estensione globale courtyard X |
|---|---|---|
| J9101/J9103 | 0° | da 12,8 a 32,1 mm |
| J9102/J9104 | 180° | da 117,9 a 137,2 mm |
| J9102/J9104 *solo prova DRC* | 0° | da 106,8 a 126,1 mm |

La sporgenza nominale del courtyard è **7,2 mm esternamente** sul lato corretto con l'orientamento attuale, mentre la prova a 0° riporta il connettore del lato destro verso l'interno del PCB e modifica l'ingombro e la direzione di accoppiamento. Pertanto **rotare a 0° per azzerare i warning è una falsa soluzione di progetto**. Le quote sono dei disegni CAD candidati, non validazioni meccaniche.

## 4. Produttore TE e qualificazione footprint

Fonte primaria: [TE Connectivity — CONSMA002-SMD](https://www.te.com/en/product-CONSMA002-SMD.html), jack SMA RF 50Ω a 90°, montaggio SMD. Disegno approvato per uso progettuale elencato `C-CONSMA002-SMD-X-X Rev D`, pagina 2 raccomanda centro Ø2,05 mm e quota trasversale 7,76 mm. Lo stesso sito offre CAD `2d_dxf.zip`, `3d_igs.zip`, `3d_stp.zip`. **In questa revisione tali archivi non sono stati importati, confrontati o approvati**, né sono stati verificati F.Paste/F.Mask, tolleranze, contatto, zona termica, DFM e ritorno RF.

La semplice corrispondenza geometrica locale dei cinque pad di J9101...J9104 alla libreria storica non basta a validare l'impronta ruotata. Qualificare la vera geometria del footprint KiCad e il meccanismo del `lib_footprint_mismatch` senza ignorare la segnalazione; preservare 180° sul lato di uscita fino ad una soluzione CAD reale.

## 5. Stato e gate

- RX coupon ERC V7.15: 0 errori /0 warning, non cambiato.
- Root 7 fogli ERC V7.15: **43 errori /340 warning**, ancora aperto; 15 interfacce OPEN/HOLD, SG48 HOLD.
- DRC RX V7.15 con refill su copia effimera: 2 mismatch, 0 unrouted, non un PCB fabbricabile.
- V7.16: sole prove causali native e regressioni software, nessun nuovo FPGA Icarus/Yosys, HW, RF, VNA, EMC o collaudo produzione.
- Nessun percorso PA/antenna/DAC/FPGA TX attivato o integrato.

**Decisione tecnica:** integrare il progresso diagnostico V7.16, ma **NON** alterare i footprint SMA/rotazioni o generare Gerber finché il confronto vendor 2D/3D e i DRC su una scheda revisionata corretta non sono risolti. Prossima V7.17: qualifica CAD/transform da dati ufficiali, verifica GUI+CLI, poi valutazione zone-filled PCB versionato e ERC gerarchico. **NO FAB / NO TX.**
