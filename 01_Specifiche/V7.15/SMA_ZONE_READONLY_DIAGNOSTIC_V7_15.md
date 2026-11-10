# Superstar3900 SMD Evolution — V7.15, SMA + GND zone audit (NO FAB / NO TX)

**10 novembre 2026 — branch diagnostica, non release di produzione.** Base: V7.14 su `main`, source RX originale preservato byte per byte. La V7.15 non costruisce una nuova radio, non collega RX/MCU/AUX e non attiva la TX.

## 1. Disegno manufacturer acquisito come riferimento (NON come qualifica CAD)

- Produttore: TE Connectivity / Linx, connettore jack SMA 50Ω **CONSMA002-SMD**.
- Pagina ufficiale: https://www.te.com/en/product-CONSMA002-SMD.html (documenti: disegno **C-CONSMA002-SMD-X-X, Rev D**, datasheet e file 2D/3D).
- Copia pubblica del disegno tecnico per il controllo: https://docs.rs-online.com/a010/A700000010108374.pdf, **pagina 2/3**.
- Tavola manufacturer: diametro pad centrale **Ø2,05 mm**, dimensione trasversale complessiva illustrata **7,76 mm**, altre quote 4,56 / 2,88 / 2,44 mm da verificare integralmente nel sistema di riferimento del disegno; **non** interpretare le singole quote come una certificazione del custom pad KiCad.

La libreria storica `S3900E_V38_Review.pretty/CONSMA002_SMD_SHAPED_REVIEW.kicad_mod` include centro circolare 2,050 mm e quattro pad GND sagomati; i centri dei pad GND sono a y=±3,130 mm, il poligono locale arriva a ±0,750 mm: **3,130 + 0,750 = 3,880 mm** per lato, ossia **7,760 mm** di estensione nominale in questa direzione. Questo è solo un controllo geometrico parziale, **non** la prova di coincidenza 2D/3D, maschera/pasta, giochi meccanici, impedenza o solderability. Il CAD originale DXF/STEP TE non è ancora importato/verificato; il part number effettivamente acquistabile e la distinta esatta vanno approvati.

## 2. Discrepanza J9102 / J9104 in KiCad

Il DRC nativo V7.14 ha segnalato `lib_footprint_mismatch` solo in **J9102/J9104**, le due istanze SMA montate a **180°**. L'analisi testuale strutturale di V7.15, che elimina da ciascun pad solo net e UUID e confronta geometrie KiCad, rileva che **tutti e quattro i footprint J9101…J9104 hanno lo stesso insieme di cinque pad locali della libreria storica**, inclusi i due ruotati. La correlazione con la rotazione **non dimostra la causa esatta dell'errore KiCad**: il DRC confronta anche elementi/trasformazioni non coperti dalla firma dei pad e la geometria custom richiede revisione CAD.

**Decisione:** NON aggiornare automaticamente i footprint da libreria; NON sopprimere i warning né forzare un DRC verde. Verificare geometria completa, rotazione, mirror, layer, disegno meccanico 2D/3D e dimensioni di montaggio usando KiCad GUI e un DXF/STEP ufficiale. La geometria attuale non è qualificata.

## 3. Inventario elettrico/copper realmente ricavato dal .kicad_pcb

- **15 footprint**, di cui 4 SMA e 1 connettore a due pad.
- **44 segmenti** di rame / piste.
- **70 via**, **tutte appartenenti alla net `GND_RF`**.
- **4 zone GND_RF** (F.Cu, In1.Cu, In2.Cu, B.Cu); **0 blocchi `filled_polygon` salvati** nel file di origine. Le zone *disegnate* non implicano automaticamente copper fill effettivamente valido nel PCB. Verificare zone refill in KiCad senza sovrascrivere il file V7.14.
- Il vero DRC V7.14 registra **70 via_dangling +2 lib_footprint_mismatch =72 violazioni**, e **63 unconnected_items** separati. **Non** si può dedurre dalle sole coordinate che una via abbia corretto ritorno RF o che una net sia sbrogliata.

La nuova CI `.github/workflows/v715_rx_sma_zone_native.yml` esegue sullo stesso PCB:
1. **DRC nativo as-is**, senza modifiche;
2. DRC con `--refill-zones` **solo se supportato dal KiCad installato**, esplicitamente *senza `--save-board`*;
3. confronto strutturato dei due report nativi, controllo SHA-256 byte-identico prima/dopo, verifiche ERC RX e root e regressioni Python complete V7.1–V7.14.
Se il KiCad della CI non supporta `--refill-zones`, il secondo test è registrato come **NON ESEGUITO** e non sostituito con una simulazione. Nessun Gerber o modifica di PCB viene prodotto.

## 4. Blocchi e piano tecnico successivo

La V7.15 di questo branch è una **milestone diagnostica read-only**, non una correzione di routing. Il DRC e il valore reale delle 63 connessioni dopo il possibile refill saranno registrati nell'artifact della CI quando eseguiti: non anticipare o inventare numeri. Il numero di via dangling dopo refill potrebbe cambiare o restare invariato; non equivale da solo alla verifica di ritorno RF.

Restano: confronto vendor 2D/3D e approvazione J9102/J9104; topologia GND con zone effettivamente riempite e controllo RF; routing reale delle net incompiute con vincoli; **43 errori ERC e 340 warning** nel root V7.14; **15 confini RX/MCU/AUX OPEN/HOLD**; pin FPGA SG48 HOLD; qualifica alimentazione/termica/stack-up/EMC/hardware. Tutti i sorgenti precedenti e le regressioni DSP/PLL/firmware vanno preservati.

**Gate finale:** `pcb_fabrication_permitted=false`, `tx_permitted=false`, `gerbers_created=false`. Niente alimentazione PA, DAC, FPGA o connessione antenna; nessuna dichiarazione di collaudo fisico. **NO FAB / NO TX**.
