# V6.3 — Alimentazione 13,8 V candidata (schema funzionale, NON KiCad)

**Il design V6.3 non è fabbricabile.** Non esiste ancora uno schema elettrico grafico nativo con pin fisici; le assegnazioni contenute nel CSV sono **nomi di funzione**, non numeri dei pad del package. Non usare questi CSV per produrre Gerber, pick-and-place o comprare componenti senza revisione.

## Catena di ingresso

`J901 → F901 (fusibile 5A T soltanto placeholder) → D901 TVS verso massa → L901 filtro di modo comune → U901 LM74900-Q1 / Q901 + R901 5mΩ + Q902 → 13V8_PROTECTED`.

LM74900-Q1 è stato scelto in quanto può pilotare **due MOSFET N esterni** per polarità inversa e disconnessione per sovracorrente, sottotensione o sovratensione. FET, BJT, circuito di misura corrente, timer, partitori UV/OV, TVS, fusibile e filtro EMI richiedono valori e codici approvati da scheda di applicazione. Il dispositivo 3–65V non autorizza a collegare direttamente un DC/DC 36V a picchi superiori: disconnessione e clamping vanno qualificati con oscilloscope.

**Power-on:** S901 è un interruttore SPST bistabile che collega EN del LM74900 a VS (=13V8_FILTERED) soltanto quando la radio è accesa; R902 pulldown 47k tiene EN basso con S901 aperto. TI documenta EN→VS per always-ON; questa è una proposta reversibile non ancora validata contro falsi contatti o transienti. J902 test in parallelo è **DNI**. Il finale RF J907 è DNI.

## Convertitori regolati

- U902 LM61460 13V8_PROTECTED→**5V_MAIN**, candidato 400kHz, L902 4.7µH, 4×22µF in uscita, 2×4.7µF + 2×100nF ingresso, RT 33.2k, feedback 100k/24.9k (Vout nominale 5.016V con Vref=1V, dati TI). Tolleranza MLCC e margine corrente da verificare.
- U903 LM61460 13V8_PROTECTED→**3V3_D**, candidato 1MHz, L903 2.2µH, 3×22µF, ingresso 2×4.7µF + 2×100nF, RT 13k e feedback 100k/43.2k secondo TI 3.3V/1MHz (Vout=3.315V ideale). **Non è stata eseguita simulazione di stabilità/EMI**.
- 3V3_UI filtrato da 3V3_D tramite FB901, destinato ai due MCP23017 della V6.1.
- 5V_RF, 5V_CODEC e 5V_MISC filtrati individualmente con beads (impedenze e frequenze da validare; l'impedenza ferrite 600Ω @100MHz non significa resistenza DC 600Ω).
- U904 TPS7A20-3.3 da 5V_MAIN→3V3_A, limitare il budget a 80mA (stimato 0.136W dissipati).
- U905 TPS7A20-1.8 da 3V3_D→1V8_CODEC, budget 100mA (0.15W). Entrambi con condensatori di uscita minimo 1µF.
- 13V8_AUD solo dopo Q903 high-side switch audio: requisito hardware futuro di gate, FAULT e turn-on. **13V8_AUDIO non è un convertitore regolato**.

## Interfacce revisioni precedenti

`13V8_PROTECTED` della V6.3 corrisponde all'etichetta precedente `+13V8_PROTECTED` nei fascicoli V6.2, `13V8_AUD` alla V6.0. Definire alias dei netlabel in KiCad attivo, non collegare doppie alimentazioni per errore. Il V6.2 TPS3700 riceve la tensione **protetta**, non quella grezza; se la protezione si disconnette, BAT_UV_OK deve disabilitarsi. 3V3_D e 3V3_UI devono avere massa DGND. **DGND, AGND e PGND rappresentano domini di ritorno nel contratto, non un invito a lasciare piani isolati**: connessione effettiva a stella/piani richiede futura analisi del layout e dell'EMI.

## Protezioni/limiti

Scenari analizzati solo numericamente: ingresso normale, inrush di 470µF e perdite, ripple ideale dei buck, Monte Carlo di carichi ed efficienze. Non sono stati simulati parassiti reali, load dump ISO, TVS, risposta dinamica compensatore, isolamento galvanico o certificazione EMC. Correnti audio/radio e rail devono essere confermati dal BOM completo. **Il circuito RX/TX e la produzione sono bloccati.**
