# SY01 - PLL filtro d'anello, V0.4

**Stato: candidato da simulazione LINEARE, NON progettazione completa o CAD verificato.**

## Schema nodale (ADF4351)

- Pin 7 CPOUT -> C1 6,8 nF -> GND_RF
- Pin 7 CPOUT -> R2 1,2 kohm -> C2 120 nF -> GND_RF
- Pin 7 CPOUT -> R3 270 ohm -> pin 20 VTUNE
- VTUNE -> C3 4,7 nF -> GND_RF

Icp programmata 2,5 mA e RSET 5,1 kohm. fPFD = 640 kHz; PLL N da 3631 a 3900 e Kv VCO assunto tipico 40 MHz/V da datasheet.

## Modello, convenzione e risultati

Y(s) = s*C1 + 1/(R2 + 1/(s*C2)) + 1/(R3 + 1/(s*C3))
Z_vtune(s) = [1/Y(s)] / (1+s*R3*C3)
L(s) = [Icp * Kv_Hz_per_V / N] * Z_vtune(s) / s

Frequenza di attraversamento 4489.0 Hz; margine di fase 54.73 gradi per N=3750, Kv 40MHz/V.
**Il modello presume un blocco PFD/CP ideale e una curva VCO linearizzata.** Non modella ritardi digitali, loop calibration, non linearita, charge pump leakage/dead zone, reference PNoise, switching regulator, layout e rumore VCO misurato.

## Sensibilita calcolata, 4000 estrazioni uniformi (non worst case esaustivo)

- N intero uniforme fra 3631 e 3900; Kv fra 25 e 55 MHz/V (IPOTESI di progetto, non dati statistici dal produttore).
- R2/R3 ±1%, C1/C3 ±5%, C2 ±20%, Icp ±5% per scenario di calcolo.
- f crossover minimo/massimo 2831/6211 Hz.
- Margine fase minimo/massimo 49.1/58.5 gradi.
- Percentili 1%-99% margine fase 50.5-58.1 gradi.
- Campioni con PM >=45 gradi: 4000 / 4000. **Non prova margine minimo di produzione.**

## Filtro e rumore

Sono forniti grafici di trasferimento piccoli segnali. NON vengono prodotti valori assoluti dBc/Hz, rumore reciproco, spurie a 640kHz, EVM o settling time misurato. Serve modello del TCXO reale, Kv sul campione, parametri PLL (ADIsimPLL), modelli di componenti e misura con analizzatore di spettro/rumore di fase.

## Fonti

- ADF4351 Rev A https://www.analog.com/media/en/technical-documentation/data-sheets/adf4351.pdf
- ADF4351 evaluation UG-435 https://www.analog.com/media/en/technical-documentation/user-guides/ug-435.pdf
- How to Design and Debug PLL https://www.analog.com/en/resources/analog-dialogue/articles/design-debug-a-pll-circuit.html
