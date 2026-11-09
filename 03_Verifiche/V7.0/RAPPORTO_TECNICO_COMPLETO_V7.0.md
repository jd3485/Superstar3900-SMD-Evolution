# Superstar 3900 SMD Evolution — rapporto tecnico V7.0

**9 novembre 2026 · revisione cumulativa, RX only · NO FAB, NO TX**

## Obiettivo e risultati

Progettati come **overlay e circuiti candidati** la demodulazione AM e FM a 455kHz, un driver LO2 10.24MHz +7dBm nominali con rete reale LC, e filtri audio FIR Q15 per SSB/CW. Conservato lo storico V6.9 senza alterarne i sorgenti. **Non** si dichiara completo né validato il ricevitore fisico.

### Componenti e dati verificati su fonti primarie

- **U7101 Analog Devices AD8307ARZ, SOIC8**, pin INM1 COM2 OFS3 OUT4 INT5 ENB6 VPS7 INP8, tensione 2.7–5.5V, uscita nominale 25mV/dB. Si usa **l'intero comportamento logaritmico**, non un modello di inviluppo lineare. ENB è active-high, da default R7102=100k a massa. Datasheet AD8307 Rev.F: https://www.analog.com/media/en/technical-documentation/data-sheets/ad8307.pdf
- **U7102 TI TLV3201AIDBVR, SOT23-5**, OUT1 GND2 IN+3 IN−4 VCC5; 40ns tipico, 2.7–5.5V, compare la FI2 con riferimento 1.65V. https://www.ti.com/product/TLV3201
- **U7103 TI CD74HC4046APWR**, TSSOP16, VCC16 GND8, SIGIN14 COMPIN3 VCOOUT4, PC1OUT2, VCOIN9 DEMOUT10, R1=11, C1A6/C1B7, INH5. 3.3V nominali. R7106=10k/C7108=100p solo valori da tarare; **non** sostengono che il VCO sia esattamente a 455 kHz. R7109 pull-up INH=OFF. https://www.ti.com/product/CD74HC4046A
- **U7104 TI TLV9062IDR** due buffer/gain analogici, 3.3V. La Vref=1.65V esterna non è ancora generata con un riferimento a basso rumore sul modulo; R e C sono candidati e i livelli verso ADC_R richiedono misura.
- **U7121 Mini-Circuits GALI-3+**: RF_IN1 GND2/4 RF_OUT+DC3, 50Ω da DC a3GHz, 35mA nominali, 3.3V nominale ai pin del MMIC, alimentato via **R7122 47Ω da 5V** e choke da qualificare. Il guadagno 22.4dB è tipico **a 100MHz**: nessun dato garantisce quel valore a10.24MHz. https://www.minicircuits.com/pdfs/GALI-3%2B.pdf

**Elaborati**: `01_Specifiche/V7.0/CIRCUITO_COMPONENTI_IF2_DEMOD_LO2_V7.0.json` e netlist CSV per pin fisici, `07_Componenti/BOM_IF2_DEMOD_LO2_V7.0.csv`, `01_Specifiche/V7.0/SCHEMA_A_COMPONENTI_IF2_DEMOD_LO2_V7.0.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.0.md`, diagramma di integrazione, netlist picircuo LPF.

## Simulazioni e test eseguiti — dati riproducibili, limiti dichiarati

| Controllo | Esito |
|---|---:|
| Nuovi test unitari statici/numerici | **75/75** |
| Suite selezionate V5.9–V7.0 | **13/13** |
| Test nelle 13 suite | **616 / 616** |
| 270 canali × cinque modi in piano storico | **1.350** senza variazioni |
| Stati fail closed audio e TX enumerati (6 × 2^6) | **384** |
| Rete LO2 LPF a componenti, f=10.24MHz Q80 50Ω | **-0.31 dB S21** |
| Attenuazione armonica 3×30.72MHz | **-32.66 dB** |
| Attenuazione armonica 5×51.2MHz | **-54.67 dB** |
| Return loss input LPF a 10.24MHz nel modello | **14.74 dB** |
| LPF induttori ±5%, condensatori ±2%, Q45..120 | **4.000 Monte Carlo** |
| AM AD8307 log 1kHz, m=35%: THD modello raw | **9.082%** |
| AM correzione digitale invertendo log: THD modello | **0.013%** |
| FM PLL XOR linearizzato, deviazione ±2kHz, tono 1kHz | **20.09mV picco** |
| GALI-3+ bias 5V R47, simulazione incertezze | **5.000 campioni**, corrente 25.0–40.2mA |
| Potenza LO nominale *solo se gain22.4dB a 10MHz* | **6.71dBm**, NON verificata |
| Compilazione sintattica header Q15 con GCC | **riuscita** |

Tutte le simulazioni sono modelli matematici di circuiti ideali/equivalenti SciPy/NumPy, incluso il PLL FM linearizzato. **Non sono** analisi LTspice/ngspice con modelli non lineari AD8307/HC4046/GALI-3 né misure di un prototipo. Il file `.cir` contiene solo il passa-basso passivo LO2, non un circuito misto completo validato. Un fallimento delle prestazioni fisiche, del VCO o dell'aggancio è ancora possibile e non costituisce un test superato.

### Filtri SSB/CW

Sono stati generati coefficienti FIR reali e Q15 con `scipy.signal.firwin`, compilabili in C e simulati a48kHz: SSB 241tap, banda **300–2700Hz**, ritardo gruppo **2.5ms**, **11.57 MMAC/s**; CW 481tap, centro **700Hz**, banda approssimata **500Hz**, ritardo **5ms**, **23.09 MMAC/s**. Risposta numerica dopo quantizzazione: SSB a1kHz **-0.000dB**, a5.5kHz **-108.3dB**; CW a700Hz **-0.003dB** e a1.8kHz **-76.6dB**. Le esigenze computazionali di 48k * 481 MAC non sono ancora provate sullo STM32 e SAI; sono da integrare nel firmware RX effettivo. **F823/F824 hardware 455kHz rimangono DNP**, perché nessun MPN in produzione con matching e disponibilità è stato convalidato. Il DSP post-demod **non** previene blocco RF/FI da interferenti adiacenti forti.

## Criticità ad alta priorità e gate

1. Programma hardware di consenso RX (J7102 AM ENB, Q7102 FM INH) non concluso: i circuiti restano **disabilitati** finché i consensi reali non saranno definiti. Q7101 non utilizzato (DNP). Vref 1.65V e matching F821/F822 ancora aperti; R7104 (terminazione FM) **DNP** fino a valutazione con filtri montati.
2. Per FM mancano misura del centro VCO a455k, taratura R1/C1, loop stabilità, capture range, rapporto segnale/rumore reale, THD, e sicurezza per interferenti; il calcolo lineare non prova queste condizioni.
3. Per AM bisogna verificare ingresso log su ampiezza reale, distorsione e calibrazione su temperatura, envelope recovery e percorso codec.
4. Il driver LO2 nominale da +7dBm richiede **misura RF obbligatoria**: i dati di guadagno MMIC tipici sono a100MHz, non a10.24MHz; il choke L7121 e gli induttori LPF devono avere Q e SRF garantiti e misurati. V6.3 va aggiornato con ~35mA sul5V e carichi analogici aggiuntivi3.3V; validazione elettrica termica in corso.
5. I precedenti problemi **immagine RX V6.7**, termica PLL V6.4, LMX registri V6.4, filtri SSB/CW 455k e integrità del front-end non sono risolti.
6. Manca **KiCad schematico nativo validato, ERC, PCB e DRC;** nessun hardware RF costruito. **NO FAB / NO TX**. Nessuna autorizzazione regolamentare o hardware a trasmettere.

## Prossima revisione V7.1

Continuare lo sviluppo globale con **TX modulatore e percorso IF/upconversion inibito in hardware**, senza collegare finale RF, e interfacce alla MCU/audio; in parallelo tenere le ECO e i gate IF2 visibili per successivi collaudi, non interrompere il progetto globale con revisioni interminabili di test. Dopo aver progettato tutti i moduli della radio è prevista la revisione sistematica integrale con KiCad e strumenti fisici.
