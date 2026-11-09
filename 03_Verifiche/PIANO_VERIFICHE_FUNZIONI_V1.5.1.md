# Piano di prova - Nuove funzioni V1.5.1

**Tutte le seguenti prove sono pianificate, non eseguite sull'hardware.**

| Test | Criterio previsto | Prerequisito |
|---|---|---|
| VX-01 | PTT e VOX non aggirano TX-LOCK | Firmware+stato PLL+schema TX |
| VX-02 | Nessun innesco da AF in ascolto a livelli previsti | Prototipo codec/microfono/cassa |
| VX-03 | Soglia/ritardo VOX ripetibili entro tolleranze fissate | Hardware ADC/DSP |
| DW-01 | Scansione A/B e ripresa dopo segnale, senza perdita canali manuali | PLL inizializzato e RX |
| DW-02 | PTT/VOX in DW non trasmettono su B senza scelta esplicita | Firmware TX policy |
| DW-03 | CH9 o PA disattiva DW immediatamente | Host MCU+comandi |
| RB-01 | Beep presente solo su fine TX autorizzata, con ampiezza e durata corrette | Modulatori TX, misura BF/RF |
| RB-02 | Beep inibito su CH9 e PA | Logica di controllo |
| EC-01 | BYPASS Echo indistinguibile da percorso voce di riferimento | Audio SMD + misure |
| EC-02 | Echo non provoca sovramodulazione/deformazione SSB | Modulatori e analizzatore |
| CT-01 | RX/TX CTCSS configurabili in modo indipendente in FM | Decoder/encoder e FM |
| CT-02 | Squelch non silenzia CH9 per impostazione CTCSS pregressa | Logica e test audio |
| DC-01 | Supporto N e I sui 104 codici dopo valida tabella | Codec DSP+radio di confronto |
| DC-02 | Codici e toni non danno falsi positivi con rumore/interferenze | RX FM + sorgenti RF |
| MD-01 | Allontanandosi da FM CTCSS/DCS disabilitati | Macchina a stati |
| SAFE-01 | RF TX inibita fuori dai canali autorizzati anche se VOX acceso | Profilo paese + TX |

Stati possibili: `NON ESEGUITO`, `PASS SOFTWARE`, `PASS STRUMENTALE`, `FAIL`, `BLOCCATO`.
Nessuno degli accettativi hardware e' ora PASS.
