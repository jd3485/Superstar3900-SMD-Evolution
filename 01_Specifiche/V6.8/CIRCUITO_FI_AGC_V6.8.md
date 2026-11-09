# V6.8 — FI1 10,695 MHz + AGC analogica + piano FI2 455 kHz

**Stato: candidato ingegneristico parziale, NO FAB / NO TX.** Non è uno schema KiCad ERC, non è un circuito RF testato, non è una radio completamente progettata.

## Topologia in sviluppo

U501 ADE-1+ FI pin 2 → J801/R801 49.9Ω (terminazione 50Ω) → C801 1nF → U801 AD8338 INPR pin1. INMR pin4 AC a massa tramite C802 1nF; entrambi gli ingressi mantengono bias interno ≈VREF 1.5V. L'AD8338 è un VGA **differenziale** con pin confermati: INPR1, INPD2 (NC), INMD3 (NC), INMR4, COMM5=GND, MODE6=GND, GAIN7 collegato DETO8 a C803 1µF verso massa; FBKM9 NC, OUTM10, OUTP11, FBKP12 NC; VAGC13; OFSN14 tramite C807 100nF a VREF16; VBAT15 =3V3_A_IF_SW, EPAD=GND_IF. VREF16 solo uscita interna + C804 100nF a massa. C805 100nF e C806 1µF sul rail.

**AGC hardware reale nel datasheet AD8338:** MODE a massa impone slope invertito, GAIN e DETO collegati con C_DETO esterno. SETPOINT: R802=100kΩ da VREF(1.5V interno) a VAGC13; R803=680kΩ VAGC13→massa; VAGC≈1.3077V; target *idealmente* |VAGC−VREF|≈0.1923 Vrms **differenziali**. R divider preleva ≈1.92µA dal VREF, non forzare VREF dall'esterno. Timing datasheet nominale T=17450Ω*(285pF+C_DETO), per 1µF 17.455ms; valore effettivo MLCC e dinamica di attacco/rilascio da misurare. Limite: la forma d'onda in ingresso può arrivare prima che AGC reagisca e saturare U801: nessuna protezione immediata ai blocker.

**Nodo d'uscita U801 OUTP/OUTM NON adatto direttamente a un carico 50Ω.** J802 porta *differenziale ad alta impedenza*. La successiva rete FI1 di roofing comprende **2 risonatori LC ad alta impedenza e buffer B811/B812 ancora NON selezionati** (L811/L812 1µH, C811/C813 180pF C0G, trimmer C812/C814 20–80pF, R811/R812 3.3kΩ ipotizzati). Il modello di risonatore assume Q0=80 e carico equivalente; NON è rete reale già adattata, isolata o garantita. Per 1µH alla FI nominale, Ctot≈221.44pF → trimmer≈41.44pF. I buffer, la trasformazione differenziale/single-ended e il controllo offset richiedono sviluppo.

U802 ADE-1+ è **SECONDO mixer candidato**: RF3 da buffer FI1, LO6 da J803 a ~10.240MHz (+7dBm da generare e verificare), IF2=455kHz pin2. Massa pin1/4/5. Il suo LO2 deve essere programmabile per centrare filtri SSB; **generatore LO2, driver, spur, IF2 matching non sono ancora completati**.

**Filtri a 455kHz:** F821 Murata SFPKA455KFA4-R1, FM 6dB half bandwidth minima 6kHz, Z≈1500Ω; F822 Murata SFPKA455KHA1-R1, AM half BW minima 3kHz, Z≈2000Ω; fonte catalogo 2011, disponibilità e footprints NON verificati. Due commutatori SW821/SW822 non selezionati fisicamente, con comando break-before-make da definire. Filtri F823 SSB nominale 2.4–2.7kHz e F824 CW 500Hz sono **segnaposti senza MPN**; non attribuire loro prestazioni commerciali. L'uso di un singolo filtro SSB centrato a 455k richiede conversione LO2 mode-dependent.

**Inversione laterale dovuta a LO alto V6.4:** RX USB RF (RF+Δ) → FI1 10.695MHz−Δ. RX LSB (RF−Δ) → FI1 10.695MHz+Δ. Assumendo banda parlato 0.3–2.7kHz, Δmid=1.5kHz, LO2_USB=10.2385MHz e BFO_USB=456.5kHz; LO2_LSB=10.2415MHz e BFO_LSB=453.5kHz. Così i contenuti IF2 di entrambe le sideband attraversano 455±1.2kHz, e l'audio recuperato è Δ. AM/FM: LO2=10.2400MHz; CW: LO2=10.2400MHz e BFO_CW=455.7kHz per tono 700Hz nominale. Questi LO2/BFO **sono frequenze di progetto, non uscite hardware già realizzate**. Tutti i 270 canali RF conservano LO1 V6.4 integer-N; la seconda conversione corregge la posizione SSB. Selezione dei demodulatori AM/FM/USB/LSB/CW e BFO hardware in revisioni successive.

**Limitazioni:** il più alto guadagno del VGA, la banda passante effettiva a 10.695MHz e la figura di rumore non sono state qualificate. La 3.3V analogica V6.3 richiede corrente aggiuntiva e gestione hardware RX-only. Le simulazioni nel pacchetto sono analitiche/numeriche, NON SPICE native e NON includono S-parameters reali, phase noise LO2, blocker, dispersione filtri 455, matching 50Ω↔1.5–2kΩ o CRC KiCad. Non collegare alcun percorso RX alla TX. Nessun MCU GPIO aggiuntivo viene assegnato arbitrariamente: controllo SW/LO2 via futura interfaccia che dovrà rispettare pinmap V6.1.

**Riferimenti primari:**
- AD8338 https://www.analog.com/en/products/ad8338.html e https://www.analog.com/media/en/technical-documentation/data-sheets/ad8338.pdf (pinout e AGC formula).
- ADI AN-1192 https://www.analog.com/en/resources/app-notes/an-1192.html
- Murata catalogo P05E (11/2011) https://www.murata.com/~/media/webrenewal/support/library/catalog/products/filter/cerafil/p05e.ashx (pag.5 / pag.7); conferma procurement necessaria.
- Mini-Circuits ADE-1+ https://www.minicircuits.com/pdfs/ADE-1%2B.pdf
