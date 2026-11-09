# Registro delle verifiche V0.5

| ID | Verifica | Stato | Risultato / limite |
|---|---|---|---|
| V5-01 | 270 setpoint LMX2572, Integer-N | PASS software | N=3631-3900, errore numerico 0 Hz, ref 12.8 MHz/R10, /128 |
| V5-02 | Range VCO 3.2-6.4 GHz | PASS da datasheet e calcolo | VCO effettivo 4.64768-4.992 GHz |
| V5-03 | fPFD 1.28 MHz nel range Integer | PASS da datasheet | min 0.25 MHz; controlli ulteriori su firmware richiesti |
| V5-04 | Formula normalizzata del floor del PLL | PASS calcolo ripetibile | ADF -126.58, LMX -141.59 dBc/Hz a LO37.5MHz, solo termine IN-BAND; 15.01 dB |
| V5-05 | Esempio mixing reciproco | PASS aritmetico | Ipotesi -40dBm/mixer, NF5dB, filtro 2.4kHz, NO ricevitore fisico |
| V5-06 | Complessivo noise phase (reference + VCO) | NON VERIFICATO | TCXO, spettri VCO, modelli loop e layout mancanti |
| V5-07 | Parametri loop LMX2572, layout e SPI | NON PROGETTATI | Componenti V0.4 NON riciclabili |
| V5-08 | Misure RF e produzione PCBWay | NON ESEGUITE | Non esistono Gerber/BOM di produzione/PCB |

Eseguire `python3 03_Verifiche/Studio_PLL_V0.5_riproduci.py` e `python3 03_Verifiche/run_all_tests.py` dalla radice progetto.
