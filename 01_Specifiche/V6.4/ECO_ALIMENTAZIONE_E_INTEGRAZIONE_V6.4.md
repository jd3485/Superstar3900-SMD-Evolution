# ECO-V64 — integrazione alimentazione/MCU/PLL, obbligatoria nel progetto unificato

1. La V6.3 prevede già `PLL_LO` **0,150 A nominali / 0,250 A inviluppo** sul `5V_RF`. La V6.4 **non aggiunge una seconda voce di carico**: divide il medesimo budget in TPS7A20 dedicato `3V3_PLL` (LMX ~82 mA tipici, TCXO 10 mA assunto, I/O/buffer 13 mA assunti = circa 105 mA, 130–150 mA target di progetto). Attenzione: TCXO e buffer potrebbero essere alimentati diversamente, quindi ricalcolare i consumi reali.
2. V6.3 `3V3_A` (45 mA nominali / 80 mA inviluppo) **non deve alimentare direttamente LMX2572**. Lasciarlo agli analogici originari.
3. LDO `U402 TPS7A20` è capace nominalmente di 300 mA ma la **termica può essere il limite**: a 5→3,3 V e 150 mA dissipa idealmente 0,255 W; con RθJA illustrativa conservativa 199,6 K/W e ambiente 85°C si ottiene 135,9°C, oltre al limite di riferimento 125°C. Richiede package/PCB/condizioni reali o architettura alternativa; NON APPROVATO.
4. CE/U401: pulldown fisico e rete `PWR_GOOD_HW` coerente V6.2; `PLL_CE` PB1 non può essere unico interblocco di sicurezza generale TX. Mute RX durante lock mancante è previsto nel firmware ma hardware da validare.
5. `PLL_CS_N` PA4, `PLL_SCK` PA5, `PLL_SDI` PA7, `PLL_MUXOUT` PB0 e `PLL_CE` PB1 **già riservati in V6.1**, senza sovrapposizione con audio e pannello. Mappa esatta negli allegati.
6. Uscita RX LO 36–39 MHz: filtro/matching e isolamento dalle alimentazioni switching da definire; evitare collegamento al TX. Non mettere PA RF J907 in BOM da montare.
7. Profilo registri TICS Pro non esiste ancora, fPFD 1,28 MHz è nel range **integer-N** ma sotto il minimo per modalità MASH 1–4; scegliere **integer mode**. Non copiare le parole dei registri di vecchie prove o di un progetto LP diverso.
8. TI Rev.B tabella PFD_DLY_SEL/ordine modulatori da confermare nel profilo TICS Pro. I core VCO della mappa V0.6 sono *stime*, non vanno forzati.
9. Mantenere aperti: TCXO pin10 AFC/GND, filtri analogici CPout/Vtune, termiche, EVM/TICS, parità KiCad, misure RF e spuri.
