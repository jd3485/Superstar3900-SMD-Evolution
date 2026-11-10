# V7.10 — PASSAGGIO DAL MODELLO ALL'EDA NATIVO, SUPERSTAR 3900 SMD EVOLUTION

**10 novembre 2026.** Baseline V7.9 su main, senza sostituire o eliminare DSP, simulazioni, firmware, BOM e test V7.0–V7.9. **NO FAB / NO TX**.

## 1. Cosa rappresenta il nuovo file KiCad

Root: `04_KiCad/Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch`

È un **file schematico gerarchico nativo**, con tre sheet KiCad collegati ai sorgenti esistenti:
- `Gerarchico_Alimentazioni_V1.5/S3900E_AUX_POWER_V1_5.kicad_sch`, che comprende le pagine reali eFuse AUX / buck 5V / LDO-TCXO-PLL;
- `Modulo_MCU_CODEC_V2.1/S3900E_MCU_CODEC_AFE_V2_1_DRAFT.kicad_sch`;
- `Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB/S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_sch`, per il quale esiste il coupon PCB V5.2 **senza qualifica fabbricazione**.

Queste pagine sono **fisicamente indipendenti**. Nessun sheet pin del root collega alimentazioni, PLL, MCU, codec o RF tra loro. La matrice `04_KiCad/Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB/MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv` contiene **15 contratti OPEN/HOLD**; i nomi di net coincidenti tra moduli non sono un permesso di cortocircuitare i rail. **NON si tratta di un circuito completo già interconnesso.**

## 2. Verifica con KiCad vero (9.0.8 in CI Ubuntu)

Prima della V7.10 c'erano schemi e un coupon PCB reali, ma gli originali dichiaravano esplicitamente KiCad ERC/DRC non eseguiti. Ora `.github/workflows/v710_kicad_native_rx_audit.yml` installa il vero `kicad-cli` ed esegue:
- `kicad-cli sch export netlist` sulla nuova gerarchia, con output `integration.net` nel report CI. **PASS generazione file** e warning di annotazione da correggere.
- `kicad-cli sch erc` sulla gerarchia V7.10, sulla AUX V1.5, su MCU V2.1 e su RX V5.2 standalone.
- `kicad-cli pcb drc` sul coupon V5.2. Output non filtrato e scaricabile dall'artifact GitHub Actions `v710-kicad-native-audit-not-for-fab`.
- 12 test statici V7.10 + tutte le regressioni software V7.1–V7.9 (143 test) preservate.

**Audit baseline effettivo KiCad 9.0.8, per contrasto con eventuale successivo miglioramento:**

| File | Rilevazione |
|---|---|
| Nuovo root RX/POWER/MCU | Netlist export riuscito ma warning annotazione; ERC **459 segnalazioni = 43 errori, 416 avvisi** |
| AUX V1.5 | ERC **270 = 22 errori, 248 avvisi** |
| MCU V2.1 | ERC **110 = 18 errori, 92 avvisi** |
| RX V5.2 schema standalone | KiCad CLI exit **3**, `Failed to load schematic`, dunque **ERC NON ESEGUITO** su questo root storico isolato; il suo contenuto è comunque letto come figlio del nuovo root |
| Coupon RX V5.2 PCB | **91 violazioni DRC** e **63 connessioni assenti** (categoria separata del report); 6 fori via Ø0.25mm contro minimum Ø0.30mm, 15 librerie footprint non risolte e 70 warning via dangling |

**Significato dei numeri:** non si sommano ERC root e singoli moduli per inventare un totale, perché l'ERC root include i moduli; il DRC classifica 91 violazioni e separatamente 63 unconnected. Un workflow verde verifica solo che l'audit si sia svolto e che i difetti siano stati documentati, NON che ERC/DRC siano 0 o che il PCB sia pronto.

## 3. Ordine corretto per arrivare al circuito completo

1. **Stabilizzare il coupon RX:** risolvere la ragione reale del mancato caricamento standalone, configurare simboli/footprint portabili, mantenere la storia originale e correggere tutti gli errori ERC rilevanti. La prova sperimentale di aggiungere `sheet_instances` non ha risolto il problema: è stata rimossa, il FAIL conservato nei log.
2. **Revisionare il PCB RX con KiCad DRC:** 63 connessioni mancanti, 6 vie termiche fuori dal limite, 70 dangling via e 15 warning libreria. Non abbassare artificiosamente i parametri DRC per far apparire un falso PASS; verificare realmente piazzamento, footprint SMA, ground return, LNA termica e fab requirements prima di cambiare fisicamente le via.
3. **Qualificare alimentazioni e MCU:** risolvere 22/18 ERC errori dei moduli preesistenti, controllare datasheet pin e rail, LDO/buck/eFuse/PLL startup, logica I/O e codec. Il segnale `+5V_BENCH` di un modulo di prova NON equivale per nome a `5V_RF_PREREGULATED` senza revisione elettrica.
4. **Interconnessione reale:** aggiungere *solo dopo* pin di interfaccia gerarchici, netlist completa, qualificazione di RF ricevente (preselettore, conversione IF1/IF2, AGC, commutazione), unità MCU audio e test automatici delle reti. Poi iniziare un vero PCB integrato da una netlist elettrica approvata, non concatenare piste fra due PCB storici senza revisioni.
5. **Firmware e simulazioni in parallelo:** mantenere 143+ regression tests, DSP/audio/PLL, modelli numerici e documentazione di ogni scelta; associare i pin firmware a uno schema reale verificato, senza inventarli.
6. **TX fisicamente separata:** i blocchi TX restano DNP, nessun PA/antenna/PTT, alimentazioni DAC non collegate, Lattice SG48 PCF **HOLD** (XLSX vendor originale non verificato). Nessuna fabbricazione o emissione RF.

## 4. Stato release

**EDA parziale: IN LAVORAZIONE. Esportazione netlist: PASS con problemi annotazione; ERC/DRC: FAIL/VIOLAZIONI ancora da risolvere; RX V5.2 root standalone: NON CARICABILE; hardware: NON PROGETTATO COMPLETAMENTE.**

Non eseguire Gerber/foratura/posizionamento, non ordinare PCB. **NO FAB / NO TX.**
