# Riferimento TCXO, alimentazione e controllo PLL - V0.6

## TCXO proposto (da verificare approfonditamente)
**TXC 7N-12.800MBP-T**: 12.800 MHz, 3.3 V, uscita CMOS, stabilita indicata ±280 ppb, SMD 7 x 5 mm, max consumo 10 mA secondo scheda distributore (DigiKey, 06/11/2026). Valore frequenza errore relativo al riferimento = ±0.28 ppm (12.8 MHz -> ±3.584 Hz), che si propaga proporzionalmente alle frequenze derivate. Un singolo oscillatore FI indipendente introduce un proprio errore: NON attribuire un errore RX/TX complessivo di soli ±0.28 ppm.

**Punti aperti:** datasheet TXC originale, footprint 10-pad, pin abilitazione, rumore di fase vs offset, comportamento alimentazione, compatibilita livelli 12.8MHz OSCinP e capacita d'accoppiamento, disponibilita al momento dell'ordine.

## Collegamenti del LMX2572
- Pin 7 VccDIG, 11 VccCP, 15 VccMASH, 21 VccBUF, 26 VccVCO2, 37 VccVCO -> 3V3_PLL. Posizionare decoupling **per pin** come pinmap e datasheet: non raggruppare o trascurare i condensatori.
- Pin 3, 10, 27, 29, 33, 36, 38 sono **nodi BYPASS interni**, NON reti di alimentazione. Collegarvi SOLO i condensatori indicati dal datasheet, non ingressi esterni.
- Rete 3V3_PLL da LDO basso rumore: sorgente dalla distribuzione 13.8V ma topologia di conversione, dissipazione, ripple, transitori, inrush e capacità bulk restano da definire. LMX2572 circa 82-86mA configurazione uscita divisa tipica; dimensionare con margine e TCXO/MCU separati quando opportuno.
- TI indica livelli 3.0-3.5V per LMX2572. SPI 3.3V logico; MCU da definire. Reset CE, lock detect su MUXout: se PLL non lock, **TX inibita hardware/firmware con strategia fail-safe**.
- OSCinP e OSCinM richiedono accoppiamento AC per i segnali applicati, ingresso single-ended da qualificare. SCK/SDI/CSB e MUXout secondo sequenza registri TI e timing. Nessun firmware di produzione ancora esiste.

## Frequenze e cambio VCO core
- fRX 25.615-28.305 MHz, FI proposta 10.695 MHz, fLO 36.310-39.000 MHz, divider output 128; VCO 4.64768-4.9920 GHz.
- VCO3 copre 4.2-4.65 GHz, VCO4 4.65-5.2 GHz (TI Table 136, range nominali indicativi). Nelle 270 frequenze VCO3 ricorre solo su A-CH1 (4.64768GHz) e A-CH2 (4.64896GHz); i restanti 268 sono in VCO4 per il valore nominale di Table 136.
- Vicino al confine NON forzare un VCO core tramite semplice confronto in firmware: eseguire la calibrazione automatica TI e verificare temperatura / tensione / lock. Quick re-calibration potrebbe essere utile dopo caratterizzazione.

## Sicurezza e conformita
- Ricezione estesa; trasmissione vincolata ai canali CB autorizzati e alle modalita/regole vigenti da verificare a livello italiano. Questo documento NON abilita o autorizza TX fuori banda.
- Non alimentare radio o mixer sui soli dati di questa nota.

Fonti: TI https://www.ti.com/lit/ds/symlink/lmx2572.pdf ; TXC tramite https://www.digikey.it/en/products/detail/txc-corporation/7N-12-800MBP-T/5222401 .
