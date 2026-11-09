# ECO V6.7 — integrazione delle revisioni precedenti

- V6.5 `F501` era un filtro ideale segnaposto; V6.6 è candidato `SXBP-27R5+`, selezionato qui come **F501 preferito**, senza cancellare l'alternativa LC V6.6.
- V5.2–V5.8 `U101 ADL5535`: **riutilizzo logico**, evitare duplicati in BOM consolidata; l'integrazione C701/L701/C702/C703/C704/C705 è solo la nuova topologia candidata. Il file KiCad esistente NON viene modificato in questa revisione.
- V6.5 `U501 ADE-1+ RF3`: rimane il carico nominale a 50 Ω della catena; LO +7dBm ed IF non qualificati.
- V6.3 `5V_RF`: corrente ADL5535 **97mA tip, 115mA max**. La precedente allocazione del front-end deve essere confrontata con la nuova; **non aggiungere due volte lo stesso U101 legacy**. Se il ramo 5V RF ha un limite di 80mA va riesaminato. La sua alimentazione separata/switch RX resta un'interfaccia non chiusa.
- V6.2 PA_HW/RX_BLOCK: non implica isolamento RF antenna effettivo né spegnimento RF U101: sono necessari commutatore d'antenna e hardware bias-enable, attualmente NON IMPLEMENTATI.
- V6.4 TLS 3.3V PLL: rischio termico aperto, indipendente dalla catena a 5V RX.
- Sviluppo futuro: test di near-channel blocking, doppio tono, reiezione immagine misurata e termica sul PCB, applicazione ECO sul progetto KiCad gerarchico dopo disegno completo.

**Nessuna modifica retroattiva ai sorgenti storici. Produzione e TX vietate.**
