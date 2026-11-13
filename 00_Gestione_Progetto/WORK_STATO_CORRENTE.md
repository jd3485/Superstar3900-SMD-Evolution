# WORK_STATO_CORRENTE.md — checkpoint canonico di ripartenza da GitHub

## STATO LIVE PIÙ RECENTE — 13 novembre 2026 — **V7.39 INTEGRATA / VIN−VOUT TPS7A20 ABS-MAX, 20 TEST PASS**

**GitHub verificato:** [PR #42](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/42) **MERGED** squash `94347b21a45a618ccabdf814467dac91acf3751a`; precedente V7.38 PR#41 MERGED `91e4f9d7867bb1fdcd18d19a752460e73d38cd5d`. [Run V7.39 **43391844669**](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43391844669) **SUCCESS / 20 Python unittest PASS**; [cost/safety policy run **43391844470**](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43391844470) **SUCCESS**. Nessuna modifica CAD/footprint: rapporto `03_Verifiche/V7.39/RAPPORTO_ABSMAX_TPS7A20_POWERDOWN_V739.md`, script `03_Verifiche/V7.39/test_tps7a20_powerdown_absmax_v739.py`, workflow PR minimo. Non avviato KiCad9 per questa analisi perché sorgente CAD invariato.

**Nuovo criterio TI SBVS338H §5.1 vincolante:** su `TPS7A2033PDBVR` U6205/U6206 `VOUT ≤ min(6.5V, VIN+0.3V)` massimo assoluto. È distinto dal limite per corrente inversa **15mA per breve periodo** (§6.3.7). Il test legge la schematic MCU V7.36 reale e accerta pin IN/EN/OUT degli LDO e **12 condensatori**: `5V_DIGITAL_FILTERED` nominali **14.1µF** (C6215 1µF, C6219 10µF, C6220 100nF, C6221 1µF, C6223 1µF, C6225 1µF), `3V3_CODEC_IO` **1.2µF** (C6201 100nF, C6224 1µF, C6231 100nF), `3V3_CODEC_LDOIN` **11.1µF** (C6207 100nF, C6208 10µF, C6226 1µF). Non sono Ceff e non sono capacità full-board. Modello di rampe indipendenti puramente illustrative `5 exp(-t/τIN)`, `3.3 exp(-t/τOUT)` produce superamento di `VIN+0.3V` in esempi di collasso rapido VIN; **non** è simulazione TPS7A20 né dimostrazione che l'hardware reale subisca stress. Il test **rifiuta signoff** senza tracce di tensione e corrente validate. Nessuna modifica diodo/RC arbitraria.

**NEXT V7.40:** priorità nuova: analizzare nella netlist root 7 fogli gli upstream eFuse/buck 5V, condizioni di scarica e current sink di tutti i carichi sul `5V_DIGITAL_FILTERED`; valutare V_IN(t), V_OUT(t), I_REV(t) con modelli fisici validati o misure su prototipo e limite VOUT−VIN e 15mA; se serve ECO, specificare circuito reale con MPN e rischi reverse/backfeed, verificare nuovo ERC/netlist prima-dopo. Qualifica Ceff X7R e firmware RESET/ALDO ancora HOLD.

**CAD invariato V7.36:** 134 componenti / 101 reti / **33 footprint mancanti** / ERC **36 errori+221 warning**, nessuna PCB completa e nessuna DRC globale. 15 interfacce cross-domain OPEN/HOLD, SG48 HOLD, Y1 TCXO pin10 AFC/GND HOLD, power/PLL/thermal da completare. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. PCB overall storico stimato ~10%, senza incremento da test/report. Le voci storiche sotto sono fotografie delle revisioni precedenti.

---


## STATO LIVE PIÙ RECENTE — 13 novembre 2026 — **V7.38 INTEGRATA / CORRENTE INVERSA TPS7A20 DA CAPACITÀ REALI — 20 TEST PASS**

**GitHub verificato:** [PR #41](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/41) **MERGED**, squash `91e4f9d7867bb1fdcd18d19a752460e73d38cd5d`. Baseline precedente V7.37 PR#40 MERGED squash `6d6c7f694c22fa12047c3099c9cd0dfc839b3947`. **Workflow dedicato [run 43330419481](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43330419481) SUCCESS / 20 unit test PASS**, [cost/safety policy run 43330421407](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43330421407) SUCCESS. V7.38 **NON modifica schemi/PCB**. Test `03_Verifiche/V7.38/test_codec_ldo_reverse_current_v738.py`, rapporto `03_Verifiche/V7.38/RAPPORTO_REVERSE_CURRENT_LDO_CODEC_V738.md`; workflow Python PR piccolo, nessun KiCad9 ripetuto perché CAD immutato.

**Risultato ingegneristico:** C nominale in parallelo alle uscite dei LDO **U6205 3V3_CODEC_IO = 1.2µF** (C6201=100nF, C6224=1µF, C6231=100nF) e **U6206 3V3_CODEC_LDOIN = 11.1µF** (C6207=100nF, C6208=10µF, C6226=1µF). A 3.3V, carica teorica **3.96µC** e **36.63µC**. Fonte produttore **TPS7A20 SBVS338H §6.3.7**: con collasso VIN lo scaricatore attivo non va considerato sufficiente per grandi condensatori; corrente inversa **OUT→IN** limitare a non oltre **5% della corrente rated 300mA = 15mA per breve periodo** (non rating DC continuativo). Con ipotesi estrema **100%** della carica che ripercorre a ritroso LDO in 1ms, I_equiv sarebbe 3.96mA (IO) e 36.63mA (LDOIN); **questo non è il vero picco di corrente inversa**, non è una corrente misurata e non dimostra alcun guasto: occorrono percorso di scarica, corrente nei carichi, reale Ceff e dinamica VIN/VOUT. Uno script fail-closed mantiene ignota `fraction reverse` e non permette signoff senza modello validato.

**Priorità V7.39:** prima di ECO confrontare le capacità sul rail 5V upstream, U6205/U6206 corrente inversa vera e capacità C6208 effettiva sotto DC bias/tolleranza, caratteristiche scarica attiva del package versione P, dropout, soft-start e fault; progettare prova o simulazione elettronica reale della corrente OUT→IN con timing VIN(t), VOUT(t), reverse-current maxima, possibile isolamento se dimostrato. Contestualmente verificare protezione eFuse, timing 5V/3V3, 15 interface OPEN/HOLD e soglie brownout V7.37. Non aggiungere diodi/resistenze/RC per un mero screening.

**Baseline CAD invariata V7.36:** 134 componenti, 101 reti, **33 footprint mancanti**, ERC 36 errori /221 warning, nessuna PCB completa / nessuna DRC globale. Restano SG48 HOLD, Y1 TCXO pin10 AFC/GND HOLD, 15 interfacce cross-module e power/PLL/thermal HOLD, **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Stima PCB storica circa 10%, non aumentare da analisi/test. Stati V7.37 e precedenti nei blocchi sotto sono fotografia storica e non prevalgono su questo stato LIVE.

---


## STATO LIVE PIÙ RECENTE — 13 novembre 2026 — **V7.37 INTEGRATA / VERIFICA BROWNOUT CORNER TI / 16 UNIT TEST PASS**

**Stato GitHub verificato:** [PR #40](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/40) **MERGED** squash `6d6c7f694c22fa12047c3099c9cd0dfc839b3947`; precedente V7.36 PR#39 MERGED squash `e3ea888bdac51ff7d0061c8c6b932e4edb71cbe0`. [Run mirato V7.37 **43328811949**](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43328811949) **SUCCESS con 16 unit test PASS**; [run cost/safety policy **43328811690**](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43328811690) **SUCCESS**. V7.37 **non modifica CAD né BOM/footprint**: solo `03_Verifiche/V7.37/test_tps3840_pl30_brownout_corners_v737.py`, rapporto `03_Verifiche/V7.37/RAPPORTO_BROWNOUT_TPS3840_TPS7A20_V737.md` e workflow Python-only minimale. Non è stato riavviato KiCad9 perché non sono cambiati schemi o PCB.

**Risultato elettrico TI con limiti reali:** il TPS7A2033PDBVR 3.3V in regolazione (VIN almeno 3.6V, 1–300mA, T coperta) ha VOUT(min)=**3.2505V** (accuratezza ±1.5%). Il TPS3840PL30 ha VIT- massimo=3×1.015=**3.045V** (accuratezza ±1.5%) e isteresi massima **0.125V**, dunque VIT+(max)=**3.170V**. **Margine di rilascio statico = +80.5mV**; VOH(min) 0.8×3.2505=2.6004V > VEN(HI)=0.9V; VOL(max)=0.2V < VEN(LOW)=0.3V. Fonti primarie TI SNVSB03E May2026 e TI SBVS338H Jul2024 verificate anche nelle pagine PDF originali. Nessuna modifica arbitraria del MPN TPS3840PL30 necessaria per i soli corner **regolati**; variante PL29 sarebbe più permissiva sui brownout e non automaticamente migliore.

**HOLD essenziali:** sotto `VDD<VPOR` (TPS3840 PL VPOR max0.3V con carico/slew spec) uscita RESET_N **undefined**; nello spazio isteretico circa 2.955–3.170V stato può dipendere dalla storia; TPS7A20 pull-down EN ~500kΩ tipico su floating NON prova di spegnimento contro un driver attivamente alto. U6205 fuori regolazione o in dropout, C6231 Ceff sotto DC bias/temp/aging, carichi, backfeed, transitori e firmware codec RESET/ALDO **non qualificati**. Nessun SPICE/hardware/DRC nel V7.37; CI 16 test dimostra solo envelope algebrico e costanza delle etichette del CAD V7.36. Prossimo progetto V7.38: qualificare dinamica startup/brownout, ripartizione dei carichi e Ceff con dati vendor; intervenire sul CAD **solo se rischio misurabile o nuova topologia fondata**.

**Baseline CAD ancora V7.36**: **134 componenti, 101 reti, 33 footprint mancanti, ERC36 errori/221 warning**. Non esiste PCB unica completa, né vera DRC globale. 15 interfacce cross-module OPEN/HOLD, SG48 HOLD, Y1 pin10 AFC/GND HOLD, ingressi power/return, termica e PLL HOLD. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Percentuale storica ~10% stimata, senza incremento per audit/test.

**Nota:** eventuali blocchi seguenti su V7.36 sono fotografie storiche e non prevalgono sullo stato LIVE presente.

---


## STATO LIVE PIÙ RECENTE — 12 novembre 2026 — **V7.36 INTEGRATA / C6231 MURATA GRM155 0402 REVISORE / KIcad9 PASS**

**GitHub verificato:** [PR #39](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/39) **MERGED**, squash `e3ea888bdac51ff7d0061c8c6b932e4edb71cbe0`. Baseline precedente V7.35 PR#38 MERGED squash `24ae2dd93fed694980dab1fe68e55fabf4ba9ebe`. **Native KiCad9 run [43274909287](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43274909287) SUCCESS**, 7 unittest PASS, pcbnew.FootprintLoad 2 pad geometria vendor, export/ERC prima-dopo 7 fogli; **cost/safety policy run [43274908894](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43274908894) SUCCESS**. Artefatto [#13968524887](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43274909287/artifacts/13968524887). Il vero esito: **134 componenti, 101 reti, 0 differenze dei nodi pin–rete**, solo `C6231` nuova proprietà Footprint e MPN, **footprint mancanti 34→33**, ERC **36 errori/221 avvisi invariati**. Non è stato eseguito un DRC PCB completo.

**Nuovo CAD V7.36:** nuovo MCU `04_KiCad/Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/` e master 7 fogli `04_KiCad/Assemblaggio_RX_Power_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/`. **C6231** bypass `3V3_CODEC_IO`→GND del TPS3840 U6207, nominale 100nF, MPN `GRM155R71C104KA88D` Murata (16V, ±10%, X7R, EIA0402), footprint `S3900E_MURATA_GRM15_V736_HOLD:MURATA_GRM15_0402_REFLOW_REVIEW`; due pad Cu **0.40×0.50mm** centri x ±0.40mm, `a=0.40,b=0.40,c=0.50mm` nella tabella Murata reflow GRM15 JEMCGC-2701X p26. Rapporto `03_Verifiche/V7.36/RAPPORTO_TECNICO_MURATA_C6231_V736.md`. Il vendor land è un **candidato REVIEW**, non progetto assemblabile approvato.

**Riesame vendor post-V7.36 (12 novembre 2026):** TI TPS3840 SNVSB03E §7.4.3 dichiara `RESET_N` **indeterminato quando `VDD < VPOR`**; TI TPS7A20 SBVS338H §6.3.2 dichiara **smart EN pulldown interno** (LDO spento con EN flottante). Questi due fatti rendono plausibile il safe default quando il driver supervisor è disalimentato, ma **non garantiscono EN basso se l'uscita supervisor indeterminata si comporta da driver attivo**. Evitare una nuova resistenza esterna senza calcolare leakage/source current, soglie EN e correnti di fault; la verifica brownout resta **HOLD**. Fonti primarie https://www.ti.com/lit/ds/symlink/tps3840.pdf e https://www.ti.com/lit/ds/symlink/tps7a20.pdf .

**Vincoli ancora aperti per V7.37:** il produttore TI TPS3840 prescrive nominalmente **0.1–1µF vicino a VDD in ambienti rumorosi**; `GRM155R71C104KA88D` nominale 0.1µF **non garantisce capacità effettiva ≥0.1µF sotto 3.3V/tolleranza/temperatura/aging**. Verificare Ceff worst-case o qualificare un C maggiore via ECO. Inoltre uscita TPS3840 per VDD sotto VPOR, EN LDO U6206, brownout e power-down/reverse-current, reset/ALDO codec da qualificare con strumenti appropriati. 15 cross-module OPEN/HOLD, SG48 HOLD, Y1 TCXO pin10 HOLD, power/PLL/thermal da completare. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Nessuna PCB unica completa. Avanzamento storico radio PCB ~10% stimato e non aumentato per solo footprint.

**Nota:** i checkpoint sotto questa sezione sono storici e possono riferire V7.34 o V7.35 come ultimi: questo paragrafo LIVE prevale.

---


## STATO LIVE PIÙ RECENTE — 12 novembre 2026 — **V7.35 INTEGRATA / U6207 TI DBV0005A 5-PAD VENDOR REVIEW / KIcad9 PASS**

**GitHub verificato:** [PR #38](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/38) **MERGED**, squash `24ae2dd93fed694980dab1fe68e55fabf4ba9ebe`; V7.34 PR#37 squash `5e744addf40040f074980323e38156ec88bba4de` baseline precedente. **Native KiCad9 run V7.35** [43257574206](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43257574206) **SUCCESS**, **6 unittest PASS**, native `pcbnew.FootprintLoad` TI DBV0005A 5-pad geometria + netlist/ERC reali prima/dopo a sette fogli; [cost/safety policy run 43257573711](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43257573711) **SUCCESS**, [artifact 13962610691](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43257574206/artifacts/13962610691). Sorgenti V7.35 verificati prima del merge: 134 componenti, 101 reti identiche, **pin-net delta zero**, solo `U6207` footprint assegnato, **missing 35→34**, ERC **36 errori/221 warning** invariati. Nessuna PCB completa/DRC o hardware.

**Nuovo CAD fisico V7.35:** `04_KiCad/Modulo_MCU_CODEC_V7.35_TPS3840_DBV5_VENDOR_LAND_REVIEW_NOT_FOR_FAB/` e master sette fogli `04_KiCad/Assemblaggio_RX_Power_V7.35_TPS3840_DBV5_VENDOR_LAND_REVIEW_NOT_FOR_FAB/`. `U6207 TPS3840PL30DBVR` riceve footprint reviewer `S3900E_TPS3840_DBV5_V735_HOLD:TI_DBV0005A_5PAD_REFLOW_REVIEW` in `04_KiCad/Librerie_Footprint_V7.35_TI_TPS3840_DBV5_HOLD/`. Manufacturer TI land 4214839/K, 08/2024: **cinque pad Cu 1.10×0.60mm**, x centri ±1.30mm, y −0.95/0/+0.95mm, numerazione 1/2/3 sinistra, 5/4 destra. Report `03_Verifiche/V7.35/RAPPORTO_TECNICO_TI_DBV5_V735.md`. È **review vendor geometry**, non DFM/solder-mask/layout approvato.

**Prossimo blocker V7.36:** C6231 100nF bypass VDD TPS3840 resta senza footprint/MPN; selezionare condensatore MLCC reale con curva Ceff @3.3V, classe dielettrico e land manufacturer 0402/0603 e test nativi. Verificare **U6207 push-pull OUTPUT sotto VPOR indeterminato**, compatibilità EN U6206 alle condizioni startup/brownout/guasto e sequenza firmware ALDO/RESET; non attribuire zero-error signoff. **15 cross-module OPEN/HOLD, SG48 HOLD, Y1 TCXO pin10 AFC/GND HOLD**, power protection/thermal/PLL. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Avanzamento storico radio PCB ~10% stimato, non aumentare per una sola footprint.

**Nota cronologica:** i checkpoint precedenti riportano V7.34 come stato più recente o PR #38 come bozza; sono storici. Questo blocco live aggiornato post-merge prevale.

---


## STATO LIVE PIÙ RECENTE — 12 novembre 2026 — **V7.34 INTEGRATA / SUPERVISORE U6207 + BYPASS C6231 / KIcad9 PASS**

**GitHub verificato:** [PR #37](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/37) **MERGED** (squash `5e744addf40040f074980323e38156ec88bba4de`). La V7.33 precedente resta nel repository come baseline storica. La nuova revisione è una **ECO CAD KiCad review/not-for-fab**, non PCB pronta per produzione.

**Verifiche finali vere sull'HEAD della PR V7.34:** [KiCad9 run 43256127182](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43256127182) **SUCCESS**, **37 test Python PASS**, export native 7 sheet netlist/ERC prima/dopo; [policy cost/safety run 43256126821](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43256126821) **SUCCESS**. Risultato: **132 → 134 componenti**, **100 → 101 reti**, **ERC 36 errori invariati**, **warning 218 → 221** (+3 endpoint/geometria da riesaminare, non soppressi), delta nodi pin-rete controllato solo a seguito ECO. I 132 componenti preesistenti restano identici, inclusi footprint e valori. Non è stata eseguita verifica DRC di una PCB completa né misurazione hardware.

**ECO concreta:** in MCU/CODEC V7.34 aggiunti `U6207 TPS3840PL30DBVR` supervisore 3.0V PL active-low push-pull, ingresso VDD pin2 su `3V3_CODEC_IO`, GND pin3, RESET_N pin1 su `CODEC_LDOIN_EN_SUPERVISED`, ora collegato a U6206 pin3 EN invece del 5V fisso. `C6231 100nF` decoupling tra `3V3_CODEC_IO` e GND per VDD supervisore, valore coerente con TI §7.3.1. MR/NC pin4 e CT pin5 aperti come consentito dal produttore. Nuova gerarchia `04_KiCad/Assemblaggio_RX_Power_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB/`, nuova MCU `04_KiCad/Modulo_MCU_CODEC_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB/`, report tecnico `03_Verifiche/V7.34/RAPPORTO_AUDIT_CONDENSATORI_MCU_V734.md`. **35 footprint mancanti** (33 baseline + U6207 + C6231); componenti vendor e land ancora HOLD.

**Blocker reale V7.35:** verificare al dettaglio `TPS3840PL30DBVR` pin-pad-footprint e C6231 MPN/derating; valutare EN U6206 per `VDD<VPOR` (uscita supervisore non definita), brownout, powerdown/retroalimentazione, soglie e ritardo worst case, firmware reset/ALDO; solo successivamente realizzare una ECO CAD mirata e prova KiCad9 netlist/ERC. **15 cross-domain OPEN/HOLD, SG48 HOLD, Y1 TCXO pin10 AFC/GND HOLD**, PLL, power protection, thermal HOLD. **NO FAB / NO GERBER / NO PCBWAY / NO TX.** Progresso globale PCB storicamente ~10% stimato (non inferire progresso da test/footprint). GitHub Actions limitate a policy e revisione tecnica mirata, non usare run duplicati inutili.

**Nota:** i checkpoint più vecchi sotto questo blocco riportano V7.34 OPEN/DRAFT perché sono fotografie storiche **precedenti** al merge; questo blocco sopra prevale.

---


## V7.34 LAVORO CAD REALE — 12 novembre 2026 — PR #37, sequenziatore TPS3840PL30 / native KiCad9 PASS / POLICY PASS

**Stato al checkpoint:** [PR #37](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/37) ancora **OPEN/DRAFT sul branch** `feature/v7.34-mcu-capacitor-inventory-hold`; `main` rimane V7.33 finché non si conferma il merge. Nuovi file: `04_KiCad/Modulo_MCU_CODEC_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB/`, nuovo master seven sheets `04_KiCad/Assemblaggio_RX_Power_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB/`, `03_Verifiche/V7.34/test_tps3840_native_v734.py` e workflow puntuale `.github/workflows/v734_tps3840_sequence_native.yml`.

**ECO:** aggiunto `U6207 TPS3840PL30DBVR` (supervisore supply `3V3_CODEC_IO`), output RESET_N a nuovo nodo `CODEC_LDOIN_EN_SUPERVISED` su pin 3 EN del LDO U6206. Non più EN del secondo LDO direttamente da 5V; U6205 EN resta 5V; tutti i componenti precedenti e le 15 interfacce cross-module restano intatti. U6207 MR/NC e CT deliberate NC, footprint vuoto in HOLD, non per fab; pending supervisor decoupling, package/land e tempistiche di brownout/ALDO.

**Prova CI nativa** [run 43254688982](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43254688982) **SUCCESS**: KiCad9 export netlist/ERC before-after 7 sheets, **37 unittest PASS**, 132→133 componenti, 100→101 reti, PIN-NET delta esattamente quattro nodi aggiunti e U6206 pin3 rimosso dal 5V; ERC **36 errori invariati**, warning **218→220** (nuovi endpoint off-grid); [artefatto 13959369775](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43254688982/artifacts/13959369775). **Costo/safety policy** prima FAIL [run 43254688716](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43254688716) per duplicate self-trigger nel nuovo workflow; **corretto** commit `571075f6`, [policy run 43254944933](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43254944933) SUCCESS. Nuovo run tecnico sul commit di fix workflow `43254944878` in attesa al momento dell'ultimo controllo; non considerarlo passato finché non termina.

**HOLD invariati:** PCB non completa, 33 missing footprint iniziali → **34** (supervisor ancora senza footprint), 15 interfacce aperte, SG48, Y1 TCXO pin10, thermal, PLL, AVDD/ALDO codec e hardware/reset. Nessuna simulazione start-up completa e nessuna scheda PCB/DRC. NO FAB / NO GERBER / NO PCBWAY / NO TX. Progresso complessivo storico prudenziale ~10%, non attribuire incremento sulla sola ECO.

**Next:** completare verifica run tecnico dopo fix workflow, valutare signoff 'REVIEW/HOLD' e merge quando policy+native verdi; su `main` aggiornare nuovamente checkpoint con vero merge SHA. Qualificare footprint MPN TI TPS3840PL30DBVR, C decoupling supervisor, pin4 MR floating validato vendor, schemi sequencing al brownout e reset reale MCU prima di hardware.

---


## AGGIORNAMENTO LAVORO APERTO V7.34 — 12 novembre 2026 — doppio EN LDO / SEQUENCING HOLD

[PR #37](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/37) resta **OPEN/DRAFT non integrata**. Verificati in sorgente KiCad V7.33 i pin fisici DBV per U6205/U6206 (TI TPS7A20 SBVS338H): entrambi hanno pin1 IN e pin3 EN su `5V_DIGITAL_FILTERED`, ma pin5 OUT su reti distinte `3V3_CODEC_IO` e `3V3_CODEC_LDOIN`. LDO con enable contemporaneo **non garantisce sequenza di uscita IOVDD prima/assieme a LDOIN** prescritta da TI SLAA492A tab3. Questo è un **rischio sequencing HOLD**, non un guasto confermato. Soluzione da scegliere con PGOOD/supervisore/abilitazione condizionata qualificata, incl. brownout e EN default, MA **nessuna ECO allo schema** ancora giustificata.

Nuovo test versione `03_Verifiche/V7.34/test_dual_ldo_enable_topology_v734.py`, protezione source-only delle reti ai pin LDO: **NON attestato eseguito in suite Python/CI**, benché i dati estratti siano stati ricontrollati indipendentemente. Rieseguito localmente `python3 -m unittest discover -s /mnt/data/v734_validation -p test_*.py -v`, 5 PASS del precedente `test_codec_power_sequence` (soltanto numerico). `kicad-cli` e `ngspice` non risultano installati nel runtime corrente, perciò nessuna nuova netlist/ERC/SPICE nativa: non attribuire PASS inesistenti. Nessun GitHub Actions avviato; PR non mergiata. **Prossimo:** qualificare schema e MPN del gate PGOOD/EN senza violare 15 interfacce HOLD; poi ECO CAD, CI mirata KiCad9 e merge solo se prove sufficienti. Main V7.33 baseline invariata (132 componenti, 100 reti, 33 footprint missing, ERC36/218, NO FAB / NO GERBER / NO PCBWAY / NO TX).

---


## LAVORO APERTO (NON INTEGRATO) — 12 novembre 2026 — V7.34 PR #37 DRAFT / CODEC STARTUP HOLD

**Branch in lavorazione:** `feature/v7.34-mcu-capacitor-inventory-hold`; [PR #37](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/37) **OPEN/DRAFT, non merge**, non sostituisce V7.33 su `main`. Rapporto `03_Verifiche/V7.34/RAPPORTO_AUDIT_CONDENSATORI_MCU_V734.md` e quattro script Python source/numerici. Audit: 30 condensatori MCU/CODEC e 60 etichette terminali, 33 pin codec U6202, reti MIC/FM (C6227 100nF/R6207 1k/C6228 4.7nF; C6229 1uF/R6208 1k/C6230 10nF), pullup R6206 4.7k IOVDD→LDO_SELECT, pull-down R6201 47k RESET→GND. Nessuna ECO al CAD.

**Nuovo rischio elettrico V7.34:** confronto con TI SLAA492A §3 mostra IOVDD `3V3_CODEC_IO` e LDOIN `3V3_CODEC_LDOIN` provengono da due LDO TPS7A2033 distinti (U6205/U6206), alimentati dallo stesso 5V filtrato ma senza timing di rampa dimostrato; con LDO_SELECT high D-LDO abilita ma A-LDO richiede successiva configurazione firmware. C6203+C6204 sul nodo AVDD = 10.1uF nominali, percorso di precarica interno ~10kΩ ⇒ tempo **5τ ~505ms** condizionale, NON ritardo obbligatorio/misura. TI prescrive RESET dopo validità IOVDD/DVDD e **1ms senza scritture dopo reset**; verificare sequencing, brownout e P1_R2 ALDO, evitare Schottky o modifiche CAD speculative. Si veda dettaglio con fonte TI nel rapporto V7.34.

**Test effettivamente eseguiti:** 5 test dello script `test_codec_power_sequence_v734.py` eseguiti localmente in Python `unittest` **PASS 5/5** (equazioni e limiti teorici); i tre script precedenti sono versionati ma **non dichiarati eseguiti in KiCad9 o in CI**. Parser indipendenti sul contenuto del file GitHub hanno verificato l'inventario dei condensatori e i pin nominati. Nessuna netlist/ERC nativa V7.34, nessun layout, hardware o SPICE, nessuna Actions a pagamento avviata. La baseline invariata rimane 132 comp, 100 reti, 33 footprint mancanti, ERC 36 errori/218 warning; 15 interfacce OPEN/HOLD, SG48 HOLD, Y1 pin10 HOLD, NO PCB completa/NO FAB/NO GERBER/NO TX. **Non mergiare la PR come se fosse una ECO CAD validata.**

---


## STATO LIVE PIÙ RECENTE — 11 novembre 2026 — **V7.33 INTEGRATA / 8 YAGEO 0402 MPN/PAD / KIcad9 PASS**

**GitHub reale:** [PR #36](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/36) **MERGED** squash `27d66c4ed8f23ce0a7fc0b608c052c30f25de0d0`. [CI nativa KiCad9 run 43061798023](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43061798023) **SUCCESS** con 10 unit test PASSED e `pcbnew.FootprintLoad` 2 pad geometrici + netlist/ERC prima/dopo; [policy cost/safety run 43061797916](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43061797916) **SUCCESS**. Artefatto nativo [#13872898509](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43061798023/artifacts/13872898509) ZIP scaricato e letto: `v733.yageo_native.json`, due netlist, due ERC reali. **132 componenti, 100 reti invariate, zero pin-net delta, esattamente 8 nuovi footprint**, missing **41→33**, ERC **36 errori / 218 warning** invariati (217 endpoint off-grid, 1 Y1 footprint warning).

**Nuovo CAD V7.33:** nuova MCU `04_KiCad/Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/` con sole 8 proprietà Footprint e 8 proprietà MPN hidden per R6201–R6208. Datasheet Yageo individuali codici: R6201 47k=`RC0402FR-0747KL`; R6202/R6203/R6204/R6206 4.7k=`RC0402FR-074K7L`; R6205 33Ω=`RC0402FR-0733RL`; R6207/R6208 1k=`RC0402FR-071KL`. Tutti 0402, 1%, 0.063W a70°C, Vmax rated 50V; MPN documentati in `03_Verifiche/V7.33/RAPPORTO_TECNICO_YAGEO_8R_V7.33.md`. Land Yageo reflow [Mounting v10, p4 Tab1](https://www.y-ic.es/datasheet/94/TC164-JR-072K7L.pdf), **pad 0.50×0.60mm, centri x±0.50mm, gap0.50mm, span1.50mm**. Footprint reviewer `04_KiCad/Librerie_Footprint_V7.33_YAGEO_0402_HOLD/S3900E_Yageo_Review.pretty/YAGEO_RC0402_REFLOW_VENDOR_CANDIDATE.kicad_mod`. Master 7-fogli `04_KiCad/Assemblaggio_RX_Power_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/` riusa AUX V7.31/RX e Y1 invariati. Valori originali delle resistenze invariati, sola qualifica geometrica/MPN candidata.

**Importante HOLD elettrico:** R6205 33Ω su clock 12.288MHz richiede segnale/impedenza, transienti e fault check: scenario teorico 3.3V su 33Ω se guasto =330mW, superiore a63mW nominali (non consumo in regime). R6207/R6208 per analogico richiedono valutazione rumore/range. Nessuna attribuzione di footprint implica signoff di potenza/sovratensione/reflow/assemblaggio; niente misure hardware.

**Ultima V7.32:** PR#35 MERGED squash `541e0389414a0e5581c94df52db9b104a82cc85e`, CI native 43060517528 PASS; X6201 SiTime 3225 quattro pad, 42→41 senza footprint, 132/100 nets, ERC36/218, zero delta. **Stato aggregato dopo V7.33: 33 senza footprint (resto prevalentemente condensatori C6201–C6230, FB6201, J100/J101); 36 errori ERC +218 warning; 15 interfacce cross-domain OPEN/HOLD; SG48 HOLD, Y1 TCXO pin10 AFC/GND irrisolto; power source/return/eFuse, thermal, PLL e signal integrity HOLD.**

**Next**: V7.34 investigare MPN e derating DC-bias dei 30 condensatori MCU, soprattutto 10µF vs rail 3.3V, 100nF decoupling e tensioni; non assegnare genericamente 0402 senza verifica capacità effettiva, DC bias, ripple; FB6201 MPN 600Ω@100MHz e J100/J101 housing pinout/footprint ancora TBD. Oppure risolvere errori ERC autentici solo con dati elettrici certi; non sopprimere i 26 dangling/6 power/4 input errori. Limitare Actions ai PR mirati con immagine KiCad9 (V7.30 cost policy). **NO PCB completa/NO global DRC, NO FAB / NO GERBER / NO PCBWAY / NO TX.** Progresso totale PCB storico ~10% stima non aumentata.

---


## STATO LIVE PIÙ RECENTE — 11 novembre 2026 — **V7.32 INTEGRATA / X6201 SiTime KIcad9 NATIVO PASS**

**VERIFICA GitHub live:** PR [#35](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/35) **MERGED** squash `541e0389414a0e5581c94df52db9b104a82cc85e`. CI tecnica [run 43060517528](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43060517528) **SUCCESS**, 10 test Python nativi KiCad9 PASS, e policy economica [run 43060517050](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43060517050) **SUCCESS**. Artefatto nativo [#13874140732](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43060517528/artifacts/13874140732) scaricato e ispezionato indipendentemente; presenti 2 netlist e 2 ERC KiCad9 reali + `v732.sitime_native.json`. Confronto: **132 componenti, 100 reti identiche, zero modifiche a nodi pin-rete; 42→41 footprint non assegnati; 36 errori ERC +218 warning esattamente invariati**, inclusi 217 `endpoint_off_grid` e una `footprint_link_issues` Y1. Solo footprint property X6201 cambiata.

**ECO V7.32 reale:** X6201 SiTime `SiT8008AI-22-33E-12.288000` 12.288MHz industrial 3.3V OE, **4 pad 3.2×2.5mm (3225)**, raccomandazione [datasheet SiTime rev A 1.11 p8](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/2092/SiT8008A.pdf) con pad 1.4×1.2mm centri 2.2×1.9mm. Simbolo pin 1 OE,2 GND,3 OUT,4 VDD coincide. Nuovo `04_KiCad/Librerie_Footprint_V7.32_SITIME_X6201_HOLD/S3900E_SiTime_Review.pretty/SiT8008AI_3225_VENDOR_CANDIDATE.kicad_mod` caricato realmente via `pcbnew.FootprintLoad` con quattro pad e geometrie verificate. Nuovo MCU `04_KiCad/Modulo_MCU_CODEC_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB/`; nuovo master 7-fogli `04_KiCad/Assemblaggio_RX_Power_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB/` riusa AUX V7.31 e RX invariati. **Solo candidato REVIEW/HOLD**, non DFM/PCB fab verificata. Report `03_Verifiche/V7.32/RAPPORTO_TECNICO_X6201_V7.32.md`.

**V7.31 realmente MERGED (checkpoint precedente OBSOLETO):** [PR #34](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/34) squash `aabe4122430e6581c958837061c5bf4c4ed9b5c7`, KiCad9 native [run 43057479410](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43057479410) **SUCCESS** (10 PASS), policy [43057479397](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43057479397) SUCCESS. Griglia AUX J100/J101 corretta, 132 componenti/100 reti, 0 pin-net delta, ERC 36/220→36/218 e offgrid219→217. Report nativo [artifact 13872031422](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43057479410/artifacts/13872031422) scaricato. **V7.30 Actions policy** PR#33 già integrata: 34 workflow historical triggers pertinenti/manuali + guard policy; tutte le prove tecniche conservate, non duplicare CI, utilizzare container KiCad preinstallato.

**Prossimo blocker V7.33 (scegliere ECO reale solo se è sicura):** investigare 217 `endpoint_off_grid` residui con evidenza nativa senza spostare arbitrariamente pin o unire circuiti; oppure qualificare le 41 impronte non attribuite con MPN/vendor; Y1 TXC `7N-12.800MBP-T` 10 pad pin10 **AFC/GND incerto → HOLD**. Nessuna simulazione/hardware test attribuibile a questa ECO; clock, power 13.8→5→3.3V, 36 errori ERC, 15 interfacce RX/MCU/AUX OPEN/HOLD, SG48 HOLD. **NO PCB completa/NO global DRC, NO FAB / NO GERBER / NO PCBWAY / NO TX.** Non aumentare percentuale progresso globale sulla base della sola attribuzione di footprint. CI GitHub Actions oltre quota a pagamento: 1 singolo job tecnico PR mirato quando necessario, mantenere policy. Non alterare billing.

---


**Aggiornato: 11 novembre 2026.** Sorgente di verità: repository GitHub **jd3485/Superstar3900-SMD-Evolution**, branch **main**; questo documento è un checkpoint, verificare sempre HEAD / PR / Actions in diretta.

**Prima di procedere in una nuova chat Work: LEGGERE ANCHE [AGENTS.md](../AGENTS.md)** (mandato, bootstrap, vincoli e procedura multi-revisione). Il file AGENTS è la configurazione stabile, questo è il registro da aggiornare ogni volta.

## Stato attuale 11 novembre 2026: V7.30 ACTIONS OTTIMIZZATE / V7.31 PR #34 ANCORA IN VERIFICA

**PR [#33](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/33) MERGED** squash `34bea592da038a28bad040ec41699e8b2a1a39d8`. **CI rapida [43054647792](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43054647792) SUCCESS** (primo tentativo 43054469057 failure veritiera, 12 exclusion reports missing, corretti). Audit su **34 workflow storici**, 30 PR paths-source-specific + manual e 4 solo manual; aggiunto 35esimo guard `.github/workflows/actions_policy_quick.yml` con `ci/workflow_policy/audit_workflow_costs.py`. **Nessuno step/job tecnico esistente modificato** nel diff della PR (solo eventi/paths/concurrency), test di sicurezza/regressione/ ERC/DRC non soppressi. No più V7.0 ad ogni merge KiCad: verifiche numeriche attivate dai loro input/manifest e manuali se necessarie; nuove ECO richiedono native CI individuale su PR. `AGENTS.md` include ora regola permanente. Nessuna modifica di budget/fatturazione.

**CAD V7.31 PR [#34](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/34) APERTA, NON INTEGRATA** branch `feature/v7.31-aux-connector-grid-kicad`, HEAD `09162edecccba0f933c05b31a02b0f5ca4686326`. Due veri connettori AUX J100/J101 off-grid in schemi nativi V7.29: versionati nuovi AUX e root, spostati **solo 2 symbol origins, 8 etichette di pin e relative proprietà**, 16 linee; tutte e 10 le coordinate terminali/pin su griglia 1,27mm. Sottofogli AUX, librerie e CAD V7.29 intatti; nessun collegamento cross-domain volontario. Audit statico del sorgente conferma 16 righe modificate **ma non è un test ERC/netlist**. L'integrazione richiede veri `kicad-cli` before/after 132 componenti/100 reti identiche, zero pin-net delta, 42 footprint mancanti, 36 errori invariati, warning 220→218 di cui offgrid219→217, 10 test V7.31.

**Actions PR #34:** controllo economico [43056454699](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43056454699) SUCCESS. Vecchio run nativo [43055752263](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43055752263) rimasto su installazione KiCad lenta, poi **CANCELLED** automaticamente dalla concurrency quando aggiornato workflow a timeout ridotto. Nuovo [43056454927](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43056454927) **in corso all'ultima consultazione**, timeout globale 12min/apt update max180s/install max360s. Non dichiarare V7.31 PASS prima del suo risultato effettivo; se fallisce correggere e ripetere solo native check necessari.

**Ricerca TCXO Y1:** [TXC 7N serie ufficiale 10-pad](https://txccrystal.com/images/pdf/7n.pdf) specifica pin10 **AFC oppure GND** dipendentemente dalla opzione; un'altra scheda `7N Rev1.03` reperita online presenta invece **package a 4 pad** e NON è usabile come pinmap dello specifico `7N-12.800MBP-T` con **10 pad** (confermato da scheda distributore DigiKey). Il suffisso `P` suggerisce TCXO non VCTCXO, ma non certifica se pin10 reale sia GND o NC, né autorizza collegarlo a massa. Y1 GND/AFC remains HOLD e l'ultimo footprint link errato rimane nel CAD corrente. Accertare disegno e pin funzione *della variante effettiva* prima di modificare la rete.

**Ultimo baseline CAD tecnicamente integrato:** V7.29 PR#32, 132 componenti/100 reti, **36 errori +220 warning ERC**, 219 endpoint offgrid, un footprint Y1 non riconosciuto, **42 senza footprint**, PCB unica assente. **15 interfacce RX/MCU/AUX OPEN/HOLD, SG48 HOLD, NO FAB / NO GERBER / NO PCBWAY / NO TX**. Sull'ambiente locale corrente non risultano `kicad-cli` e `ngspice`; non dichiarare prove native locali.

---

## STATO TECNICO CANONICO — 11 novembre 2026 — V7.29 INTEGRATA, CI PASS 14 TEST, ERC 36/220

**GitHub live:** [PR #32 V7.29](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/32) **MERGED**, squash `336883111b9817b7cb5d7472c7cd439db5b73f64`. [CI nativa #43024443162](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43024443162) **SUCCESS**, 14 test Python V7.29 PASS, KiCad9 `pcbnew.FootprintLoad` + originale/revisionata netlist/ERC, dati nel [run artifact #13856172598](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43024443162/artifacts/13856172598) ZIP effettivamente scaricato e JSON `v729.native_littelfuse_f200.json` letto. Dopo il merge anche il workflow base V7.0 [run #43024653345](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43024653345) è **SUCCESS**. Evitare duplicate CI perché Actions oltre quota è pagato dall'utente.

**Nuovo CAD V7.29:** root `04_KiCad/Assemblaggio_RX_Power_V7.29_F200_LITTELFUSE_REVIEW_NOT_FOR_FAB/`, AUX `04_KiCad/Gerarchico_Alimentazioni_V7.29_F200_LITTELFUSE_REVIEW_NOT_FOR_FAB/`; solo proprietà `Footprint` di **F200** cambiata dal vecchio `S3900E:LF_451_FOOTPRINT_NON_VALIDATO` inesistente al local review `S3900E_LF451_V729_HOLD:LF451_045101_5MRL_VENDOR_CANDIDATE`. **MPN esisteva già** nel valore schema, `Littelfuse 045101.5MRL`, Nano² 451 rapido 1,5A 125VDC/AC. Nuovo vero file `04_KiCad/Librerie_Footprint_V7.29_LITTELFUSE_451_HOLD/S3900E_LF451_Review.pretty/LF451_045101_5MRL_VENDOR_CANDIDATE.kicad_mod`; produttore raccomanda due pad rame, geometria KiCad9 nativa **span totale 6,86 mm, gap interno 2,95 mm**, profondità 3,15mm, larghezza pad calcolata1,955 mm≈1,96 mm nominale. 3 altri fogli AUX, sym-lib-table, MCU e RX originali invariati. Nessun link elettrico inventato.

**Native ERC V7.29:** 132 componenti,100 reti, **0 differenze in tutti i nodi pin-rete**, **42 footprint ancora senza assegnazione**; **36 errori ERC preesistenti invariati** e **220 warning** (221→220 per la sola impronta F200). Ripartizione 36 errors = 26 `label_dangling`, 6 `power_pin_not_driven`, 4 `pin_not_driven`. 220 warnings = 219 `endpoint_off_grid` + **1 `footprint_link_issues`**, esclusivamente **Y1 TXC 7N-12.800MBP-T 12,8MHz TCXO** con `S3900E:TXC_7N_7x5_10pad_UNVALIDATED`. Per TXC datasheet generico 7N serie 10pad pin10 **AFC oppure GND** a seconda variante, tuttora indeterminata. Etichetta `TCXO_PIN10_AFC_OR_GND_TBD` da lasciare aperta, nessuna massa arbitraria. Acquisire scheda tecnica TXC della variante esatta / vendor pin10 e land per validare Y1; NON assegnare footprint solo per togliere l'ultimo warning.

**F200 safety warning:** Littelfuse 451 1.5A ha Rcold0,063Ω, I²t nominale0,853A²s, derating corrente continua consigliato **25%** → soglia preliminare1,125 A a25°C *prima* del derating termico: effettivo assorbimento 13,8V, spunto, fusione/sovracorrente, potere d'interruzione e coordinamento eFuse **NON validati**. Il nuovo footprint è **review-only**, non certifica l'adeguatezza del fusibile. Anche L100 Bourns e U1/MCU/codec/LDO candidate review restano HOLD termica/DFM e nessuna PCB completa.

**Revisioni integrate in questa sessione, in ordine:** [V7.26 PR #29](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/29) CI 43019926260 PASS 12 test, 32 simboli AUX/MCU/RX con collisioni R/C risolte e 117 warning `lib_symbol_issues` eliminati; [V7.27 PR #30](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/30) CI 43022065783 PASS 14 test, U1 TI LMX2572 package RHA40+EP41 e 9 paste apertures, warning −1; [V7.28 PR #31](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/31) CI 43023404615 PASS 13 test, Bourns SRP1038A-150M L100 15µH con scan ripple +Isat 25°C, warning −1; [V7.29 PR #32](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/32) 14 PASS, fuse F200 manufacturer footprint, warning −1. Totale **53 nuovi test specifici PASS** su quattro CI mirate, altre regressioni storiche **344 PASS in V7.25** e V7.0 main baseline PASS (non inventare rerun 344 su ogni nuova versione). ERC **36 errors sempre**; avvisi 340→220 (**120 risolti**) senza waiver.

**Next V7.30:** qualificare TXC 7N exact Y1 pin10 AFC/GND, versione CMOS/abilitazione, dimensioni 10pad land pattern e clock PLL; se non dimostrabile, mantenere Y1 HOLD. Valutare correzioni `endpoint_off_grid` con veri diffs di pin/net/label + KiCad9 ERC; non applicare snap indiscriminato ai 219. Investigare sorgenti di power ed eFuse return senza unire `EFUSE_RTN` e `GND_MAIN`, protezioni e temperatura; solo dopo PCB unica. **15 interfacce RX/MCU/AUX OPEN/HOLD, SG48 HOLD, 42 footprint senza assegnazione, niente PCB unica, nessun DRC globale, avanzamento ~10% stima storica non aggiornata, NO FAB / NO GERBER / NO PCBWAY / NO TX.** [Issue #27](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/27) aggiornata.

---

## STATO ATTIVO — 11 novembre 2026 — V7.28 MERGED, CI NATIVA PASS, ERC 36/221

**Verifica live GitHub:** [PR #31](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/31) **MERGED** squash `2c1d7096c11cb212b04d16a3d2f194aac477ac28`. [Actions 43023404615](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43023404615) **SUCCESS** con vero `kicad-cli` e Python PCBNEW KiCad9, **13 test V7.28 PASS**. Artefatto [13855897579](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43023404615/artifacts/13855897579) scaricato e letto: `v728.native_bourns_review.json`, origin/revised `kicad-cli` netlist/ERC. [V7.0 main baseline run 43023649771](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43023649771) **success** dopo merge, workflow baseline trigger su CAD come previsto. Ultimo checkpoint main precedente `34a5f160ab00fb1b2e2e76d403e2d708964aedf4`.

**CAD L100 reale:** nuove versioni `04_KiCad/Gerarchico_Alimentazioni_V7.28_L100_BOURNS_REVIEW_NOT_FOR_FAB/` e `04_KiCad/Assemblaggio_RX_Power_V7.28_L100_BOURNS_REVIEW_NOT_FOR_FAB/`: soltanto riferimento e valore di **L100** modificati, scegliendo **Bourns SRP1038A-150M** 15µH e footprint locale REVIEW `04_KiCad/Librerie_Footprint_V7.28_BOURNS_L100_HOLD/S3900E_Bourns_Review.pretty/SRP1038A_150M_BOURNS_VENDOR_CANDIDATE.kicad_mod`. MPN Bourns: 15µH±20%, DCR(max)45mΩ, Isat10A @25°C, Irms6,25A @25°C. Land pattern consigliato **due pad da 4,10×3,50mm** centro x±4,75mm (span esterno13,6mm, gap interno5,4mm); parser `pcbnew.FootprintLoad` verificato con coordinate/layer. Altri AUX e simbologia V7.26 byte identici. **Nessuna PCB prodotta, nessun DRC globale**.

**Proof native KiCad9 V7.28:** 132 componenti, 100 reti, **zero nodi elettrici modificati**; solo L100 valore+footprint, **42 footprint ancora mancanti**, ERC **36 errori invariati** e avvisi **222→221** esattamente `footprint_link_issues` **3→2** (solo L100). F200 e Y1 rimangono **UNVALIDATED** con footprint S3900E non disponibile. Remaining **221 warning** = 219 `endpoint_off_grid` + 2 `footprint_link_issues`. **36 errors** = 26 `label_dangling` HOLD, 6 `power_pin_not_driven`, 4 `pin_not_driven` PLL. Non ridurre artificialmente.

**Schermatura di corrente L100 (teorica, non misura):** TI TPS54202 buck 5V, Iout nominale massimo 2A, Vin 4.5–28V, fSW nominale min390kHz; sul caso limite esemplificativo Vin28V, Vout5.077V reale da divider, Lmin=12µH, fmin390kHz, `ripple=0.888A p-p`, `Ipeak≈2.444A`, perdita avvolgimento stimata `0.183W` con 45mΩ. Sono screening, non qualificano termica reale, saturazione al caldo, EMC, startup, loop, cavi, assembly, carichi e fonte/ritorno 13,8V.

**Precedenti integrate in questa stessa sessione:** V7.26 [PR #29](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/29) native CI 43019926260 PASS, 32 simboli collision-free AUX/MCU/RX, 6 R/C renames, warning ERC 340→223 senza cambiare reti; V7.27 [PR #30](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/30) CI 43022065783 PASS, TI LMX2572 RHA0040H U1 40 pad+EP41 native, 9 finestre pasta, warning223→222. Candidati reviewer-only, **non approvati per fabbricazione**. I 344 test storici V7.25 PASS non sono stati nuovamente eseguiti nelle tre CI mirate successive; nuovi test **12+14+13=39 PASS** in 3 run, inoltre il workflow V7.0 baseline main ha success.

**Next V7.29:** investigare **F200 fuse** e **Y1 TCXO** manufacturer package/pinout e fattibilità footprint (nessun MPN qualified, non inventare), e classificare per foglio i **219 `endpoint_off_grid`** senza snap indiscriminato; ogni spostamento dovrà avere differenziale vero pin-net e ERC nativi. Power 13,8V→eFuse→buck5V→3,3V e 15 interfacce cross module ancora HOLD, SG48 HOLD, nessuna PCB unica. Avanzamento totale ~10% **stima storica** invariata, 42 impronte mancanti. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**

---

## STATO ATTIVO 11 novembre 2026 — **V7.27 MERGED / 36 errori + 222 avvisi ERC**

**Main tecnico integrato corrente:** [PR #30](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/30) **MERGED**, squash `18c027c3073a2442bb3c5979382e13c6a904adaf`, su V7.26 [PR #29](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/29) squash `564e3c4ad2caebec053d000659edb3bec453c6d4`. **Native KiCad9 CI V7.27 [run #43022065783](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43022065783) SUCCESS**: 14 unit test PASS, tutti gli step KiCad netlist/ERC + `pcbnew.FootprintLoad` PASS. [Artefatto #13854479601](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43022065783/artifacts/13854479601) ZIP effettivamente scaricato e letto: `v727.native_rha41_review.json` conferma **132 componenti, 100 reti, 0 nodi di netlist modificati, 42 footprint ancora mancanti**, U1 unico componente con modifica di `Footprint`, **36 errori invariati, warning **223→222** esclusivamente `footprint_link_issues` 4→3. No waiver.

**CAD V7.27 nuovo e vero:** `04_KiCad/Librerie_Footprint_V7.27_TI_RHA_HOLD/S3900E_TI_RHA_Review.pretty/LMX2572_RHA0040H_VENDOR_CANDIDATE.kicad_mod` (TI LMX2572 SNAS740B RHA0040H 6x6mm): 40 pad perimetrali 0,60×0,25mm/pitch0,50 + EP41 rame 4,50×4,50mm e **9 aperture F.Paste separate 1,26×1,26mm** a interasse 1,46mm (~70,56% nominale secondo esempio TI). `pcbnew` 9.0.8+dfsg-1 ha caricato veri 41 copper pads/9 paste apertures, tutti numeri, layer e quote superati. Nuovi AUX `04_KiCad/Gerarchico_Alimentazioni_V7.27_PLL_RHA41_REVIEW_NOT_FOR_FAB` e root `04_KiCad/Assemblaggio_RX_Power_V7.27_PLL_RHA41_REVIEW_NOT_FOR_FAB`; una sola modifica proprietà footprint di **U1 LMX2572**, ora in libreria locale `S3900E_TI_RHA_V727_HOLD`, senza toccare né pin DAP41 già presente su GND_MAIN né altre masse, etichette o fili. Nulla di questo costituisce qualifica assemblaggio/stencil o autorizzazione produttiva.

**ERC nativo aggiornato: 36 errori** = 26 `label_dangling`, 6 `power_pin_not_driven`, 4 `pin_not_driven`. **222 avvisi** = 219 `endpoint_off_grid` + **3 `footprint_link_issues`**. Tre refs rimaste: **F200/Y1** libreria `S3900E` footprint unvalidated; **L100** `Inductor_SMD:L_10.0x10.0_H5.0` inesistente nella libreria KiCad9, componente attuale `15uH / 3.5A` ma **MPN non scelto**, dati Isat/Irms/termica e land pattern vendor assenti. Non correggere selezionando footprint a caso per rendere ERC verde. **V7.28 prossimo:** MPN + calcolo reale dell'induttore L100 e modelli power, poi eventuale CAD footprint, senza forzare interfacce non qualificate; analizzare 219 off-grid con netlist diff per ogni trasformazione, senza snap automatico indiscriminato. Possibile revisionare i 10 pin undriven soltanto con fonte/ritorno reali.

**Vincoli invariati:** 15 cross-module RX/MCU/AUX **OPEN/HOLD**, SG48 HOLD, 42 componenti senza footprint, F200/Y1 non qualificati, PCB unica non esiste e non è stata fatta DRC globale. Progresso totale ~10% *stima storica* non aggiornata per audit. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Actions sbloccato direttamente dall'utente e oltre quota fatturabile: CI V7.27 una sola `pull_request`, non duplicare azioni costose. I 344 Python del CI V7.25 restano evidenza storica, non sono stati rieseguiti integralmente nella V7.27: 12 V7.26 e 14 V7.27 nuovi PASS.

---

## STATO ATTIVO — 11 novembre 2026, V7.26 INTEGRATA: 117 avvisi simboli eliminati realmente

**GitHub live:** [PR #29](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/29) **MERGED** squash `564e3c4ad2caebec053d000659edb3bec453c6d4`. [GitHub Actions 43019926260](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43019926260) **SUCCESS**, un unico runner KiCad9 di confronto nativo V7.25→V7.26, **12 test V7.26 PASS**, nessuna regressione elettrica verificata: **132 componenti, 100 reti, delta zero nodi pin/rete, 42 footprint non assegnati**. **36 errori ERC** identici prima/dopo; avvisi **340→223**, esattamente i **117 `lib_symbol_issues`** eliminati, senza soppressione regole/waiver. [Artefatto reale 13854287534](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43019926260/artifacts/13854287534), `v726.native_library_parity.json` letto dal ZIP (conferma 36/223 e `lib_symbol_warnings_new:0`).

**Reale CAD versione V7.26:** `04_KiCad/Librerie_Simboli_V7.26_UNIFIED_NOT_FOR_FAB/S3900E.kicad_sym` con **32 simboli univoci embedded** AUX/MCU/RX; 3 copie controllate dei fogli AUX e 6 nomi R/C distinti (`R_EFUSE,C_EFUSE,R_BUCK,C_BUCK,R_PLL,C_PLL`) mantenendo pin e fili intatti; nuovo root `04_KiCad/Assemblaggio_RX_Power_V7.26_UNIFIED_SYMBOL_LIB_NOT_FOR_FAB/`, `sym-lib-table` completo. Tutti i fogli storici V7.25 intatti e disponibili. Una CI mirata su `pull_request` soltanto per limitare costi Actions. **Non dichiarare che i 344 vecchi test sono stati rieseguiti V7.26**: restano run verde V7.25, mentre 12 nuovi test specifici sono PASS.

**Residuo ERC V7.26 (nativo):** 36 errori = 26 `label_dangling`, 6 `power_pin_not_driven`, 4 `pin_not_driven`; 223 avvisi = **219 `endpoint_off_grid` + 4 `footprint_link_issues`**. Quattro link non validi esatti: F200 `S3900E:` review, Y1 `S3900E:` review (entrambi HOLD/UNVALIDATED), L100 `Inductor_SMD:L_10.0x10.0_H5.0` assente, PLL U1 `Package_DFN_QFN:VQFN-40-1EP_6x6mm_P0.5mm_EP4.35x4.35mm` assente. Da **non** far sparire usando false footprint.

**NEXT V7.27:** valutare MPN vendor **TI LMX2572 RHA0040H VQFN40 + DAP41**, il cui pad centrale 41 compare già nella netlist U1 sul GND_MAIN con 10 GND periferici (da verificare pinmap/datasheet e RF power); creare solo un'impronta `HOLD` qualificata geometrica secondo land/stencil TI, verificare con `pcbnew.FootprintLoad` nativo e, se sicuro, sostituire l'alias KiCad U1 inesistente su nuovo AUX/root **solo reviewer-only**, assicurando netlist invariata. Il datasheet TI SNAS740B (2019) riferisce pad DAP come RF ground e prescrive thermal pad saldato con vias; esempio package RHA0040H espone **41 pad**, centrale **4,5 mm**, land periferici 0,60 × 0,25 mm passo 0,50, stencil 9 aperture da 1,26 mm con ~70% copertura. La guida pin functions TI ufficiale assegna **pin 11 VccCP, pin 21 VccBUF** (non basarsi su descrizioni image/OCR ambigue). L100 15uH/3.5A senza MPN e F200/Y1 restano HOLD, non assegnare footprint inventati. Evitare DRC senza PCB unica.

**Vincoli:** 15 cross-module RX/MCU/AUX OPEN/HOLD, SG48 HOLD, nessuna PCB unificata, no Gerber, PCBWAY, TX; 42 footprint mancanti, F200/Y1 package non approvati, power source/return 13,8→5→3,3V non dimostrato. Progresso storico ~10% stima invariata. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

---

## STATO CORRENTE — 11 novembre 2026 — V7.25 **MERGED**, 344 TEST PASS (consultare prima delle sezioni storiche)

Ultimo `main` revisionato in questa sessione: [V7.25 PR #28 merged](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/28), commit squash **`a1924b2b525de27b4e677b992abd702741922781`**. Le precedenti sezioni su V7.25 come *prossima* e su 48 footprint mancanti sono **storiche** e non devono prevalere sul presente checkpoint. V7.22 PR #23, V7.23 PR #25 (real `pcbnew.FootprintLoad`), V7.24 PR #26 (ottimizzazione trigger CI a consumo) sono già MERGED.

**Verifica live KiCad 9 e Python:** [Actions run #43012099267 — success](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43012099267) su PR #28, runner realmente eseguito, **344 Python PASS, 0 FAIL/0 SKIP, 23 gruppi** (10 nuovi V7.25 + 334 storici), controlli `kicad-cli` ERC/netlist pre/post, `pcbnew.FootprintLoad` tre vendor lib da V7.23, ngspice e regressioni. Artefatto verificato localmente: [#13850348324](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43012099267/artifacts/13850348324) con `v725.six_footprints.json`, due netlist e due ERC report nativi.

**CAD integrato V7.25, 7 fogli:** `04_KiCad/Modulo_MCU_CODEC_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` associa SOLO U6201 STM32G474RET6 LQFP64 ST, U6202 TLV320AIC3204 RHB33 TI e quattro U6203–U6206 TPS7A2033PDBVR DBV5 TI alle tre librerie review con nickname `_HOLD`; root `04_KiCad/Assemblaggio_RX_Power_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB/`. MPN ↔ pin simbolo ↔ pad e geometrie esempio vendor ST/TI collegate *per revisione nativa*, **non** approvate per assemblaggio/stencil/produzione. Lo schema di revisione passa da **48 a 42 footprint mancanti** (90/132 campi compilati), **senza cambiare alcun pin o nodo elettrico**, 132 componenti, 100 reti, ERC **36 errori/340 avvisi** prima/dopo. Termica, mask/paste di fabbricazione, F200/Y1, power source/return e PCB integrata rimangono HOLD.

**Issue ERC da trattare prossimo:** [#27 — triage ERP nativo](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/27): 26 `label_dangling` errors (NON unire interfacce in HOLD), 6 `power_pin_not_driven` errors, 4 `pin_not_driven` errors; 219 `endpoint_off_grid` warnings, 117 `lib_symbol_issues` warnings, 4 `footprint_link_issues` warnings. Dieci pin da investigare U6203 IN/GND, AUX U200 IN/RTN, AUX U2 IN/GND, PLL U1 SYNC/SysRefReq/RampClk/RampDir. Prossima revisione sostanziale **V7.26**: qualificare libreria `S3900E` coerente con simboli embedded, controllare conflitti per pin/MPN e librerie on-disk, ridurre i warning librerie senza waiver, senza inventare connessioni elettriche. Non assegnare 42 impronte non giustificate. Lato energia, 15 interfacce OPEN/HOLD e source/return non dimostrati.

**Blocco V7.26 — collisione simboli già riscontrata senza alterare CAD:** i fogli AUX `01_EFUSE_AUX`, `02_BUCK_5V`, `03_PLL_LDO_TCXO` incorporano più definizioni con il medesimo id `S3900E:R` e `S3900E:C`, ma **non byte-identiche** (R: 648, 761, 753 caratteri; C: 749, 863, 855). La `sym-lib-table` root punta alla libreria RX di prova che manca dei simboli MCU/AUX. **Non aggregare automaticamente le definizioni**, non scegliere arbitrariamente una variante. Prima differenziare nomi solo quando la semantica pin/grafica diverge, poi creare libreria versionata e fare KiCad9 netlist/ERC differenziale. [Issue #27 aggiornato](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/27). Nessuna correzione elettrica V7.26 introdotta da questo audit.

**Budget:** GitHub Actions sbloccato direttamente dall'utente; ora i minuti extra sono a pagamento. CI V7.25 su **pull_request soltanto**, no doppio push+PR. Evitare test ridondanti o runner a vuoto; non modificare billing senza esplicito ordine.

**NON pronto alla produzione:** 15 interfacce cross-module RX/MCU/AUX OPEN/HOLD, SG48 HOLD, 42 footprint senza assegnazione, F200/Y1 non validati, ERC 36/340, nessun layout PCB globale o DRC completo, avance globale storica ~10% stimata NON cambiata. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**

---

## Verifica V7.25 — lettura nativa ERC storica e triage rigoroso, 11 novembre 2026 (nessun nuovo CAD integrato)

**Artefatto del run verde V7.22** [13849074958](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515/artifacts/13849074958) estratto in ambiente di analisi senza consumo di altri minuti Actions. Il file KiCad9 originale `v722.revised.erc.rpt` (52.064 bytes) contiene esattamente **376 messaggi: 36 errori e 340 warning**. La distribuzione letta direttamente (non ricostruita da chat precedente) è: **26 `label_dangling` errors**, **6 `power_pin_not_driven` errors**, **4 `pin_not_driven` errors**, **219 `endpoint_off_grid` warnings**, **117 `lib_symbol_issues` warnings**, **4 `footprint_link_issues` warnings**.

**Dieci pin da investigare con fonti reali prima di ogni modifica elettrica:**
- MCU U6203 **IN:1, GND:2** (nessuna sorgente/return riconosciuta, 2 ERC).
- AUX eFuse U200 **IN:1, RTN:8** (2 ERC), source/return 13.8V/EFUSE_RTN OPEN/HOLD.
- AUX U2 LDO **IN:1, GND:2** (2 ERC), source/return OPEN/HOLD.
- AUX PLL U1 **SYNC:5, SysRefReq:28, RampClk:30, RampDir:32** (4 ERC, input senza driver).

**117 warning librerie** includono simboli locali `S3900E` non trovati nella libreria dichiarata per il root (per esempio `CONN_2_EXT_DRAFT`, `HOST_SPI_6PIN_DRAFT`, `F/C/D/R`): `sym-lib-table` del root punta a RX test library insufficiente. Prossimo ECO plausibile: costruire **libreria S3900E versionata completa** da simboli embedded reali, deduplicare verificando pin/MPN, retarget root **solo dopo** aver provato che netlist non cambia; non inventare simboli o ottimizzare via waiver. **219 off-grid warnings** vanno affrontati senza snap indiscriminato; **26 dangling labels** rappresentano potenziali interfacce non qualificate, non ricollegare TX. [Issue #27 con tabella e blocker puntuali](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/27).

**GATE:** niente nuova PR V7.25 né modifica elettrica per questi problemi finché non è dimostrata una correzione sicura. Root V7.22 invariato in V7.23/V7.24. Ultimo CI V7.0 [43011495583](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43011495583) **SUCCESS**, e successivo commit solo checkpoint precedente `cac509458f743655c5a503067b98bced74f78c77` **non ha prodotto Actions runs**, confermando il risparmio di workflow V7.24. Uso Actions ora a pagamento: evitare runner inutili.

**Sicurezza invariata:** 15 interfacce OPEN/HOLD, 48 footprint ancora mancanti, 36/340 ERC non corretti, SG48 HOLD, nessuna PCB unica/DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

---

## Sessione 11 novembre 2026 ore 12:20 CET — **V7.23 e V7.24 INTEGRATE, V7.25 PROSSIMA**

**Verifica indipendente da GitHub live:** `main` dopo [PR #25](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/25) squash `8e46b26bb488fb1484ee9cc2b1c366b91badfb80` e [PR #26](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/26) squash `9308b710db8a13071de60ad9f9b93fed3c414b89`, entrambe **MERGED**. Base V7.22 precedente [PR #23](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23), squash `e6b04082e4268cccc8338127824a0a2e0341ad91`, [run 42997229515 attempt 2 PASS](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515) **334 Python PASS, KiCad9/ERC/netlist root prima/dopo 36 errori + 340 warning, 132 comp/100 reti, U6202 EP33 local GND**.

### V7.23: nuovo controllo vero KiCad9 sulle tre librerie

- Script `03_Verifiche/V7.23/audit_native_footprints_v723.py` usa **`pcbnew.FootprintLoad`** del KiCad nativo, NON regex per la verifica finale. Compara coordinate, dimensioni, pad numerati, layer rame F.Cu, F.Mask, F.Paste e paste-only. **102 pad elettrici numerati in totale (ST LQFP64 64 + codec TI RHB 33 + TI DBV 5)**; TI codec EP33 ha **quattro pad separati di pasta non-rame** 1,49×1,49 mm. Suite di review, nessun export né PCB di prova salvata.
- Primo [run 43010894472](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43010894472) **failure INSTALL** perché l'Ubuntu runner non ha `python3-kicad` come pacchetto separato: nessun test CAD in quel run. Corretto workflow rimuovendo il pacchetto fittizio (binding `pcbnew` installato insieme a `kicad`).
- Successivo [run 43011010863](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43011010863) **SUCCESS**, KiCad **9.0.8+dfsg-1**, step native footprint load **success**, artefatto [13849469820](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43011010863/artifacts/13849469820) `v723.native_footprint_load.json`. Letto log CI: ST64, TI RHB33+4 paste-only, TI DBV5, geometry/layers veri tutti PASS. **Non si sono assegnati footprint a U6201–U6206.** Il gate dimostra caricamento nativo, non qualifica stencil/assemblaggio/DRC globale.
- La PR #25 è stata verificata **e integrata**, quindi i tre footprint candidati restano nell'albero root, ma sempre `HOLD/NO ASSIGNMENT`.

### V7.24: controllo preventivo dei costi Actions

- **L'utente ha sbloccato Actions a pagamento**. Nessuna modifica di billing o budget effettuata dall'agente. Il vecchio workflow `.github/workflows/verifica_v70.yml` partiva su ogni push in `main`, anche solo aggiornamenti checkpoint. [PR #26](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/26) limitata ai `paths` tecnici (`ci/**`, `03_Verifiche/V6.9/**`, `03_Verifiche/V7.0/**`, `04_KiCad/**`, stesso workflow), mantenendo `workflow_dispatch` e tutti gli step SHA256/tag v7.0 + regressioni numeriche invariati. Nessuna modifica CAD o elettrica V7.24, nessun test indebolito **dentro** il workflow. Per modifiche solo a `00_Gestione_Progetto` non deve partire il runner V7.0. V7.24 merge squash `9308b710db8a13071de60ad9f9b93fed3c414b89`; [baseline run 43011495583](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43011495583) **in coda all'ultima consultazione** — verificarne il risultato in diretta, non dichiararlo verde se non completato.

### Stato reale e prossimo passo V7.25

**48 footprint ancora mancanti in schema** nonostante le nuove librerie, F200/Y1 presenti ma UNVALIDATED. **15 interfacce cross-domain OPEN/HOLD**, `EFUSE_RTN` non unire a `GND_MAIN`, SG48 HOLD. Root 7 fogli/132 comp/100 reti, **ERC 36 errori / 340 warning preesistenti**, nessuna PCB unica completata, nessun DRC globale possibile su PCB inesistente, avanzamento ~10% stima storica invariata. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

**V7.25 priorità:** confrontare pin-to-pad/vendor per U6201/U6202/U6203–U6206 anche contro netlist native, verificare stencil e assembly DFM, fare vera correzione KiCad se emerge un difetto con prova. In parallelo analizzare/reportare e poi ridurre *difetti ERC reali* senza PWR_FLAG fittizi, short fra domini o waiver; esaminare source/return 13,8V→5V→3,3V e termiche LDO; soltanto dopo assegnazione controllata di footprint e progetto PCB unitario. Usare **una CI mirata per revisione** e monitorare costo GitHub Actions.

---

## Aggiornamento 11 novembre 2026 ore 12:09 CET — **V7.22 INTEGRATA, CI VERDE, passare a V7.23**

**Fonte live verifica GitHub:** `main` revisione ingegneristica V7.22 integrata con squash [PR #23](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23), commit **`e6b04082e4268cccc8338127824a0a2e0341ad91`**. La PR #23 è **MERGED**, non più aperta. Tutti i paragrafi sotto questa sezione che dicono `PR #23 NON MERGIATA` o `CI bloccata` sono **storico superato**, NON stato corrente.

**RUN NATIVA realmente riuscita:** [GitHub Actions 42997229515, tentativo 2, 11 Nov 11:09 UTC](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515) `success`, runner attivo, KiCad9 + ngspice, esportazione netlist/ ERC root pre/post, **334 test Python PASS, 0 FAIL/0 SKIP**, 22 gruppi (26 V7.22 +308 storici). Artefatto reale [13849074958](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515/artifacts/13849074958), `v722.native_pin_net_diff.json` letto e confrontato in ZIP, conferma **132 componenti /100 reti**, un solo nodo nuovo `/MCU_CODEC_AFE_existing_V2_1_UNQUALIFIED/GND, U6202, pin 33`, zero nodi rimossi. ERC **36 errori/340 warning** prima **e dopo** (non pulito, nessun peggioramento). I 3 footprint locali da vendor ST/TI sono verificati con 16 test statici di geometria (oltre ai test della ECO), registrati in fp-lib-table ma **NON assegnati**; **48 footprint ancora mancanti**. `NO FAB` sempre attivo.

**Blocco costi Actions risolto dall'utente:** budget Actions sbloccato; il runner hosted è tornato attivo e il workflow ha avuto successo. [Issue #24](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/24) deve essere chiusa come risolta (quota pregressa 2.000/2.000 + budget $0, poi aumento approvato direttamente dall'utente). Evitare lanci ripetuti o duplicati: i nuovi minuti oltre quota sono **a pagamento**, minimizzare workflow e preferire una sola CI mirata per revisione. Non modificare billing/budget autonomamente.

**Priorità V7.23:** verificare in KiCad9 parsing eseguibile dei 3 `.kicad_mod` (non basta regex), rivedere pad/mask/paste/courtyard con datasheet e vincoli IPC, qualificare MPN-symbol-pad-footprint per U6201/U6202/U6203–U6206 prima di eventuale assegnazione, mantenendo hold qualora un elemento non dimostrato. Poi source/return della catena 13,8V→5V→3,3V ed ERC nativo. Non generare PCB dimostrativa chiamandola radio completa.

**VINCOLI:** 15 interfacce cross-module **OPEN/HOLD**, SG48 HOLD, nessun corto GND dei domini o EFUSE_RTN, nessun PWR_FLAG arbitrario; root **7 fogli, 132 comp,100 reti, ERC 36/340**, **48 footprint senza assegnazione**, F200/Y1 unvalidated, nessuna PCB unificata; ~10% stima storica immutata. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**

---

## Aggiornamento confermato — quota GitHub Actions esaurita (11 novembre 2026)

**CAUSA BLOCKER IDENTIFICATA DALL'UTENTE:** screenshot originale dell'avviso ufficiale GitHub `jd3485`: **2.000 / 2.000 minuti GitHub Actions consumati, 100% del ciclo**. Reset comunicato per **1 dicembre 2026**. GitHub dichiara che oltre quota la fatturazione è possibile salvo **budget Actions impostato a $0**, caso in cui le esecuzioni vengono bloccate fino al reset. **Non è stato letto direttamente il valore budget $0 dell'account**: non inventare impostazioni; indisponibilità dei runner con `runner_id=0` su workflow nuovi e vecchi coerente con esaurimento quota. [Issue #24 aggiornata](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/24).

**Regola operativa NO COSTI:** non modificare budget/fatturazione, non acquistare minuti, non cambiare visibilità del repo o bypassare protezione branch. Non generare workflow falliti a ripetizione prima del reset senza ragione. **Sviluppo V7.22 può proseguire su PR #23** con verifiche native offline/locali a costo zero se l'ambiente dispone di KiCad9/ngspice; per contro in questa sessione `kicad-cli` e `ngspice` risultano **assenti** e `apt-get update` ha raggiunto timeout (~18s), quindi **nessuna verifica KiCad9 locale è stata eseguita**. I test Python V7.22 non sono stati eseguiti con netlist ERC reali. Non fare merge della PR tecnica senza gate nativi; dopo reset 1 dicembre rieseguire interamente il CI e registrare ID/run/esiti effettivi.

**Stato immutato:** PR #23 aperta, branch HEAD `9aedec44e1fe10bdc61a3a55c75903263a98cbae`, tre nuovi footprint candidati ST/TI non assegnati; 26 test nuovi + 308 storici **334 previsti NON ESEGUITI**; 48 footprint root mancanti, ERC baseline V7.21 36/340, 15 interfacce OPEN/HOLD, PCB unica assente. **NO FAB / NO GERBER / NO PCBWAY / NO TX; SG48 HOLD.**

## Sessione 11 novembre 2026 — **V7.22 PR #23 NON MERGIATA**: ECO codec + tre librerie vendor, GitHub Actions runner BLOCCATO

**Verifica live:** `main` base tecnico integrato **V7.21 PR #21** (CI [42987421253](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42987421253), 308 Python PASS in KiCad9); PR #22 solo protocollo; `main` prima di questa continuazione `b805a333e23e78d44e0c357cf43a66ae6cdb3646` (checkpoint precedente). **Non dichiarare V7.22 integrata**.

**Ramo in corso (NON MERGED):** [PR #23](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23), branch `feature/v7.22-codec-ep33-ground-eco`, HEAD corrente `9aedec44e1fe10bdc61a3a55c75903263a98cbae`.

### Modifiche CAD reali e conservazione NO FAB

- Foglio KiCad nativo versionato `04_KiCad/Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`: simbolo U6202 TLV320AIC3204 RHB con **pad termico fisico n. 33** passive `EP_GND_THERMAL_PAD`, etichetta `GND` esattamente sul pin locale (448.26,190.48 mm). Vecchi pin/collegamenti conservati; nessuna unione GND MCU/AUX/RX/`EFUSE_RTN`, nessun `PWR_FLAG`. Baseline V7.21 non toccata.
- Nuovo root 7 fogli `04_KiCad/Assemblaggio_RX_Power_V7.22_EP33_NOT_FOR_FAB/` punta allo schema MCU aggiornato e contiene tabelle librerie locali. Indice di moduli **NON elettricamente unificati**.
- **Tre librerie nuove con veri file `.kicad_mod`, geometria vendor controllata staticamente e registrata nel `fp-lib-table` V7.22 (non assegnate a nessun simbolo):**
  1. `04_KiCad/Librerie_Footprint_V7.22_ST_LQFP_TI_HOLD/S3900E_ST_LQFP_Review.pretty/STM32G474RE_LQFP64_ST_DS12288_CANDIDATE.kicad_mod`: ST DS12288 Rev.6 Fig.63, LQFP64 64 pad 1,20×0,30mm, passo 0,50mm, centri lati ±5,75mm, rame esterno 12,70mm.
  2. `04_KiCad/Librerie_Footprint_V7.22_RHB_TI_HOLD/S3900E_TI_RHB_Review.pretty/TLV320AIC3204_RHB0032E_VENDOR_CANDIDATE.kicad_mod`: TI SLOS602E pp.53–54, 32 pad periferici 0,60×0,25mm / passo 0,50, rame termico **EP33 3,45×3,45mm**, **4 aperture pasta 1,49×1,49mm**, copertura ~74,61% come stencil esempio TI da 0,125mm.
  3. `04_KiCad/Librerie_Footprint_V7.22_DBV_TI_HOLD/S3900E_TI_DBV_Review.pretty/TPS7A20_DBV0005A_VENDOR_CANDIDATE.kicad_mod`: TI SBVS338H p.57, cinque pad 1,10×0,60mm, centri colonna ±1,30mm e passo 0,95mm; pin1 IN,2 GND,3 EN,4 N/C,5 OUT.
- I **sei componenti U6201–U6206 rimangono senza footprint assegnato**. Per confronto i footprint standard KiCad consultati (non confermati in KiCad9 live) avevano quote pad differenti dagli esempi vendor; questa differenza **non certifica** i generici come inutilizzabili, e la compatibilità di maschera/stencil/courtyard/assemblaggio **NON** è approvata. Nessuna PCB completa, Gerber, TX, simulazione hardware, PVT o test a banco.

### Test e blocco live

- `03_Verifiche/V7.22/` report tecnico, **26 test Python nuovi** (EP33/netlist, ST64/TI5 pin names, pad 64/33/5, paste apertures, HOLD). Workflow `.github/workflows/v722_codec_ep33_native.yml` prevede **334 test totali** = 26 nuovi +308 storici, e **VERI export ERC/netlist KiCad9 prima/dopo**.
- **VERIFICHE EFFETTIVE FINORA: statiche**, lette dal GitHub branch e confrontate contro dati vendor: file S-expression bilanciati, sorgente MCU ricostruibile invertendo le sole modifiche pin33/label/titolo, root senza altre variazioni, geometria 64+33+5 pad, 4 aperture pasta EP33, tre library links e **nessun footprint assegnato**. Non confondere controlli statici con parsing/DRC/ERC nativi.
- **Actions non avvia il runner**, causa NON dimostrata: V7.0 baseline [run 42987689585](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42987689585) successo 08:31 UTC con 10 steps e runner; stesso workflow V7.0 [run 42994271590](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42994271590) failure con zero step; V7.22 HEAD [runs 42997214762](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997214762) e [42997229515](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515) `failure` con `runner_id=0, runner_name="", steps=[]`, dunque **zero test V7.22 realmente eseguiti**, non 334 PASS. Vedere [issue #24 — CI runner blocker](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/24). GitHub job logs non disponibili; accertare Settings/Actions/runner e possibile account/billing (solo ipotesi), oppure eseguire KiCad9 su runner realmente funzionante. No waiver fittizio.
- **Non integrare PR #23** senza controllo nativo del nuovo file KiCad, dei tre `.kicad_mod`, netlist ed ERC differenziale, test regressione 334 e qualifica package; non alterare policy o account settings alla cieca.

### Prossima ripresa (non chiedere all'utente “continua”)

1. Recuperare `main`, `AGENTS.md`, questo checkpoint e [PR #23](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23); usare lo stesso ramo esistente. Recuperare Actions #24 e motivazione reale runner KO, ripristinare CI se disponibile oppure ambiente KiCad9 equivalente; installare versioni reali senza produrre output fab. Eseguire `kicad-cli sch export netlist` + `sch erc` originale vs versione e `python -m unittest discover -s 03_Verifiche/V7.22` insieme alle regressioni.
2. Correggere eventuali difetti nativi rilevati, controllare footprint/MPN/land pattern e GND pad fisico, solo dopo CI verde e nessun gate di approvazione integrare PR e aggiornare checkpoint con merge SHA e run ID verificati.
3. Passare autonomamente a V7.23: 42 altri footprint mancanti, F200/Y1 non validati, power budget 13.8→5→3.3V, 15 cross-module HOLD, veri ERC e IF/RF/meccanica, poi PCB unica.

**Baseline main V7.21 ancora valida:** root 7 fogli, **132 componenti / 100 reti, ERC 36 errori + 340 warning**, footprint 48 mancanti (nuove librerie non cambiano il conteggio), 15 interfacce OPEN/HOLD, nessuna PCB globale; avanzamento storico ~10% *stima* invariata. **NO FAB / NO GERBER / NO PCBWAY / NO TX · SG48 HOLD**.

## Ultimo risultato ingegneristico integrato

| Campo | Valore |
|---|---|
| Ultima revisione ingegneristica | **V7.21** |
| PR | [#21 — merged](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/21) |
| Commit squash | `9805f110d0acf59e69f7f54e87e299248b99d96b` |
| Ultima CI della revisione | [run 42987421253 — success](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42987421253) |
| Test | **308 PASS, 0 FAIL, 0 SKIP**: 24 V7.21, 284 precedenti |
| Ultima vera modifica elettrica schema master | **V7.19**; V7.20–21 audit/verifiche, schemi invariati |
| Netlist root KiCad9 | **7 fogli, 132 componenti, 100 reti** |
| ERC root KiCad9 | **36 errori / 340 warning** |
| Footprint root | **84 compilati**, **48 mancanti** (46 MCU/CODEC, J100/J101), F200/Y1 esplicitamente non validati |
| Interfacce tra moduli | **15 OPEN/HOLD** |
| PCB singola completa | **NON creata**, nessun routing globale |
| Avanzamento PCB complessivo | **~10% stimato**, non automatico, non aumentato dalla V7.21 |
| Release | **NO FAB / NO GERBER / NO PCBWAY / NO TX · SG48 HOLD** |

## Prossima priorità di lavoro autonomo

**V7.22 — Correzione reale CAD con verifica vendor dei sei circuiti principali MCU/CODEC/POWER**, non solo un altro rapporto:

1. Per il codec **U6202 TLV320AIC3204 RHB** il simbolo KiCad nativo ha i soli pin **1–32**, mentre il package fisico ha la piazzola termica **EP33**. TI impone saldatura e collegamento a ground plane. Verificare [datasheet TI](https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf), aggiornare **copia versionata** dello schema/simbolo, aggiungere pin 33 e connessione di massa corretta **solo dopo** qualificare partizione GND; confronto pin-pad/EP, netlist ERC e stencil. **Non assegnare footprint prima di questa ECO**.
2. Qualificare da vendor ST **U6201 STM32G474RET6 LQFP64 10×10 0,5**; TI **U6202 RHB VQFN32 5×5 EP33**; quattro TI **U6203–U6206 TPS7A2033PDBVR SOT23-5**, con corretta funzione/pin e land pattern. Sei candidati già controllati per numeri pad in libreria KiCad9, ma *non ancora approvati*.
3. Passare poi alla qualifica degli **altri 42 footprint mancanti**, incluso X6201 e FB6201 e AUX J100/J101, e dei due assegnati esplicitamente `UNVALIDATED` F200/Y1. Non assegnare valori e footprint a caso per chiudere il contatore.
4. Risolvere in base a prove il source/return della catena 13,8 V→TPS26600 eFuse→TPS54202 5 V→TPS7A20 3,3 V. I sei LDO contano 2 su AUX 5V, 4 su MCU 5V ancora non qualificata. Nessuna unione arbitraria delle due reti o di EFUSE_RTN con GND_MAIN. Eseguire corrente/termica, inrush, PVT reali e verifiche a banco.
5. Qualificare gradualmente le **15 interfacce**, RX→IF e chassis; solo con netlist realmente integrata realizzare **PCB unica** in KiCad, poi DRC, regole RF, confronto pin-pad-net, ERC, e prototipo prima di un rilascio.

Se in questa sessione si completa V7.22, **non fermarsi automaticamente**: dopo CI/PR/merge passare subito alla priorità V7.23 e successive, finché consentito da tempo e strumenti.

## File e riferimenti obbligatori

- [Protocollo permanente agenti](../AGENTS.md)
- [Handoff storico completo](../RIPRENDI_IN_UNA_NUOVA_CHAT.md)
- [Rapporto tecnico V7.21](../03_Verifiche/V7.21/RAPPORTO_TECNICO_CAD_V7.21.md)
- [Gates per la PCB unica](../01_Specifiche/V7.21/PIANO_QUALITA_PCB_UNICA_GATES_V7_21.md)
- [Stato GitHub PR](https://github.com/jd3485/Superstar3900-SMD-Evolution/pulls)
- [Run GitHub Actions](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions)

## Contratto di aggiornamento del checkpoint

Alla fine di ogni **versione** e **prima della scadenza del contesto Work**:

- Sostituire questa sezione con **latest PR effettivamente merged**, commit, branch HEAD, ultima Actions CI verde o rossa, totale test, ERC/DRC, netlist, cambiamenti elettrici CAD REALI, percentuale PCB onesta.
- Annotare ramo/PR eventualmente **aperti ma non mergiati**, errori inattesi e prossima correzione, con comandi/file per riprendere senza chat precedenti.
- Segnalare ciò che rimane HOLD e **NO FAB / NO TX**; non dichiarare sbloccato un gate senza evidenza.
- Aggiornare lo storico `RIPRENDI_IN_UNA_NUOVA_CHAT.md`; non affidarsi alla memoria della nuova sessione.

**Una chat nuova deve riuscire a riprendere tutto leggendo `AGENTS.md` + questo documento + GitHub live, anche se non ha accesso alla cronologia della chat precedente.**
