# LO buffer 36,310-39,000 MHz - studio V0.4

**Decisione:** nuovo candidato U3 = ADL5611 (SOT-89, SMD), alimentazione 5V, banda dichiarata 30MHz-6GHz. Non ancora BOM approvata.

### Correzione candidato precedente
PHA-1+ ha banda nominale da **50 MHz** in su: non e' idoneo come candidato garantito per un LO a 36-39MHz. ADL5611 copre formalmente la gamma, ma a 30MHz il **P1dB tipico e' solo +16dBm**, diverso dal valore +21dBm indicato a 900MHz.

### Connessioni di principio

ADF4351 /64 (36,31-39 MHz) -> filtro LPF prima catena (calcolato V0.3) -> pad PI 50 ohm IN selezionabile -> ADL5611 (AC-coupled) -> pad PI OUT selezionabile -> opzionale filtro post-buffer -> mixer ADE-1+ SMT level-7 (+7dBm). Un secondo filtro prima del mixer evita di presumere che l'amplificatore sia privo di distorsione. **I filtri non sono ancora progettati come dispositivi reali.**

- ADL5611: pin 1 RFIN, pin 2 GND + paddle, pin 3 RFOUT/Bias. Rete bias per 30-500MHz, da datasheet: induttore 1uH (0603HP), C ingresso e uscita 100nF, bypass su 5V 68pF, 1.2nF, 1uF. Dettagli di inserzione, SRF/ESR, pin/pad e placement da verificare.
- Consumo nominale 94mA a 5V => 0.47W elettrici (limite superiore approssimato di dissipazione in assenza di RF utile); calcolo termico PCB aperto.
- Mixer ADE-1+: 0,5-500MHz RF/LO, level 7; potenza e isolamento da verificare sui campioni.

### Bilancio NOMINALE ILLUSTRATIVO non misurato

| Grandezza | dB/dBm |
|---|---:|
| PLL uscita teorica | +5,0 dBm |
| Perdite complessive ipotizzate LPF (prima/dopo) | -1,5 dB |
| Attenuatore prima ADL5611 | -16,0 dB |
| Guadagno tipico **a 30MHz** (non dato garantito a 38MHz) | +21,8 dB |
| Attenuatore dopo ADL5611 | -2,0 dB |
| **LO mixer calcolato** | **+7.3 dBm** |
| Output ADL5611 calcolato | +9.3 dBm |
| Headroom su P1dB tipico 30MHz | 6.7 dB |

Deve essere possibile regolare con alternative PAD-IN 12/14/16/18dB e PAD-OUT 0/2/3/6/9dB, scegliendo popolazione componenti SMD e misurando +7 dBm nel mixer sul banco. Gli attenuatori sono **passivi resistivi 50ohm**, non commutati dal firmware; file CSV contiene valori IDEALI, da arrotondare a serie E96 e poi simulare S-params.

### Criticita 

1. P1dB tipico non equivale a specifica minima garantita. Misurare Pout su gamma e temperatura.
2. ADF4351 RFOUT e le perdite filtri non sono misurate: no stima di potenza garantita.
3. LO spurie e attenuazione a 2,4GHz non possono essere dedotte dal modello LC concentrato V0.3; richiedono layout e VNA/spectrum analyzer.
4. Il beneficio in rumore del buffer sul mixer e' tutto da provare; un amplificatore puo' introdurre rumore, armoniche o disadattamento.

### Fonti ufficiali
- https://www.analog.com/media/en/technical-documentation/data-sheets/ADL5611.pdf (Rev B, pp.3/13)
- https://www.analog.com/media/en/technical-documentation/data-sheets/adf4351.pdf
- https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B
- https://www.minicircuits.com/pdfs/PHA-1%2B.pdf (banda da 50MHz)
