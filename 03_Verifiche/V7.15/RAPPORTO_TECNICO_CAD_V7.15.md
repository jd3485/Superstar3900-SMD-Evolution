# Superstar 3900 SMD Evolution — Rapporto tecnico CAD V7.15

**10 novembre 2026 · vera prova nativa di riempimento zone KiCad su COPIA TEMPORANEA, senza produzione. NO FAB / NO TX.**

## 1. Ambito e tracciabilità

Baseline: V7.14 su `main`; PCB RX originale `04_KiCad/Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB/S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pcb`. La V7.15 aggiunge SOLO audit e script/test di diagnostica: nessun sorgente schematic/PCB/copper, via, footprint, libreria RF o firmware esistente è modificato.

Vera CI eseguita per la branch `feature/v7.15-sma-zone-diagnostics` al commit `bd465bea98613282af72b431d0e72d72999f48cc`: [run 42918178033](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42918178033) conclusione **success**, job `130185907657`; ulteriori controlli PR [run 42918302874](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42918302874) **success**. I file veri DRC/ ERC + JSON diagnostici sono negli artifact Actions `v715-sma-zone-native-read-only-NO-FAB-NO-TX`.

## 2. Prova causale della mancata connessione GND

Il file di origine contiene **15 footprint, 44 segmenti, 70 via GND_RF e quattro zone di GND_RF** (F.Cu, In1.Cu, In2.Cu, B.Cu). Non presenta `filled_polygon` salvati.

Il comando KiCad CLI installato nel runner **non** espone `--refill-zones`; la verifica via tale flag è stata correttamente marcata `UNSUPPORTED_NOT_RUN`, mai spacciata per PASS. Per ottenere un controllo reale è stato usato **`pcbnew.ZONE_FILLER`** su una copia temporanea dell'intero progetto KiCad, creata come directory sorella (per mantenere i path relativi delle librerie); sono stati salvati SOLO i dati di riempimento dentro la copia effimera, poi è stato eseguito `kicad-cli pcb drc` su quella stessa copia. Terminato il test, la directory temporanea viene rimossa automaticamente. I checksum SHA256 di origine prima e dopo risultano identici.

| Verifica KiCad nativa | V7.14 PCB come salvata | Copia temporanea V7.15 dopo refill |
|---|---:|---:|
| `via_dangling` | **70** | **0** |
| `unconnected_items` | **63** | **0** |
| `lib_footprint_mismatch` | **2** | **2** |
| Violazioni DRC (escluse unconnected) | **72** | **2** |
| `filled_polygon` memorizzati | **0** | **4** |

**Risultato importante:** tutti i 70 dangling via e tutti i 63 unconnected del DRC iniziale spariscono nella copia temporanea dopo un vero zone fill. Si dimostra che il riempimento mancante è un fattore determinante della diagnosi iniziale: non è giustificato aggiungere 63 piste arbitrarie o 70 via nuove per inseguire un conteggio precedente al riempimento. Tuttavia il test **non misura** impedenza, correnti, ritorno di massa RF, continuità fisica su un prototipo, stabilità rispetto a cambi board stack-up, thermal stitching, DFM, né autorizza PCBWay.

## 3. SMA J9102 e J9104: i due blocchi DRC ancora aperti

Il vendor ufficiale TE/Linx identifica **CONSMA002-SMD** (https://www.te.com/en/product-CONSMA002-SMD.html). Disegno **C-CONSMA002-SMD-X-X Rev D, p.2/3** anche all'URL https://docs.rs-online.com/a010/A700000010108374.pdf: pad centro **Ø2,05 mm**, quota trasversale nominale **7,76 mm**. La libreria di progetto usa Ø2,050 centro e forma/custom pad GND con estensione nominale calcolata di 7,760 mm in direzione y.

Il confronto testuale dei pad KiCad mostra che i quattro J9101…J9104 contengono le stesse cinque geometrie di pad della libreria storica, al netto di reti e UUID. Le due istanze con mismatch sono quelle ruotate **180°**, J9102 e J9104. **Questo non prova che la rotazione sia la causa**: il confronto strutturale non sostituisce il confronto DRC interno, import DXF/STEP ufficiale, layer F.Mask/F.Paste, courtyard, assieme o misura. **I due mismatch restano**; non va aggiornato il footprint a caso per ottenere un report verde.

## 4. ERC e regressioni

- RX ERC reale KiCad9: **0 errori, 0 warning** come V7.14.
- Gerarchia 7 fogli ERC reale KiCad9: **43 errori e 340 warning** ancora aperti, zero interconnessioni nuove RX/MCU/AUX.
- **12 test Python V7.15 + 201 regressioni V7.1–V7.14 =213 PASS, 0 FAIL, 0 SKIP** nella CI sopra citata. Include DSP/PLL/firmware, ma non nuovi Icarus/Yosys o collaudi reali.
- Nessuna net, modulo TX, PA, antenna, FPGA/DAC, alimentazione o firmware attivato dalla V7.15.

## 5. Decisione e prossimo sviluppo

**V7.15: risultato diagnostico REALE integrabile nel repository.** Non è un PCB modificato, non è un layout produttivo e non è una qualificazione del prodotto. Prima di risolvere J9102/J9104 servono l'interpretazione 2D/3D del manufacturer sul part number preciso e la ricontrollo GUI KiCad della trasformazione/footprint custom. Dopo: persistere una nuova copia di scheda con refill approvato e verificare DRC sull'artefatto versionato, stackup/return currents, progettazione completa 7 fogli e i 43 ERC root, 15 contratti OPEN/HOLD, SG48 HOLD.

**Nessun Gerber/ordine PCBWay, nessun hardware collaudato, nessun TX autorizzato. NO FAB / NO TX.**
