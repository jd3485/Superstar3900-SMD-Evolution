# Superstar 3900 SMD Evolution — V7.9 HEARTBEAT, WATCHDOG e SRF

**10 novembre 2026. Base V7.8 su main `c5f508f`. SOLTANTO MODELLI SOFTWARE / COMPONENTI DNP. NO FAB / NO TX.** Tutte le revisioni e la baseline RX restano conservate; nessun DAC, FPGA, oscillatore, IF2, mixer TX, PA o antenna è stato collegato.

## 1. Individuata e corretta una criticità di V7.8: sottocampionamento heartbeat

La V7.8 produceva `heartbeat_toggle` ogni **8 fronti master** a nominali 30.720.000Hz: frequenza delle transizioni **3,84 milioni/s**, 1,92MHz per un periodo completo. Un riferimento indipendente a **32.768Hz** non può campionare e riconoscere affidabilmente tale onda (Nyquist 16.384Hz): i test V7.8 con clock simulati non simulavano i rapporti di frequenza fisici. La V7.8 resta conservata come modello astratto, ma NON deve essere scelta per future implementazioni.

**Nuova cadenza V7.9**, applicata al solo modello:
- Master nominale **30.720.000 Hz** (X7601 V7.5 ancora DNP).
- `MASTER_TICKS_PER_TOGGLE = 307200`: un fronte di commutazione heartbeat ogni **10,000ms**, frequenza di transizioni 100/s.
- `WDI` riceverebbe in un futuro circuito il **fronte di discesa ogni 20,000ms**, o 50 fronti/s. Nessun WDI fisico viene guidato.
- Un riferimento indipendente **32.768Hz** osserverebbe matematicamente ~327,68 periodi propri per fronte di commutazione; non è un componente montato, e il suo clock 32k non è vincolato a quello master.
- A master ±10ppm l'intervallo di due fronti WDI di discesa resta circa **19,9998–20,0002ms**, senza assicurare startup corretto, jitter, clock-stop detect fisico o PVT reali.

File RTL `08_Firmware_Prototipi/V7.9/rtl/slow_heartbeat_v79.v`: contatore di riferimento con parametro di simulazione accelerabile, con TOP virtuale e `v78_independent_ref_monitor` ereditato. **Due clock sono solo INPUT ai modelli**, e tutte le uscite `tx_rf_permission, dac_pd_released, analog_path_connected` restano zero costante. Nessun HDL viene implementato sui GPIO FPGA SG48, la PCF è ancora HOLD.

## 2. TPS3430: WDI window effettivamente confrontata con i limiti TI

**Candidato manufacturer TI TPS3430WDRCR**, 10 terminali VSON DRC 3×3mm, **watchdog standalone a finestra**, distinta da U7901 TPS3840 di V7.8 (solo supervisor di tensione). Fonte primaria: https://www.ti.com/product/TPS3430/part-details/TPS3430WDRCR ; datasheet `SBVS366A` https://www.ti.com/lit/ds/symlink/tps3430.pdf , **p.3** configurazione/pin e **p.6** tempi, controllati anche tramite immagini del PDF.

**Pin fisici TI confermati per versione TPS3430 DRC top view:**
1 VDD1, 2 CWD, 3 SET0, 4 CRST, 5 GND, 6 SET1, 7 WDI, 8 WDO, 9 NC, 10 VDD2, oltre a pad termico a GND. `VDD1` e `VDD2` devono essere collegati esternamente per il funzionamento reale, ma nel nostro file `NETLIST_WATCHDOG_CANDIDATA_DNP_V7.9.csv` tutte le reti sono **OPEN/DNP/NON ALIMENTATE**. Pin9 NC deve rimanere non collegato, non un possibile segnale.

**Configurazione studiata matematicamente (NON fisicamente connessa):** CWD=NC, SET0=LOW, SET1=HIGH, CRST=NC. Dal datasheet Rev.A tabella 6.6:
- Finestra inferiore `tWDL`: massimo **2,22ms**.
- Finestra superiore `tWDU`: minimo **23,375ms**.
- WDI viene rilevato sul **fronte di discesa**. Intervallo nominale 20ms, margine minimo superiore **3,375ms** (prima di ulteriori margini di sistema) e margine inferiore **17,78ms**.
- Ritardo di reset CRST=NC: tRST circa **170–230ms**. Il TPS3430 **non mantiene WDO basso per sempre**: dopo tRST riprova, quindi un latch indipendente per fault persistenti e un'uscita di isolamento fisico sono ancora requisiti da progettare.
- **WDO è open-drain active-LOW**, con resistenza di pullup a sorgente valida richiesta. Il DAC900 `PD` è active-HIGH, con pulldown interno: **non collegare direttamente WDO a PD**; occorrono conversione di polarità, bias sicuro a rail=0, analisi stuck-at, reset e interruttore fisico fail-open.
- La configurazione `SET0/SET1` può disabilitare il watchdog; linee flottanti, rail assenti o errata impostazione sono rischi single-fault. Un TPS3430 alimentato dallo stesso rail che cade non garantisce nulla sulla protezione RF durante blackout. Il second reference e il latch devono essere indipendenti dai fault critici.

Per riferimento **X8001 Abracon ASFLK-32.768KHZ-LJT**, 32.768kHz CMOS 3,3V, ±20ppm, 5032 4-SMD, parte ACTIVE secondo il sito produttore https://abracon.com/parametric/oscillators/ASFLK-32.768KHZ-LJT. Il sito non è stato usato per assegnare i suoi quattro **NUMERI DI PIN**: `X8001` rimane solo BOM DNP, nessun vincolo fisico. Inoltre il TPS3430 è già uno watchdog indipendente che contiene un proprio riferimento: non si assume che il clock X8001 debba o possa pilotare il chip.

## 3. Induttanze candidate reali e SRF: confronto, non filtro approvato

F7401 della V7.3 è un LC Butterworth 7 poli con **due porte ideali 50Ω** e IF2 455kHz. Induttanze di progetto **L1=L7 ≈4,1665µH** e **L3=L5≈16,8698µH**. Sono state individuate due alternative di catalogo Coilcraft **SOLO per screening DNP**:
- `MSS1260T-472MLD` **4,7µH ±20%**, **SRF 38MHz tipica**, DCR circa 13,9mΩ tipica /15,5mΩ max, pagina https://www.coilcraft.com/en-us/products/power/shielded-inductors/ferrite-drum/mss-mos/mss1260t/ . L è già **+~12,8%** rispetto alla L nominale F7401.
- `MS590PNB183MSZ` **18µH ±20%**, **SRF 11,2MHz minima**, DCR 35,4mΩ tipica /39,4mΩ max, pagina https://cps.coilcraft.com/en-us/products/power/shielded-inductors/ferrite-drum-sleeve-high-l/pnb/ms590pnb/ms590pnb183/ . L è **+~6,7%** rispetto alla L nominale F7401.

**Questi sono induttori di potenza**, NON componenti qualificati per un filtro IF2 low-distortion 455kHz. I valori vendor pubblicati come **SRF tipica vs minima non sono intercambiabili**, e non c'è un dato Q vendor validato per questa topologia a 455kHz. Le capacità C2/C4/C6 non hanno ancora MPN/Q/ESR selezionati. Neppure l'interfaccia I/V e il carico differenziale del DAC900 sono risolti.

`03_Verifiche/V7.9/analizza_filtro_srf_v79.py` propone **solo** una ABCD 50Ω matematica: L vendute al posto delle L nominali, QL=60 e QC=500 **ASSUNTI**, C parassita dedotta dalla SRF vendor, assorbita in una topologia RL parallela C. Campi `vendor_q_at_455khz_known=False`, `vendor_srf_typ_vs_min_mixed=True`, `physical_dac_iv_interface_validated=False`. L'attenuazione numerica risultante NON dimostra 50Ω reali, adattamento I/V o maschera emissiva.

## 4. Distinte e blocchi

- BOM V7.9 `07_Componenti/BOM_WATCHDOG_FILTRO_V7.9.csv`: **11 componenti, tutti DNP/OPEN**.
- Netlist V7.9 `01_Specifiche/V7.9/NETLIST_WATCHDOG_CANDIDATA_DNP_V7.9.csv`: **15 terminali, tutti DNP/OPEN**. I soli pin numerici di un IC vendor definiti qui appartengono al TPS3430 (verificati su PDF ufficiale). FPGA e oscillatore ancora non cablati.
- Test Python V7.9, benchmark/verifica logica Verilog con Icarus/Yosys generico e regressioni storiche, da riportare nel rapporto tecnico dopo la CI.
- **SG48 pinout** originale Lattice XLSX documento 51971 **non accessibile**, la PCF e la tabella V7.6 restano **HOLD**; non approvare hardware FPGA, PCB, PNR/STA senza una verifica primaria.

**NON ESEGUITI**: implementazione hardware del watchdog, POR e PD a rail=0, fault singolo elettrico, CDC/MTBF, interfaccia DAC900, Q e SRF misurate, SPICE/EM, KiCad/ERC/DRC, PCB, EMC, banco, emissioni o trasmissione.

**Prossima V7.10:** pinout Lattice originale autenticato e review banking, progetto circuitale dei due domini di alimentazione/watchdog con isolamento normalmente aperto, filtri IF reali con Q/ESR misurati e componenti cap vendor, verifica DSP fixed-point/PVT, sempre con **NO FAB / NO TX**.
