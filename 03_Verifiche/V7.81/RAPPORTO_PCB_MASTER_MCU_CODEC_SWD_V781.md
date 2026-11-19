# V7.81 — PCB master reale: estensione 25→74 footprint, MCU/CODEC/SWD

**Lavoro CAD sostanziale (WIP, non produzione).** Il generatore `03_Verifiche/V7.81/build_master_mcu_codec_placement_v781.py` estende lo stesso progetto PCB master partendo dai **25 footprint già versionati nel PCB V7.80**, tutti con coordinate e **pad→net** conservati, e colloca i **49 componenti fisici del foglio MCU/CODEC** dalla netlist nativa del master KiCad V7.79: STM32G474RE U6201, TLV320AIC3204 U6202 (EP33), 4 LDO U6203–U6206, supervisore U6207, oscillatore X6201, ferrite FB6201, debug J6201, 31 condensatori C6201–C6231 e 8 resistori R6201–R6208. Non vengono aggiunti componenti non presenti nel CAD nativo.

**File PCB unico WIP:** `04_KiCad/PCB_MASTER_V7.81_MCU_CODEC_SWD_PLACEMENT_WIP/S3900E_MASTER_V781_STAGING_NO_FAB.kicad_pcb`. L'output pcbnew KiCad9 **va materializzato e committato** con la CI come prova, non soltanto generato sul runner. Posizioni per gruppi funzionali, con passo provvisorio grande per ridurre sovrapposizioni; la posizione non prova bontà dei loop, EMC, ritorni o compatibilità chassis. Regolatori 3,3V e loro condensatori sono sul lato MCU, ma nessuna via, pista, zona o ponte tra `GND`, `GND_MAIN`, `EFUSE_RTN` viene introdotto. SWD J6201 pin1 è soltanto **VTREF sense** e pin 2–5 rimangono SWDIO, SWCLK, NRST, GND MCU; nessuna connessione a programmatori autorizzata.

## Accettazione verificabile

- KiCad9 carica i footprint *effettivi* vendor/standard da `fp-lib-table`, confronta tutti i pin elettrici collegati con i pad reali, e conserva la netlist nativa (141 componenti/103 reti).
- La PCB già committata V7.80 è letta con pcbnew prima dell'estensione; tutti i suoi 25 riferimenti, coordinate, numeri di pad e **identità della rete** devono risultare invariati.
- Verificare che `J6201` corrisponda fisicamente a `U6201` pin 49,50,7,16,15 e `U6202 EP33` NON sia erroneamente cortocircuitato con `U200 EP17`. MCU GND locale non collegata artificialmente a PLL/AUX GND_MAIN.
- DRC diagnostico KiCad9 **NON RELEASE**, con tutte le segnalazioni effettive conservate; NON dichiarare DRC PASS. Manca `Edge.Cuts` perché outline, forature, stackup, distanze termiche e RF sono HOLD; zero piste e zone finché ritorni/sorgenti non qualificati.
- **49 nuovi footprint, 74 totali**, non rappresentano un avanzamento percentuale né una PCB completata. Residuo schematico: **67 componenti** ancora senza posizione, compresi RX/PLL e altri blocchi, D200 DNP esclusa intenzionalmente. L'intero schema mantiene 25 errori ERC e 180 warning come ultima evidenza V7.79.

**Blocchi permanenti:** sorgente 13,8V/fusibile F200/eFuse reset, TVS D200 DNP, assorbimenti 5V/3,3V e termica/DFM, 15 interfacce cross-module OPEN/HOLD, SG48/Y1 pin10 HOLD, compatibilità meccanica, filtraggio/impedenza RF, dispositivi RX/TX. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

**Prossimi gate:** ispezionare DRC nativo, correggere soltanto overlap reali senza waiver, posizionare progressivamente i 67 restanti con componenti qualificati, poi stabilire outline/fori reali e layout/routing/DRC prima di ogni valutazione produttiva.

## Risultato CI finale sul generatore (19 novembre 2026)

[Run nativo KiCad9 44506575017](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/44506575017) SUCCESS sul codice generatore: vero PCB 74 componenti, 25 invariati dal V7.80, 49 nuovi. Fallimento iniziale separato da 4 aperture paste-only non numerate su U6202 EP33, corretto controllando che **non** contengano F.Cu; non bypassate la verifica pad33 rame. DRC iniziale **41 violazioni = 1 invalid_outline +40 text_height** e 169 pad non instradati; corretti fisicamente 40 reference text height a ≥0,8mm. **DRC finale NON RELEASE: 1 invalid_outline +169 unconnected pads**, nessun altro finding; nessun routing. La CI sul file PCB generato **versionato nel branch** deve essere ancora verificata prima del merge, perché la prova CI iniziale materializzava il file sul runner.
