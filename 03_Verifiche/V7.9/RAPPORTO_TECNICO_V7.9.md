# SUPERSTAR 3900 SMD EVOLUTION — RAPPORTO TECNICO V7.9

**10 novembre 2026 · modello RTL indipendente, confronto WDI TI e filtro LC parametrico, NO FAB / NO TX.**
Evoluzione incrementale di V7.8 su `main`. Storico e baseline `v7.0` preservati; DAC900, clock FPGA, mixer IF2/RF, PA, antenna e ogni componente TX rimangono **DNP, senza alimentazione né collegamento fisico**.

## 1. Correzione di un limite di fattibilità del watchdog V7.8

Nel blocco V7.8 heartbeat commutava una volta ogni 8 tick del clock da 30,72MHz: **3,84 milioni di transizioni/s**, periodicità completa a 1,92MHz. Un riferimento indipendente **32.768Hz** campionante non potrebbe riconoscere in modo affidabile quelle transizioni; l'accelerazione dei due clock nel bench V7.8 occultava l'aliasing.

Nuovo RTL `08_Firmware_Prototipi/V7.9/rtl/slow_heartbeat_v79.v`:
- Il parametro default `MASTER_TICKS_PER_TOGGLE=307200` riduce il heartbeat a **100 cambi di livello/s** e **50 fronti di discesa/s**, ossia **20,000ms fra fronti WDI**. Dal clock nominale 30,72MHz sono dunque 307200 tick per cambio livello e 614400 per ciclo intero.
- Il secondo riferimento eventuale **Abracon ASFLK-32.768KHZ-LJT** 32.768kHz/3.3V/CMOS/±20ppm (5032 4-SMD, fonte ufficiale https://abracon.com/parametric/oscillators/ASFLK-32.768KHZ-LJT ) osserverebbe ~327,68 tick per cambio nel modello ideale. Non ci sono tuttavia pin di oscillatore verificati, rail o campionamento reale.
- `v79_virtual_watchdog_top` mantiene `tx_rf_permission=0`, `dac_pd_released=0`, `analog_path_connected=0` anche quando il watchdog virtuale diagnostica uno stato sano. Nessuna modifica a un FPGA reale o WDI fisico.

I testbench sono accelerati (parametri ridotti), non riproducono il tempo di salita o la frequenza fisica del dispositivo.

## 2. Watchdog TI standalone — dati di produttore e margini nominali

**TI TPS3430WDRCR**, VSON 10 pin DRC 3×3mm, ACTIVE, https://www.ti.com/product/TPS3430/part-details/TPS3430WDRCR ; datasheet **SBVS366A** https://www.ti.com/lit/ds/symlink/tps3430.pdf , **pagine 3 e 6 controllate visivamente**.

Pin vendor DRC top-view verificati: **1 VDD1, 2 CWD, 3 SET0, 4 CRST, 5 GND, 6 SET1, 7 WDI, 8 WDO, 9 NC, 10 VDD2**, pad di massa termico. VDD1 e VDD2 richiedono connessione elettrica reciproca in una futura scheda; **nella V7.9 sono entrambi OPEN/DNP**, nessun chip montato.

Configurazione puramente numerica candidata `CWD=NC, SET0=LOW, SET1=HIGH, CRST=NC`. Dal timing datasheet per alimentazione/temperatura specificate:
- **tWDL max 2,22ms**, **tWDU min 23,375ms**.
- WDI fronte di discesa previsto **20,000ms**, margine rispetto limite superiore **3,375ms**, rispetto limite inferiore **17,78ms**; per master ±10ppm il controllo software mantiene margini >3,374ms e >17,779ms.
- CRST aperto: ritardo reset circa **170–230ms**, non bloccante permanentemente: richiede in futuro un **latch esterno** e una nuova valutazione del comportamento al riavvio. WDO è **open-drain active-LOW**, mentre il DAC900 ha PD active-HIGH con pulldown interno; **vietato accoppiarli direttamente**. La perdita di alimentazione del TPS3430 non garantisce un livello inibente su PD o RF.
- Il TPS3430 ha un timebase proprio per il suo WDI: il secondo riferimento Abracon è candidato a un MONITOR esterno separato e non è parte obbligatoria della configurazione TPS3430.

**Solo modello**, senza alimentatori, watchdog montato, CWD/SET reali, supervisor PD, isolatore normalmente aperto o test di guasto single-point. I 12 casi di guasto software includono arresto di entrambi i clock, WDO stuck-high/low, disabilitazione SET, backfeed, PD stuck-low, relay saldato: tutti hanno qualifica hardware **NON ESEGUITA**.

## 3. Filtro ricostruzione F7401: screening componenti con SRF senza qualifica RF

Rimane l'architettura V7.3 50Ω↔50Ω **7-pole LPF matematico**, taglio 850kHz su IF2=455kHz. Il DAC900 ha invece IOUT/IOUTB **in corrente**, quindi l'interfaccia I/V non è fisicamente progettata e la risposta di una ladder 50Ω non qualifica il collegamento al DAC.

Candidati Coilcraft **DNP** individuati su pagine vendor:
- `MSS1260T-472MLD` per gli induttori esterni L1/L7, **4,7µH ±20%** (anziché ~4,1665µH), **SRF 38MHz TIPICA**; pagina https://www.coilcraft.com/en-us/products/power/shielded-inductors/ferrite-drum/mss-mos/mss1260t/ .
- `MS590PNB183MSZ` per gli induttori interni L3/L5, **18µH ±20%** (anziché ~16,8698µH), **SRF 11,2MHz MINIMA**; pagina https://cps.coilcraft.com/en-us/products/power/shielded-inductors/ferrite-drum-sleeve-high-l/pnb/ms590pnb/ms590pnb183/ .

La valutazione `03_Verifiche/V7.9/analizza_filtro_srf_v79.py` integra nominalmente la reattanza dei due inductor con una capacità di autoparassita dedotta da SRF, nel solo equivalente ABCD: **QL=60 e QC=500 ipotetici**, nessun vendor Q @455k, nessuna curva di impedenza o modello SPICE reale, né tolerance/temperature/bias/PCB. Le SRF riportate come **tipica e minima non sono comparabili come limiti garantiti**; gli induttori sono famiglie per elettronica di potenza e non sono componenti RF già qualificati.

Numeri riproducibili del modello:
- filtro V7.3 ideale originale: perdita massima in banda IF2 **0,00075 dB**;
- induttori candidati ma senza SRF e senza Q: perdita **0,00069 dB**;
- componenti candidati con Q e SRF **ipotetici**: perdita massima in banda desiderata **0,23537 dB**, attenuazione relativa minima ai due toni immagine del DAC **88,7018 dB** nel modello.

**Questi non sono dati garantiti su un dispositivo né una emission mask**, e le incertezze su Q/ESR/PCB/I-V e variazioni L ±20% impediscono qualsiasi approvazione. Capacità e reti di adattamento DNP/TBD.

## 4. Esiti realmente verificati nel repository completo

| Verifica | Esito | Valore probatorio |
|---|---|---|
| Nuovo RTL Icarus V7.9 slow heartbeat / ref monitor | **PASS** | Diagnostico soltanto, simulazione accelerata |
| Yosys `synth; check -assert` generico nuovo TOP V7.9 | **PASS** (302 celle nel log) | Non `synth_ice40`, PNR, STA o bitstream |
| Regressioni Icarus V7.8 / V7.7 / V7.6 | **3 PASS** | Nessuna attivazione RF/PD |
| Nuovi test Python V7.9 | **17 PASS, 0 FAIL, 0 SKIP** | Rapporti 307200/20ms, WDI vendor, SRF, DNP, 270 canali |
| V7.8 / V7.7 / V7.6 | **20 + 14 + 15 PASS** | Regressioni modelli |
| V7.5 / V7.4 / V7.3 | **22 + 21 + 15 PASS** | Regressioni DSP/DAC digitali |
| V7.2 / V7.1 | **11 + 8 PASS** | Regres. RX/IF2 |
| **Totale Python** | **143 PASS / 0 FAIL / 0 SKIP** | [GitHub Actions run 42847265093](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42847265093), job **129938002468**, log esaminato |
| Stato hardware, emissioni e PCB | **NON ESEGUITI** | Nessuna misura di potenza, RF o sicurezza fisica |

Machine-readable `03_Verifiche/V7.9/RISULTATI_VERIFICHE_V7.9.json`. Se successivi commit modificano codice o test, rifare CI prima del merge. Il report indica test software realmente verificati sul branch, non test di produzione.

## 5. Distinte, continuità e blocchi aperti

- BOM `07_Componenti/BOM_WATCHDOG_FILTRO_V7.9.csv`: **11 voci ALL DNP/OPEN**; netlist `01_Specifiche/V7.9/NETLIST_WATCHDOG_CANDIDATA_DNP_V7.9.csv`: **15 terminali ALL DNP/OPEN**, con solo TPS3430 pin verified vendor.
- Lattice `iCE40UP5K-SG48I` pinout ufficiale XLSX `document_id=51971` **non disponibile per verifica dei bytes**; `FPGA_PINS_PROPOSTI_V7.6.pcf` **HOLD**, nessuna autorizzazione PCB o PNR.
- **NON ESEGUITI**: clock reale, TPS3430, 32k reference e power/PD, WDI electrical timing, watchdog latch indipendente, interruttore RF fail-open, analisi guasto singolo, fixed-point runtime, SRF/Q misurate del filtro, DAC I/V, KiCad/ERC/DRC, EMC, prove in trasmissione, fabbricazione.

**Decisione V7.9:** integrabile in main come sola revisione **software/numerica** previa CI finale. Non fabbricare né collegare alcun TX. **NO FAB / NO TX.**

**Prossima V7.10:** pinout ufficiale SG48 autenticato, reali MPN/pin per alimentazioni e interlock PD/RF indipendente con fault di rail=0, modello filtro con componenti specifici e vendor Q/SRF affidabili, esperienza sulla sintesi FPGA e timing, verifiche full CI. 
