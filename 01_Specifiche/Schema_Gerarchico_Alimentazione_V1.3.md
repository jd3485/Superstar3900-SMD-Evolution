# V1.3 - Schema gerarchico ausiliari (DRAFT)

Il nuovo progetto KiCad contiene 1 foglio top-level e 3 fogli funzionali reali: `01_EFUSE_AUX`, `02_BUCK_5V`, `03_PLL_LDO_TCXO`. Ogni interfaccia è una coppia `pin` del foglio principale + `hierarchical_label` posizionata su una connessione esistente nel foglio figlio, non una mera etichetta ripetuta in due file indipendenti.

Percorso **intenzionale** (solo alimentazione ausiliaria): `PWR_13V8_AUX_RAW -> eFuse TPS26600 -> BUCK_VIN_PROTECTED -> buck TPS54202 -> 5V_RF_PREREGULATED -> 2 LDO 3.3 V per PLL/TCXO`. Sul top-level sono realmente presenti tratti di filo tra le uscite dei blocchi e gli ingressi successivi. Il ritorno `GND_MAIN` è comune sui tre fogli mediante bus sul top-level; `EFUSE_RTN` rimane esclusivamente locale al foglio di protezione e non viene esposto.

**Stato:** progetto schematico DRAFT. Impossibile certificare la connettività netlist e l'ERC senza KiCad; questo ambiente non dispone del programma `kicad-cli`. I controlli Python eseguiti verificano struttura dei file, abbinamento dei nomi e tratti di filo, NON il controllo di regole elettriche.

Bloccanti: footprint reale F200 Littelfuse 451, TCXO pin10 e footprint, scelta TVS/montaggio e coordinamento surge/fusibile, qualificazione dei transitori, schemi funzionali incompleti, filtri EMI buck, errori ERC da risolvere, ingresso 13.8 V senza connettore e fusibile principale, stadio RF finale non incluso.

Sequenza di verifica nativa da eseguire con KiCad 8 o 9 installato: aprire `S3900E_AUX_POWER_V1_3.kicad_sch`, verificare collegamenti di gerarchia, invocare `kicad-cli sch erc -o erc_V1_3.txt S3900E_AUX_POWER_V1_3.kicad_sch`, poi `kicad-cli sch export netlist -o netlist_V1_3.net ...`; verificare manualmente nodi di eFuse, buck, LDO e assenza di `EFUSE_RTN` condiviso.

Fonti: https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/ ; https://www.ti.com/lit/ds/symlink/tps2660.pdf
