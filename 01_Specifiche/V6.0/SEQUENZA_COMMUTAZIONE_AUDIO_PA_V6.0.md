# V6.0 — logica di sequenziamento PA, RX e muting

Questa sequenza è una **specifica** per la futura implementazione su STM32, con ingresso AMP_SD su porta di sicurezza hardware ancora da disegnare. Non attribuire tempi garantiti al chip senza verifica.

1. Su power-up AMP_SD=0 (R650), MUX_EN_N=1 (R601), relè K601 spento (R661), DAC in mute. Hardware TX inhibit indipendente.
2. Abilitare 3V3_AF, configurare codec/PLL audio I²S/SAI, generare VMID, alimentare stadio audio, verificare PowerGood e fault.
3. Per commutazione modo: AMP_SD=0, MUX_EN_N=1, attendere cessazione segnali audio, impostare selezioni MUX e PA_RELAY_CMD, attendere contatto stabile (tempo di contatto dal MPN futuro), poi attivare il codec e infine AMP_SD=1 solo dopo consenso di sicurezza.
4. PA_MODE_HW=1: **RF_TX_ENABLE forzato a 0 per via cablata**. Il percorso di modulazione TX DAC R resta fisicamente scollegato nel modulo AUDIO/PA. In modalità PA il percorso MICROFONO è selezionato, ma resta silenziato finché PTT non è premuto; al rilascio PTT viene silenziato senza commutare a RX.
5. Fault_n=0, lost power, MCU watchdog, relè non assestato, muting di transizione: AMP_SD=0 e DAC MUTE, senza riattivazione automatica TX.
6. Staccare carichi BTL solo con AMP_SD=0; non ponticellare i due altoparlanti né usare morsetti comuni a chassis. Da verificare il comportamento dei relè su amplificatori class-D ad alta frequenza e relative emissioni EMI.

**Limiti:** sequenza temporale proposta 20 ms di muting prima/40 ms dopo il contatto è un punto di partenza, non un tempo misurato. Non si devono dichiarare tempi soddisfatti senza caratteristiche del relè e prove sul prototipo.
