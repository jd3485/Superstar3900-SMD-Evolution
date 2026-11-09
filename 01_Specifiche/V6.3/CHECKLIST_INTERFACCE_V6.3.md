# ECO e interfacce alimentazioni V6.3

- ECO-V63-01: il segnale V6.2 `+13V8_PROTECTED` equivale a V6.3 `13V8_PROTECTED`: normalizzare netlabel al momento della futura integrazione, senza alterare lo storico.
- ECO-V63-02: `13V8_AUD` e `5V_CODEC` erogati solo ai rispettivi moduli; `5V_RF` filtrato, `3V3_UI` via ferrite, `3V3_A` tramite LDO, `1V8_CODEC` separato. Verificare effettive rail del TLV320AIC3204 nel progetto completo.
- ECO-V63-03: `PG_5V` AND `PG_3V3` fornisce `PWR_GOOD_HW`; V6.2 `POWER_GOOD_HW` deve essere rimappato una sola volta. I PGOOD open-drain richiedono pullup e verifica di livelli: **schema V6.3 non li include ancora con il valore definitivo**.
- ECO-V63-04: S901 interruttore hardware EN→VS con R902 pulldown di sicurezza e J902 di test **DNI**. Il circuito permette un avvio candidato ma non è stato verificato elettricamente.
- ECO-V63-05: futuro PA RF J907 DNI e `RF_PA_DISCONNECTED`: serve un ramo dedicato con fusibile/cavi/interblocchi indipendenti dopo il dimensionamento TX.
- ECO-V63-06: Q903 high-side switch audio ancora da selezionare, controllo attivazione `AUDIO_POWER_ENABLE` da V6.2 con controllo anti-pop; nessun collegamento diretto 13.8V ai GPIO.
- ECO-V63-07: selezionare fusibile reale, TVS e MOSFET da forma d'onda transitoria e corrente di picco del finale RF; verifica IEC/ISO non eseguita.
- ECO-V63-08: disaccoppiamento RF, massa e filtraggio emissioni a 26–28MHz non verificati. Le frequenze di commutazione e le armoniche possono interferire con l'RX.
