# Rapportino di revisione V6.0 — modulo AUDIO/PA

- Riferimenti componenti: **64**; assegnazioni pin: **206**; reti: **66**.
- Nuove fonti: JSON circuito candidato, BOM, netlist pin, elenco reti, schema tecnico SVG, matrice stati audio e modello di controllo Python.
- Selezione componenti: TMUX1308 PW16, TLV9062 SOIC8, TPA3111D1 HTSSOP28. Pinout dei due IC principali verificato su datasheet ufficiali, senza importer automaticamente librerie CAD.
- V5.9 preservato; nuovo indirizzamento PA con PTT muting e relè BTL su entrambi i poli.
- **35 test statici pass**, incluso test esaustivo 5120 casi del router. Nessuna misura reale, KiCad nativo o SPICE eseguito.
- Completamento AUDIO/PA: sottosistema in avanzamento; interblocco AMP_SD reale, relè/EMI e connettori da chiudere in revisioni future. **NO FAB / NO PCBWay / TX OFF.**
