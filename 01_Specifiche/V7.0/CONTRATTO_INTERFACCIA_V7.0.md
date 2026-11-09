# Contratto di integrazione V7.0

| Porta/sorgente | Destinazione | Stato |
|--|--|--|
| IF2_AM_OUT da F822 V6.8 (2k storico) | J7101.1, R7101, U7101 INP8 | CONDIZIONATO: matching/taratura ancora aperti |
| IF2_FM_OUT da F821 V6.8 (1.5k storico) | J7101.2, R7104/C7106, U7102 IN+3 | CONDIZIONATO: non duplicare terminazione del filtro |
| AM_DETECT_EN active high | U7101 ENB6 | DEFAULT OFF; J7102 open, richiede hardware RX CONSENT |
| FM_PLL_INH active high | U7103 INH5 | DEFAULT OFF; consent Q7102 HW RX SAFE da validare |
| LO2_DRIVER_INPUT | U971 CLK0 V6.9 via R974 | AMP GALI-3+ 5V, montare solo dopo RF tests |
| LO2_RF_AC_TO_MIXER | U802 ADE-1+ LO6 | NOMINALE +7dBm; livello, spur e filtro ancora da misurare |
| DEMOD_AM_AUDIO_AC / DEMOD_FM_AUDIO_AC | J605 V6.0 rispettivamente AM/FM | il route BB deve essere selezionato, non collegare in parallelo D991/B992 |
| USB/LSB/CW AUDIO | U981 V6.9 -> Codec ADC_R V6.0 | FIR Q15 dopo demod in firmware; filtri F823/F824 DNP |
| 3V3_A_IF_FILTERED / 5V_A_RF | alimentazione V6.3 | 3V3 ~12mA analog AM/FM (stima), 5V ~35mA GALI-3 (nominale) | 
| RF TX | NON COLLEGATO | TX sempre bloccata, approvazione fab assente |

Resta da fare un progetto nativo KiCad con conversione netlist/footprint, analisi dei ritorni analogici, gestione clock, control fail-safe hardware completo e misure.
