# Superstar 3900 SMD Evolution — rapporto tecnico V6.9

**9 novembre 2026 · Sviluppo del secondo LO, BFO e demodulazione RX. STUDIO, NO FAB / NO TX.**

## Progetto e collegamenti nuovi

- Generatore candidato **Skyworks SI5351C-B-GM 20-QFN** (U971), pinout fisico verificato su tabella datasheet 20-QFN, 3.3V candidato. Pin CLKIN6 riceve **12.8MHz condivisi** con il sintetizzatore V6.4 tramite B972 fanout **NON selezionato**. U971 SCL4/SDA5 condividono PB6/PB7 dalla mappa MCU V6.1; il bus I²C e i pull-up esistenti vanno ricalcolati. I due pin aggiuntivi proposti PC12/PB11 sono **ECO ancora da accettare**; la mappa storica rimane immutata.
- Entrambi PLL interni di studio scelti a 800MHz, con 800MHz / 12.8MHz = **62.5**; CLK0 target LO2 10.2385/10.2400/10.2415MHz secondo modo; CLK1 target BFO 453.5/455.7/456.5kHz con R divider **16**. Il prototipo numerico rappresenta tutti i rapporti mediante frazioni con denominatore ≤1,048,575; **nessun bitstream registri Si5351C è stato generato o provato**.
- R971 10kΩ tiene **OEB alto = output DISABILITATI** a riposo; Q971 2N7002 può portarlo basso soltanto se il futuro circuito `LO2_EN_HARDWARE_GRANTED` fornisce RX safe. Il circuito reale indipendente che produce questo consenso **NON è ancora progettato**: questa è una condizione aperta, non una garanzia HW.
- U971 CLK0 non pilota direttamente U802 mixer LO: `B971` **LO2 driver a +7dBm da scegliere**, filtro spur, matching, carico, alimentazione e isolamento da qualificare; lo stato `LO2_RF_7DBM_PENDING` non va considerato una sorgente disponibile.
- U981 **TS5A3157DBVR** SPDT SOT-23-6 con pin fisici confermati: 1 NO IF2 invertito, 2 GND, 3 NC IF2 normale, 4 COM audio commutato, 5 V+, 6 IN BFO. `B981` deve produrre due IF2 simmetriche polarizzate a **1.65V**, fra **0 e 3.3V**; buffer/impedenze/fase da selezionare. LPF candidati R981/982=6.8kΩ e C982/983=4.7nF, AC coupling C984. Le effettive risposte dei due RC caricati richiedono prova circuitale.
- AM: D991 Schottky generica, R991 10kΩ/C991 4.7nF più C992 blocco DC. **Nessuna parte Schottky/footprint/impedenza di ingresso ancora qualificata**. FM: B991 limiter e B992 discriminatore in quadratura **non selezionati**; solo filtro audio candidato R993/C993. Filtri stretti F823 SSB/F824 CW della V6.8 ancora da scegliere; ciò non costituisce un ricevitore completo.
- 46 istanze/ref BOM, **129 assegnazioni pin-rete** nel nuovo foglio candidato. Schema in `01_Specifiche/V6.9/`; include blocchi e collegamenti esplicitamente NON collegabili senza qualifiche. La TX **non è collegata** e resta vietata.

## Simulazioni e prove riproducibili realmente eseguite

- Piano: **1.350 combinazioni** (270 canali × AM/FM/USB/LSB/CW) ricalcolate e confrontate **riga per riga** col piano V6.8. Frequenze LO2 e BFO rappresentate senza **errore aritmetico razionale** nel modello. Questo NON certifica phase noise, jitter, spur, frequenza dopo quantizzazione registri o efficacia del riferimento su silicio.
- Modello di rivelazione nel dominio del tempo: campionamento **3.64 MS/s**, 40ms per tono, quadratura ideale e commutazione a onda quadra ideale. FFT: USB **1kHz**, LSB **1kHz**, CW **700Hz**, AM **1kHz**, FM **1kHz**. AM = diodo ideale senza soglia; FM = ritardo esatto di due campioni = quadratura ideale; SSB = inversione matematica senza sbilanciamento.
- LPF LO2: **solo modello Butterworth del quinto ordine** con taglio 14.2MHz, attenuazione terza armonica 30.72MHz **-33.52 dB**. In **4.000 scenari esplorativi** con frequenza di taglio ±7%, la perdita matematica alla terza armonica spazia da **-36.66 a -30.58 dB**. **Non esiste ancora una rete a componenti che garantisca questi valori**, né l'ampiezza +7dBm.
- Quadratura FM: **5.000 scostamenti esplorativi ±5% del quarto di periodo ideale**; guadagno relativo del discriminatore di modello tra **0.99692 e 1.00000**. Non costituiscono toleranze fisiche di un risonatore reale.
- Riferimento condiviso ±2.5 ppm: lo scarto residuo di primo ordine a RF 25.615–28.305MHz rimane **64.04–70.76Hz**. Condividere il clock **non elimina** l'errore assoluto di sintonia.
- **70/70 nuovi test V6.9**, **4096/4096 stati logici** di fail-closed enumerati (solo uno con permesso audio e nessuno con TX), **12/12 suite selezionate V5.9–V6.9**, **541/541 test**. Le 12 suite non comprendono tutte le prove storiche dei primi anni di progetto.

## Limitazioni e blocchi

**NO FAB / NO TX.** Non effettuati: ERC/DRC KiCad, PCB native, ngspice con modelli dei componenti scelti, misura reference CLKIN, programmazione Si5351C, phase noise/spurs, calibrazione BFO, allineamento di fase di B981, LO2 +7dBm, demod FM reale, demod AM su piccoli segnali, matching filtri 455k, selezione F823/F824, termica/supply del nuovo sintetizzatore, EMI, protezione antenna e integrazione finale. Sono aperti anche i problemi del frontend V6.7 (reiezione immagine conservativa 17.5dB) e del regolatore PLL V6.4.

**Prossimo modulo suggerito V7.0:** circuito demod AM/FM analogico reale con selezione dei componenti mancanti, filtri IF2 SSB/CW e piano d'integrazione audio. In parallelo non perdere il progetto globale: TX/PA RF, ATU, firmware completo, meccanica e interconnessioni ancora da costruire; a fine serie le verifiche sistematiche KiCad/strumentali.

### Fonti tecniche consultate
- https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/Si5351-B.pdf (Si5351C 20-QFN)
- https://www.ti.com/product/TS5A3157 (SPDT SOT-23 pinout)
- https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN619.pdf (programmazione della sintesi)
