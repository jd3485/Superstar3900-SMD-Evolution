# Schema funzionale primo mixer RF e FI1 V6.5

**Candidato in progettazione, NO FAB / NO TX. Non è schematico KiCad con ERC.**

## Catena di ricezione

`Antenna RX → protezioni / attenuatore / LNA storico V5.8 → J501 RX 50Ω → F501 preselettore 25–29MHz (MODELLO IDEALE, RETE NON DIMENSIONATA) → U501 ADE-1+ pin RF3 → pin IF2 → C504 accoppiamento TBD → SW501/SW502 bank filtri IF → ramo AM/FM largo o USB/LSB/CW stretto → U503 amp IF TBD → J503 uscita IF 10,695MHz → demodulatori futuri → audio V6.0`.

Separatamente: `LMX2572 V6.4 J402 LO 36,310–39,000MHz → J502 → filtro spur FL502 TBD → buffer/attenuatore U502 TBD → U501 pin LO6 (+7dBm target 50Ω)`. Il sintetizzatore V6.4 non ha ancora rete d'uscita e livello RF dimostrato.

## Pin mixer ADE-1+ (confermati su datasheet produttore)

- U501 pin 1 GND_RF, pin 2 `IF_10M695_RAW`, pin 3 `RF_MIXER_IN_AC`, pin 4 GND_RF, pin 5 GND_RF, pin 6 `RX_LO_36_39_50R`.
- Case style CD636, port nominali 50Ω, LO +7 dBm nominale, perdita di conversione tipica del componente 5 dB. Non è un guadagno e non è una misura a 27 MHz / 10,695 MHz.
- Nessuna alimentazione elettrica richiesta **dal mixer passivo**, ma gli stadi LO / IF e LNA usano rail preesistenti e devono essere riprogettati nel bilancio di potenza V6.3/6.4.

## Filtro preselector: ipotesi numerica, non componenti fisici

BPF Butterworth di **ordine prototipo 3** e conseguente **ordine analogico 6**, f−3dB=25,000/29,000 MHz e Z0 nominale 50 Ω. Il trasferimento analitico passa tutte le 270 RX con perdita ideale minore di 0,39 dB e determina reiezione relativa immagine minima circa 53,46 dB. Il **valore di ordine non significa tre soli induttori**: la rete reale richiede sintesi LC, parassiti, Q finito, adattamento, perdite e S11/S21, e potrebbe richiedere ulteriori stadi o tracking varicap.

Il caso di esempio `blocker immagine 0 dBm` contro `spur richiesto < -110 dBm` imporrebbe 110 dB di attenuazione, NON raggiunti da questo modello: non si può dichiarare sufficiente la reiezione senza una specifica completa di sensibilità, blocker e dinamica mixer/LNA.

## Filtri FI per modalità, solo requisiti di progetto

- AM: BW nominale candidata 6 kHz; FM: 12 kHz (richiede controllo adiacenti e deviazione reale). USB e LSB: 2,7 kHz. CW: 0,5 kHz.
- A 10,695 MHz il Q caricato idealizzato `f0/BW` arriva a circa 21.390 per CW: **serve tecnologia adeguata** (quarzo/ceramica/DSP con architettura adatta), non è un banco LC convenzionale già fattibile.
- Non sono ancora stati selezionati i modelli filtro, il BFO/demod SSB/CW, gli impedenziamenti, il blocco AGC o il demod FM: **vengono sviluppati nelle prossime revisioni**.
- `J504` è un contratto di controllo, non un'assegnazione GPIO; serve allocazione pin STM32 e priorità PA/retune/PLL ready, per non rompere la V6.1.

## Condizioni di avvio e guasti

Il modello `rx_frontend_guard_v65.py` mantiene audio e ricezione muted in caso di PA, retune, PLL non pronto, interblocco alimentazione assente, filtro non selezionato o fault. Ricezione riabilitata solo con tutte le condizioni valide. **TX sempre FALSE**.

## Decisioni bloccanti per schemi/PCB

1. Ricavare rete BPF fisica 50Ω, componente RF, Q/carico, layout e budget blocker; simulare S21/S11, Monte Carlo su valori L/C e perdite e testare strumentalmente.
2. Misurare LO +7 dBm alla porta ADE-1+ con carico reale e spur/isolamento, progettare stadio driver e filtro; aggiornare correnti V6.3.
3. Selezionare realmente filtri FI 10,695 MHz e architettura di demod/doppia conversione con gestione AM/FM/SSB/CW e controllo interferenze adiacenti.
4. Progettare amplificatore FI e AGC con rumore/IP3/dinamica, verificare compatibilità front-end V5.8; senza questo non si può calcolare la sensibilità completa.
5. KiCad schemi ERC / PCB DRC non eseguiti; nessuna produzione, TX non collegata.

Fonti: https://www.minicircuits.com/pdfs/ADE-1%2B.pdf ; https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B ; https://www.ti.com/product/LMX2572 .
