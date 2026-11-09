# V6.2: temporizzazione funzionale, modello (NON misure)

| Evento | Condizione di modello | Effetto TX | Effetto AMP |
|---|---|---|---|
| Avvio con 3,3 V assenti | Gate senza alimentazione e resistori pulldown | LOW | LOW |
| 3,3 V stabilizzati e RESET ancora LOW | SUP_3V3_OK=0 | LOW | LOW |
| Reset rilasciato ma 13,8V sotto UV | BAT_UV_OK=0 | LOW | LOW |
| 13,8V sopra OV | BAT_OV_OK=0 | LOW | LOW |
| PA attivata | PA_MODE_HW=1, NC RX apre | LOW | Può restare audio abilitato se codec pronto |
| Guasto sensore SWR o termico | FAULT_LOOP_OK=0 | LOW | Audio non necessariamente spento |
| WDI bloccato | watchdog TPS3823 interviene dopo intervallo specificato | LOW quando RESET attivo | LOW |
| Jumper J801 non montato | TX_BENCH_KEY=0 | **LOW sempre** | Non influenza audio |
| Codice non pronto, codec fault | CODEC_READY=0 o AMP_FAULT_N=0 | Vincolo TX non derivato da audio | AMP_SD=LOW |

RESET del supervisore ~200 ms e timeout watchdog ~1,6 s sono parametri nominali informativi: non caratterizzano la sequenza reale e NON sostituiscono i limiti min/max da datasheet.

L'uscita logica a 3,3 V non è adatta a comandare direttamente un finale RF o un relè: i relativi driver e isolamento devono essere progettati e verificati.
