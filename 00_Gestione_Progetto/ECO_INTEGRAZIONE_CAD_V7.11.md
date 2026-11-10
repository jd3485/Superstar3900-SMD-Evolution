# ECO V7.11 — modifica PCB RX documentata, nessuna trasmissione

**Baseline:** V7.10 su main commit `d6d0d08be5dfdd8afed1103ee46280a82e2c68cd`. **NO FAB / NO TX**.

- Copiato il coupon RX originale V5.2 e modificato soltanto **sei** via in prossimità U101: foro 0,25→0,30 mm, rame 0,55→0,60 mm. Originale intatto, stesse 8 reti utili, stesse 15 impronte, stesso numero di 70 vias, nessuna nuova linea TX. La copia è nella nuova directory KiCad V7.11 `*_NOT_FOR_FAB`.
- Aggiunto `fp-lib-table` locale con riferimenti ai tre `.pretty` legacy. L'esecuzione DRC rivela ancora **15 warning footprint**, quindi la portabilità non è stata ancora qualificata.
- Creato `confronta_drc_rx_v711.py`: confronta rapporti **KiCad nativi** vecchio/nuovo, esige zero errori drill e diminuzione totale delle violazioni; non considera altri avvisi come PASS.
- Verifica iniziale V7.10: 91 DRC + 63 unconnected. Nuova misura V7.11: **85 DRC + 63 unconnected**, 70 via_dangling e 15 lib issues invariati. **DRC generale NON PASS**, ma 6 errori reali corretti. Report di audit da Actions run [42856926563](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42856926563), log controllato.
- 8 nuovi test +12 V7.10 +143 regressioni V7.1–V7.9 = **163 Python PASS**, 0 FAIL/SKIP; regolari modelli e firmware preservati. Questa workflow V7.11 non include nuovi Icarus, Yosys o ERC root.
- Next: caricare RX standalone, correggere riferimenti duplicati, libraries mancanti, percorsi di ritorno GND e 63 net scollegate, quindi schema elettrico RX/power/MCU interconnesso con segnali qualificati e PCB integrato.

**La nuova scheda non è destinata a fabbricazione. Non inviare Gerber, non montare FPGA/DAC/PA, non trasmettere.**
