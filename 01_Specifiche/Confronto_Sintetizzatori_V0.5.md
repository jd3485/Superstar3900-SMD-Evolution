# V0.5 - Sintetizzatori: confronto preliminare ADF4351 / LMX2572

**Stato:** LMX2572 candidato preferito, NON approvato per PCB. Non trascrivere il filtro PLL V0.4 sul LMX2572: le caratteristiche di carica/VCO e le reti di uscita sono differenti.

## Frequenze e canali (valori matematicamente verificati)

- F_RX da 25,615 a 28,305 MHz (270 posizioni), FI1 proposta 10,695 MHz; LO high-side 36,310-39,000 MHz.
- ADF4351: fTCXO 12,8 MHz; R=20; fPFD 640 kHz; VCO /64; VCO 2,32384-2,4960 GHz; N intero 3631-3900.
- LMX2572: fTCXO 12,8 MHz; R=10; fPFD 1,28 MHz; VCO /128; VCO 4,64768-4,9920 GHz; N intero 3631-3900; MASH disabilitato in Integer-N. PFD_DLY_SEL = 1 candidato dalla Tabella 3 TI (tutte le frequenze sopra 4 GHz); da confermare nel registro finale.
- fPFD 1,28 MHz soddisfa il minimo TI di 0,25 MHz per il funzionamento intero (datasheet LMX2572, Electrical Characteristics); N>=24 in tutte le posizioni (datasheet Table 3).
- `Tabella_LMX2572_270_Integer_N_V0.5.csv` contiene i 270 setpoint aritmetici, NON le word SPI complete.

## Confronto della componente bianca normalizzata in banda

Usiamo esclusivamente il termine flat del PLL, senza riferimento, rumore VCO, buffer, spurie o rumore da alimentazione:

`Lwhite_LO = FOM + 10*log10(fPFD) + 20*log10(fLO / fPFD)` in dBc/Hz.

Parametri tipici del produttore: ADF4351 FOM = -220 dBc/Hz (ABP=6ns); LMX2572 = -232 dBc/Hz (Integer). Alla frequenza di esempio 37,500 MHz, il modello restituisce -126,58 contro -141,59 dBc/Hz, differenza di **15,01 dB** per QUESTA componente, non nel rumore totale. La formula e' quella del contributo IN-BAND e non e' valida come stima della potenza spettrale a 10 kHz se la larghezza d'anello e' inferiore a 10 kHz.

Altri contributi: 1/f dell'PLL, VCO fuori banda, TCXO e reference spur, filtro loop, accoppiamenti digitali, RF_OUT e buffer. LMX2572 richiede un nuovo loop filter, diversa sequenza di inizializzazione e diversa analisi di calibrazione VCO. Il datasheet ADF4351 riporta prestazioni open-loop del VCO a 2,2 GHz, quello LMX2572 a 4,9 GHz: il termine VCO non e' automaticamente migliore con LMX2572.

## Esempio di mixing reciproco (non predizione realistica della radio)

Se un segnale interferente e' presente al mixer a -40 dBm, filtraggio audio equivalente 2400 Hz, NF = 5 dB, rumore termico = -174 + 10log10(2400)+5 = -135,2 dBm. Con fase-noise LO a 10 kHz = -125 dBc/Hz, la potenza di rumore tradotta nel filtro e' circa -131,2 dBm (valore semplificato, PN piatta e attenuazione del filtro IF ignorata). Bisognerebbe circa -129 dBc/Hz affinche' questo contributo non superi il rumore termico, oppure <= -135 dBc/Hz per un margine di 6 dB. Questo e' un obiettivo di studio, non una misura o un requisito contrattuale definitivo; il livello reale di interferenza al mixer dipende dai filtri RF e dalla topologia.

## Decisione e piano di prove

**Raccomandazione:** avviare il progetto della scheda-sintetizzatore modularizzata con LMX2572 come riferimento, mantenendo ADF4351 come opzione fino al collaudo. Il nuovo filtro d'anello deve essere simulato con uno strumento idoneo, con valori reali TCXO/Kv/charge-pump, e con tolleranze PVT. Vanno richieste curve phase noise dBc/Hz vs offset (100 Hz, 1 kHz, 10 kHz, 100 kHz), spurie e tempo di aggancio, alle estremita' della gamma e nel canale 9. Senza strumento RF esterno e prototipo questi valori NON possono essere dichiarati verificati.

Fonti primarie (consultate 06/11/2026):
- TI LMX2572 datasheet SNAS740B: https://www.ti.com/lit/ds/symlink/lmx2572.pdf
- ADI ADF4351 Rev A: https://www.analog.com/media/en/technical-documentation/data-sheets/adf4351.pdf
