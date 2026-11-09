# Modulo PLL/LO V6.4 — schema a componenti candidato

**Stato: studio progettuale pin/rete, non schematico KiCad con ERC. NO FAB, RX ONLY, TX DISABILITATA.**

## Obiettivo

Generare LO sopra il canale in prima conversione, **fLO = fRX + 10,695 MHz**. Percorso: TCXO 12,8 MHz → OSCin → U401 LMX2572 (R=10, fPFD=1,28 MHz, integer N) → VCO 4,64768–4,992 GHz → ÷128 → RFoutA → disaccoppiamento e filtro/matching da definire → **J402 LO_RX** 36,310–39,000 MHz → mixer RX. RFoutB inutilizzata e da terminare secondo produttore.

## Collegamenti e sezione elettrica

- U401 LMX2572 in VQFN/RHA 40: 41 terminali comprendendo exposed pad; la tabella V6.4 eredita **senza sostituirlo** il pinmap precedente e include i cinque pin STM32 V6.1.
- PA4 → `PLL_CS_N` (CSB pin 24); PA5 → `PLL_SCK` (SCK pin16); PA7 → `PLL_SDI` (SDI pin17); PB0 ← `PLL_MUXOUT` (pin20); PB1 → `PLL_CE` (pin1). PA6 resta riservato, nessuna modifica ai pin codec. **CE pulldown 47 kΩ**, CSB pullup 10 kΩ, resistenze serie SPI 33 Ω candidate.
- U402 TPS7A2033DBVR da `5V_RF` della V6.3 attraverso FB401 → `3V3_PLL`; rail distinto da `3V3_A`. Condensatori di ingresso/uscita e bypass U401 come studio V0.8; quantità di BOM V6.4 **non è un circuito di bypass completamente validato pin-per-pin**.
- J401 controllo SPI/CE/MUXout + GND; J402 **solo LO ricevitore**, connesso a mixer RX via stadio filtro/matching da definire. Nessuna connessione verso finale RF o TX, nessun connettore RF PA abilitato.
- CPout (pin12) / Vtune (pin35) tramite filtro loop precedente V0.6, **non ricalcolato con modello VCO completo**; richiede TICS Pro, fase, stabilità e spur.
- Oscillatore TCXO 12,8 MHz (Y401) candidato: livello OSCin, condensatori AC e possibile pin 10 AFC/GND sono **da risolvere** prima dello schema nativo; ref_good come controllo logico della V6.4 è un segnale ipotetico, non prova materiale.
- I pin SYNC/SYSREF/RAMP non utilizzati richiedono stati sicuri/terminazione verificata sul datasheet. MUXout richiede bit reali di configurazione per lock-detect; al momento il firmware interpreta un booleano sintetico, non il registro fisico.

## Sequenza di avvio prevista

1. Alimentazioni protette 5V_RF, 3V3_PLL e riferimento TCXO presenti, PWR_GOOD_HW valido. In PA l'LO RX può essere spento.
2. Asserire CE soltanto dopo presenza di alimentazioni e riferimento; attesa **almeno 0,5 ms** per la stabilizzazione interna (il modello usa 1 ms).
3. Caricare **soltanto** profilo di 126 registri (125 → 0) con valori reali validati TICS Pro e relativo RESET R0. Il generatore di V6.4 **non emette registri**: precedente `lmx2572_spi_transport_v15.py` accetta profilo solo con conferma esplicita.
4. Attendere MUXout configurato per lock-detect e lock stabile per finestra *software* candidata 3 ms. Un cambio canale o perdita lock silenzia RX prima di un eventuale aggiornamento.
5. Ogni fault, PWR_GOOD_HW assente, ref mancante o passaggio PA porta a RX silenziata e CE OFF. **TX sempre FALSE**, compreso CH9 e tutti i canali della banda D.

## Limitazioni critiche

**Solo aritmetica**: il calcolo fVCO=fPFD×N e fLO=fVCO/128 è esatto per 270 posizioni; non dimostra lock hardware, correttezza dei valori registri, selezione VCO core, livello di uscita, rumore di fase, spur, spur da buck, phase noise TCXO, EMI, filtri LO, RF image rejection o stabilità del loop. Non usare questa BOM per ordinare PCB.

Fonti: TI LMX2572 https://www.ti.com/product/LMX2572 ; TI TPS7A20 https://www.ti.com/product/TPS7A20 .
