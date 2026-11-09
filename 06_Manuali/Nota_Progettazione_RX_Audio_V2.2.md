# Nota progettazione V2.2

# Ricevitore RF - Prima rete preselettrice V2.2

**Stato: STUDIO ANALITICO / NON COSTRUIRE / non montare sulla PCB.**

Gamma RX **25,615-28,305 MHz**. Prima FI proposta 10,695 MHz, iniezione alta LO 36,310-39,000 MHz. Frequenze immagine **47,005-49,695 MHz**.

## Topologia studiata
Cin - 5 risonatori LC paralleli a massa, accoppiati da capacita' C12/C23 - Cout - passa-basso Chebyshev 7 poli (0,3 dB, fc 31,0 MHz) - uscita da 50 ohm.

Cin/Cout = 129.37 pF; C12/C45 = 30.41 pF; C23/C34 = 11.57 pF. Cinque induttori da 330 nH; Cedge = 55.69 pF, Cintermedio = 70.34 pF, Ccentrale = 83.89 pF. Valori **numerici ottimizzati** non normalizzati E-series, da NON assegnare ancora ai footprint.

## Risultati modello Q50
- Minimo S21 25,615-28,305: **-4.52 dB**.
- Peggior S21 sulle immagini: **-68.95 dB**.
- Monte Carlo 500 casi ±5% L, ±2% C, Q_RF uniforme 30-70 e Q_LPF uniforme 40-70: **399/500** rispettano S21 banda >= -6 dB e immagini <= -60 dB. NON e' rendimento produttivo reale.

**Punto critico:** circa 4,5 dB di perdita prima dell'LNA/mixer consuma quasi tutto il budget di rumore di 6 dB. NON si e' ancora trovato il miglior compromesso fra sensibilita', immunita' alle immagini e intermodulazione; testare filtro distribuito prima/dopo LNA, bypass e singoli filtri per sottobande.

## Componenti candidati
L'induttore Coilcraft 1008CS-331X_R_ 330 nH SMD ha valore specificato a 25 MHz e frequenza di autorisonanza minima dichiarata 570 MHz; Q minimo 45 e' **misurato a 100 MHz**, quindi NON puo' essere assegnato automaticamente a 27 MHz. Dati ufficiali: https://www.coilcraft.com/getmedia/9b59774c-05d4-40c5-99c9-417bb8e881ea/1008cs.pdf . Nessun componente viene marcato come confermato per assemblaggio.

## Verifiche mancanti prima del layout
1. Estrarre modelli S-parametro reali dei componenti e verificare Q a 27 MHz, SRF e tolleranze.
2. Simulare risposta S11/S21 con reti complesse, parasitismi e tecnologia PCB reale (fino a 6 bande).
3. Ripartire la selettivita' sui due lati dell'LNA per mantenere NF e grande dinamica.
4. Validare con VNA, analizzatore di spettro, generatore RF calibrato e misure d'NF.
5. Verificare spurie e TX-vs-RX switching. ERC/DRC nativi KiCad e simulazione SPICE non eseguiti.

## Riproducibilita'
`python 03_Verifiche/V2.2/rf_preselector_v22.py` aggiorna report JSON, CSV e immagini. Il netlist `.cir` e' un *modello di studio non ancora simulato in ngspice*.

---

# V2.2 - Piano di registri per due ADC simultanei, NON firmware validato

## Obiettivo
- Microfono collegato a U202/13 `IN1_L` -> ADC sinistro.
- Discriminatore FM collegato a U202/16 `IN2_R` -> ADC destro.
- 48 kHz, 2 canali a 32 bit, interfaccia I2S con BCLK = 3,072 MHz e WCLK = 48 kHz. Il codec e' master dei clock; SAI1 STM32 e' slave. MCLK esterno 12,288 MHz.

## Sottoinsieme dei registri (TI SLAA557 e SLAA404C)
L'ordine completo dell'accensione / clock / LDO / RESET resta da chiudere prima di provare i registri seguenti. Tutti i valori qui sono esempio di studio, non sequenza di bootstrap da caricare direttamente.

| Pagina | Registro (dec) | Valore | Funzione |
|---|---:|---:|---|
| 1 | 52 | `0x80` | IN1_L -> L MICPGA via 20 kohm |
| 1 | 54 | `0x80` | CM1L -> L MICPGA ingresso negativo 20 kohm |
| 1 | 55 | `0x20` | IN2_R -> R MICPGA via 20 kohm: D5:D4=`10` |
| 1 | 57 | `0x80` | CM1R -> R MICPGA negativo 20 kohm |
| 1 | 59 | `0x0C` | Sblocco PGA sinistro, compensazione nominale 6 dB |
| 1 | 60 | `0x0C` | Sblocco PGA destro, compensazione nominale 6 dB |
| 0 | 81 | `0xC0` | Alimentazione ADC sinistro e destro **solo dopo configurazione clock valida** |
| 0 | 82 | `0x00` | Unmute ADC sinistro e destro |

Verificare readback I2C e campionamento simultaneo con due sinusoidi di frequenza diversa (es. 1 kHz sul mic e 100 Hz sulla via FM). Confermare ritardi, guadagni e accoppiamento tra canali su prototipo.

**Rischi:** modalita' LDO e alimentazioni interne gia' aperte nelle V1.9/V2.1; disturbi da clock; aggancio dei segnali di subaudio CTCSS/DCS al discriminatore.
**Fonti:** https://www.ti.com/lit/pdf/slaa557 ; https://www.ti.com/lit/an/slaa404c/slaa404c.pdf
