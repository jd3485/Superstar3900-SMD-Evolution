# V7.37 — Analisi quantitativa brownout TPS3840PL30 → TPS7A2033, NO FAB/TX

**Data:** 13 novembre 2026. **Baseline:** V7.36 integrata su `main`, PR#39 squash `e3ea888bdac51ff7d0061c8c6b932e4edb71cbe0`. **Questa revisione NON modifica il CAD:** l'obiettivo è delimitare con parametri **garantiti da TI** la sicurezza della scelta originale `U6207 TPS3840PL30DBVR`, evitando modifiche arbitrarie e individuando specificamente ciò che **non** è dimostrabile. Il test versionato è `03_Verifiche/V7.37/test_tps3840_pl30_brownout_corners_v737.py`.

## Documenti TI e intervalli controllati
- [TPS3840 SNVSB03E Rev. E, maggio 2026](https://www.ti.com/lit/ds/symlink/tps3840.pdf), §6.5 (p6), §§6.6/7.3/7.4 (pp7, 17–20): `VIT-` accuratezza **±1.5% massimo** su temperatura -40 a +125°C (NON ±5%: verificare la tabella originale); per `VIT-=3.0V` `VHYS` nell'intervallo **75–125mV** (tipico 100mV); uscita `TPS3840PL` `VOL≤0.2V` a Isink=2mA, VDD 1.5–5V; `VOH≥0.8×VDD` a Isource=2mA quando sopra `VIT+`; `VPOR≤0.3V` al carico di prova 200nA e relativo limite di slew. Al di sotto di VPOR lo stato RESET_N è **non garantito**, e non si può inferire un output stabilmente basso dal diagramma esemplificativo.
- [TPS7A20 SBVS338H Rev. H, luglio 2024](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), §5.5 (pp6–7), §6.3.2 (p24): per TPS7A2033PDBVR 3.3V `VOUT±1.5%` MAX **sotto condizioni** VIN≥VOUT_nom+0.3V e 1–300mA (non in dropout/brownout, non durante startup); pin3 `EN` `VEN(HI)≤0.9V`, `VEN(LOW)≥0.3V` a VIN 1.6–6V; pull-down smart interno circa **500kΩ** tipico **solo** quando EN non è alto, quindi non un collegamento a massa garantito per qualunque corrente esterna. `tSTR` 750–1150µs con condizioni del datasheet, non un limite globale per ogni scenario.

## Matrice conservativa di compatibilità statica

| Voce | Calcolo / condizione worst case | Risultato |
|---|---|---:|
| U6205 OUT 3.3V, limite inferiore in regolazione | 3.3×(1−0.015) | **3.2505V** |
| U6205 OUT 3.3V, limite superiore in regolazione | 3.3×(1+0.015) | **3.3495V** |
| TPS3840 PL30 soglia VIT- inferiore | 3.0×(1−0.015) | **2.955V** |
| TPS3840 PL30 soglia VIT- superiore | 3.0×(1+0.015) | **3.045V** |
| TPS3840 PL30 rilascio VIT+ massimo | 3.045 + 0.125 | **3.170V** |
| **Margine rilascio con U6205 in regolazione** | 3.2505 − 3.170 | **+0.0805V** |
| TPS3840 VOH minimo a VDD=3.2505V | 0.8×3.2505 | 2.6004V |
| Margine VOH su TPS7A20 EN_HIGH | 2.6004 − 0.9 | **+1.7004V** |
| Margine VOL su TPS7A20 EN_LOW | 0.3 − 0.2 | **+0.100V** |

**Conclusione limitata:** in condizioni **stazionarie, regolate e corrispondenti ai test TI**, il circuito **TPS3840PL30DBVR + TPS7A2033PDBVR** ha margine positivo e **non richiede un cambio automatico a PL29/PL28**. Tali varianti abbasserebbero la soglia di trip di brownout e potrebbero peggiorare la protezione contro rail in caduta: nessun motivo sufficiente per sostituirle senza specificare il budget ripple e tolleranze del carico. Anche un pull-down esterno potrebbe non risolvere il caso di un'uscita push-pull indeterminata attivamente pilotata e richiede analisi delle correnti: non aggiungerlo per sola precauzione.

## Dinamica brownout: cosa rimane davvero sconosciuto

1. Con `VDD < VPOR≈0.3V`, il reset supervisor è **undefined**. L'ingresso EN del TPS7A20 ha pull-down interno tipico, ma se il supervisore retroalimentato o sotto fault sourcing genera una tensione > soglia EN, il solo pull-down interno **non garantisce** spegnimento in ogni guasto. Il valore `VPOR` massimo è legato alle condizioni di carico e `slew rate` specificate da TI.
2. Nella banda di isteresi del TPS3840 circa `2.955–3.170V`, lo stato può dipendere da direzione di attraversamento, chip/tolleranze e precedenti transizioni: **classificare UNKNOWN** per una prova statica universale.
3. IOVDD può scendere fuori regolazione prima della tensione richiesta dal codec o della soglia del supervisore, oppure il dominio 5V può permanere mentre U6205 è guasto. **Nessuna prova** di brownout hardware, ESL/ESR dei condensatori, impedenza della massa, transitorio e ritorni.
4. LDOIN U6206 e codec possono avere alimentazioni residue/back-feed e sequenze di reset e ALDO dipendenti dal firmware. I/O del codec, VDD e pin EN richiedono un modello temporale o una misura.
5. C6231 100nF X7R resta nominale e `Ceff @3.3V/T/aging` non garantita: non trattare la decoupling in condizioni peggiori come già qualificata.

## Gate e decisione

`test_tps3840_pl30_brownout_corners_v737.py` verifica la baseline KiCad V7.36 (U6207 MPN/footprint e due label dell'EN), 16 casi di calcoli sui limiti TI, sceglie esplicitamente `UNKNOWN` dove il datasheet non consente deduzioni. Un nuovo workflow GitHub Python-only `.github/workflows/v737_codec_brownout_corners.yml` esegue soltanto questi test **senza installazioni né KiCad**. Nessun workflow di netlist/ERC necessario **poiché file CAD invariati**. Non dichiarare SUCCESS finché non è riportato un run reale.

**Decisione:** nessuna ECO elettrica arbitraria. V7.37 è una qualificazione **condizionale statica** riproducibile, NON signoff brownout e NO PCB/DRC/FA B. `main` V7.36: **134 componenti/101 reti/33 footprint mancanti/ERC36 errori +221 warning** invariati. Continuare con simulazione startup e worst-case delle rail o qualifica passivi C6201–C6230, ma mantenere 15 interfacce crossmodule OPEN/HOLD, SG48 HOLD, Y1 TCXO pin10 HOLD, **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
