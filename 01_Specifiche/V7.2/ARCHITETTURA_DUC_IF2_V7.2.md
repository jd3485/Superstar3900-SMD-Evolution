# V7.2 — sorgente IF2 / DUC MULTITONO, solo modello matematico e contratti DNP

**10 novembre 2026 · overlay sulla V7.1 · NO FAB / NO TX.** Nessun segnale inviabile a dispositivi reali. `U7201/U7202`, `R7201..R7205` V7.1 rimangono DNP, U7202 RF3 non è instradato. Qui `U7301` (DAC) e `F7301` (filtro di ricostruzione) sono solo opzioni **senza MPN, senza pinout**; anche `J7301/J7302` e `R7301..R7303` sono DNP. Non esiste connessione fisica dai campioni generati a U7201.

## Architettura software candidata
- **Ingresso** array di audio reali in `[-1,+1]` a **48.000 campioni/s**, blocchi di 384–1024 campioni. Solo vettori in memoria, nessun driver, nessuna interfaccia HAL/SAI/DMA.
- **DUC** interpolazione **80×** a **3.840.000 campioni/s**, finestra Blackman–sinc con **32 campioni audio per fase**, normalizzata a guadagno DC unitario; campioni periodici per rendere confrontabili frequenze coerenti. Nyquist = 1.920.000Hz; IF2 455.000Hz, banda audio massima nominale 2700Hz.
- **USB/LSB**: filtro Hilbert circolare Blackman **257 tap**, su finestre **periodiche** (`x+jH(x)`). RF USB, dopo conversione LO1 alto, si ottiene da `conj(x+jH(x))`, cioè IF2 inferiore; RF LSB dalla controparte IF2 superiore. La quadratura è una forma d'onda teorica, non un modulatore IQ fisico.
- **AM**: `(1+μ·audio)·cos(2π 455000 t)`, `0≤μ<1`, ingresso normalizzato; portante e due bande laterali. Non include compressore, splatter, DAC saturation e pre-equalizzazione.
- **FM**: `cos(2π 455000 t − 2π·Δf·integrale(audio dt))`; integrazione numerica trapezoidale a 3.84Msps, `0≤Δf≤5000Hz`; segno invertito perché LO1 alto inverte la deviazione finale. Non include CTCSS/DCS, preenfasi, limitatore e mask emission.
- **CW**: IF2 454.300Hz quando key-down, tono risultante RF +700Hz; sin² con ingresso/uscita **2ms** nello studio; key-up = array interamente 0. Non prova banda occupata o forma finale del keyer.
- **Sicurezza:** `tx_permission(...)=False` incondizionatamente; nessun backend DAC, GPIO, SPI, antenna o PA. Il modello non può diventare trasmittente cambiando un flag.

## Vincoli strutturali
Il clock audio 48kHz ×80 = 3.84MHz è una frequenza digitale **candidata**; nessun clock tree STM32G474, timer, DAC, clock jitter o clock recovery verificato. La ricostruzione analogica a 455kHz richiede DAC reale a 3.84Msps (e limiti di latenza, jitter, SFDR, linearità, impedenza, rumore), filtro F7301, isolamento e percorso RF che restano **tutti assenti**. Un buffer da 384 campioni contiene 30.720 campioni IF2 (64KiB se Q16, 120KiB se float32): costo RAM/throughput non qualificato. Solo la convoluzione interpolante naïve 32×3.84M richiede **122.88 MMAC/s**, senza contare Hilbert e NCO: **non** considerare compatibile con STM32 senza ottimizzazione/prove.

Il filtro Hilbert *circolare non causale* è adatto soltanto a blocchi periodici di test: input voce reale a confini non periodici produrrebbe discontinuità e artefatti. Occorrono filtri causali a stato, corretto allineamento ritardi I/Q, gestione blocchi, limitazione ampiezza, verifica fixed-point e profilo DMA prima di firmware reale. Test a due toni non equivalgono a voce/occupazione di banda su transitori.

## Piano analogico: filtri solo ideali, non selezionati
- **F7301** ricostruzione analogica 455kHz: passband, reiezione immagini di campionamento, numero di poli, termination, MPN e footprint non selezionati. Il modello software **non** prova eliminazione immagini DAC né spettri analogici.
- **F7201** IF1 10.695MHz V7.1: proxy Butterworth BPF ideale ordine 2, punti a -3dB 10.685–10.705MHz, rejezione teorica 9.785MHz **79.15dB**. Non è un filtro reale né dimostra Q/matching/phase linearity.
- **F7202** RF V7.1: proxy Butterworth BPF ideale ordine 5, punti -3dB 25–29MHz. Sul piano V6.4 (270 canali), perdita teorica in banda **0–0.082dB**, reiezione relativa immagine alta min **89.66dB**, reiezione relativa feedthrough LO1 min **61.05dB**: numeri **solo ideali**, non attribuibili a componenti fisici. Nessun MPN, layout, campagna S-parameter, modellazione Q/SRF o risultati EMC.
- Rischio di sovrastima: filtro 5 sezioni ideale privo di perdite e parassiti è un riferimento di **fattibilità algebrica**; prima di adottarlo servono componenti con Q, SRF, tolleranze, accoppiamento, potenze, rischio feedthrough e misure.

## DNP e interfacce
Vedi `07_Componenti/BOM_DUC_IF2_V7.2.csv` e `NETLIST_DUC_IF2_V7.2.csv`. Le 12 assegnazioni sono terminali di **connettori/ponti virtuali**, non pin reali verificati del DAC o del filtro (pin fisici di U7301/F7301 **TBD**, quindi non fittiziamente numerati). `J7302` è solo un'interfaccia di misura non cablata. I tre resistori aperti R7301/2/3 mantengono interrotti i punti logici DSP→DAC→filtro→mixer IF2 V7.1. Nessuna alimentazione, interblocco o emissione RF aggiunta.

## Mancanze aperte per V7.3
Selezione DAC e clock fisici e schede dati primarie, filtri analogici con netlist pin verificate, transitori/FFT broadband con maschere, filtro anti-alias in ingresso, bilancio segnali, ottimizzazione DSP realtime, test STM32, F7201/F7202 implementabili e interoperabilità delle revisioni RX. **ERC/DRC KiCad, SPICE/EM, misure e fabbricazione NON ESEGUITI.**
