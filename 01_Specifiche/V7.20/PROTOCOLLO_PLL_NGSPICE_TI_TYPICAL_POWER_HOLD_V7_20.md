# V7.20 — protocollo di verifica PLL LMX2572 e domini di alimentazione

**11 novembre 2026 — verifica di modello analogico e dei blocchi POWER, non approvazione di schema/fab. NO FAB / NO TX.**

## Riferimenti Texas Instruments

- [LMX2572 datasheet SNAS740B, §8.1.3, tabella 135 p.64 ed equazione 4 p.65](https://www.ti.com/lit/ds/symlink/lmx2572.pdf): dati **tipici** di guadagno KVCO in MHz/V, interpolati in base a fVCO entro ciascun core. *VCO3*: 4200–4650 MHz, 47–64 MHz/V; *VCO4*: 4650–5200 MHz, 50–73 MHz/V. Questi valori NON sono limiti di fabbricazione né una caratterizzazione del chip reale. Al confine 4650 MHz cambia il core e la curva KVCO **non è continua**.
- [LMX2572 SNAS740B, §7.3.3 tabella 2 p.16](https://www.ti.com/lit/ds/symlink/lmx2572.pdf): corrente charge-pump **2500 µA per CPG 4 oppure 8**. La corrente modello 2,5 mA ha quindi una possibile impostazione prevista dal vendor, ma **nessuna configurazione di registri o readback hardware è stata verificata**.
- [LMX2572 SNAS740B, §8.1.11 figura 179 p.75](https://www.ti.com/lit/ds/symlink/lmx2572.pdf): topologia del filtro passivo a 3 poli, separazione CPOUT/VTUNE, C3 shunt di **almeno 1,5 nF** e posizionamento C3 fisico vicino VTUNE. I valori del Superstar NON sono approvati dalla figura.
- [TI PLLatinum Sim, strumento ufficiale](https://www.ti.com/tool/PLLATINUMSIM-SW): è lo strumento appropriato per spettro di rumore, spurie, tempo d'aggancio e verifica di filtro per un caso applicativo. **Non viene eseguito in V7.20**.

## Prove realmente eseguite

**A. Analisi AC indipendente del filtro:** `ngspice` esegue il file `04_KiCad/Bozze_pre_KiCad/Filtro_LMX2572_V0.6_ac.cir`; lo script `03_Verifiche/V7.20/verify_pll_spice_270_v720.py` ricalcola numericamente in modo indipendente la transimpedenza **Z(VTUNE / I_CPOUT)** con le ammettenze complesse di due nodi. Il gate confronta centinaia di punti AC e blocca un errore di modulo relativo superiore a 0,1%. Si verifica **soltanto il filtro passivo**, senza transistor VCO, stimoli digitali, controllo PLL interno, rumore o spurie.

**B. Confronto con studio V0.6:** il nominale usa C1=220pF, R2=620Ω, C2=120nF, R3=22Ω, C3=2,2nF, Icp=2,5mA, KVCO=55MHz/V, N=3750. La simulazione non viene chiamata «TI PLLatinum» e riproduce soltanto il precedente modello lineare ipotetico (~4,016 kHz crossover e ~59,76° margine).

**C. Tutti i 270 canali del piano frequenze:** si controllano uno per uno `PLL_N=3631..3900`, `fPFD=1,28MHz`, divisione intera, `fVCO = N×fPFD` (**solo aritmetica**). Si conducono:
1. **2430 scenari ipotetici** =270 N ×3 valori KVCO *assunti* (39/55/85 MHz/V) ×3 Icp *assunti* (2,3/2,5/2,7mA). Questi intervalli **non rappresentano le tolleranze TI**.
2. **270 risultati tipici di riferimento TI** per KVCO da tabella 135/equazione 4, una corrente nominale ipotetica CPG4/8=2,5mA. Nel piano corrente ricadono **2 casi VCO3 e 268 casi VCO4**. CSV di ogni canale e JSON dei casi estremi; **non approvazione di registri o di un vero core scelto**.

**D. Sei segnalazioni KiCad9 ERC `power_pin_not_driven`:** lo script `audit_native_power_v720.py` carica **veri report `kicad-cli sch erc` e netlist `kicad-cli sch export netlist`** del master V7.19, riporta per ognuno il pin, la net completa e i tipi KiCad di ciascun nodo sulla net. Tutti i 6 restano HOLD. Nessun PWR_FLAG o collegamento artificiale per eliminare un warning.

## Decisioni e divieti

**NO FAB / NO TX / NO GERBER / NO PCBWAY**. V7.20 non modifica lo schema V7.19 né alcun `.kicad_pcb`; lo stato completo resta **36 errori ERC / 340 warning / 15 interfacce OPEN/HOLD**. Conformità di un modello lineare a ngspice o a valori *tipici* TI **non prova** margine di fase reale, resa RF, misura spurie, parametrizzazione register map, risposta nel tempo o impedenza di ground. Le misure devono essere collegate alla configurazione TI e a campioni reali prima di liberare PCB. Restano inoltre aperti IF RX→MCU, potenza 13,8 V, protezione ritorni e TX interdetto.

**Prossimo gate proposto V7.21:** verifica dettagliata dello schema di alimentazione usando datasheet/nominali, source/return current budget e piano di connessione fisica delle sei reti non pilotate; a seguire simulazione del loop in PLLatinum Sim per le configurazioni hardware realmente approvate.
