# V7.66 — ingresso eFuse: F200 su griglia e analisi elettrica TPS26600/F200

13 novembre 2026. Baseline `main` V7.65 (140 componenti, 103 reti, ERC 28 errori/206 warning, 306 test PASS).

## 1. ECO KiCad vera, non elettrica

Nuovo foglio AUX `04_KiCad/Gerarchico_Alimentazioni_V7.66_F200_FUSE_GRID_REVIEW_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch`: **F200** fusibile candidato Littelfuse `045101.5MRL` 1.5A da (58,77) a (58.42,76.20) mm sulla griglia 2.54 mm. Spostate solo due label solidali: `PWR_13V8_AUX_RAW` (52.92,77)→(53.34,76.2) e `EFUSE_VIN` (63.08,77)→(63.50,76.2). Esattamente sei atomi sorgente (simbolo, 3 coordinate proprietà, 2 label). Nessun valore/MPN/pad/net pin cambiato. Candidato F200 non autorizzato per fab. Root versionata `04_KiCad/Assemblaggio_RX_Power_V7.66_F200_FUSE_GRID_REVIEW_NOT_FOR_FAB/`, cambiare solo il Sheetfile AUX; i sei fogli non eFuse, librerie e project tables identici.

## 2. Soglie nominali TI per i valori realmente nel progetto

Fonte primaria: Texas Instruments [TPS2660x SLVSDG2G Rev G](https://www.ti.com/lit/ds/symlink/tps2660.pdf) §10.2.2.2–3 (pagina stampata 29, Eq. 9–12) e §7.5 Electrical Characteristics (pagina 7). `R200=365kΩ` (=R1 da VIN a UVLO), `R201=16.2kΩ` (=R2 UVLO→OVP), `R202=30.1kΩ` (=R3 OVP→RTN), totale 411.3 kΩ. VIN nominale 13.8V.

- `VUVLO_rise = V_UVLOR × (R1+R2+R3)/(R2+R3)` con rif. tipico **1.19V** → **10.5712V**.
- `VOVP_rise = V_OVPR × (R1+R2+R3)/R3` con rif. tipico **1.19V** → **16.2607V**.
- Corrente nominale nel partitore a 13.8V → **33.552µA**, ben maggiore di 20×100nA nel solo calcolo semplificato. Inversione di ingresso, impedenza reale, leakage dei due pin e altri fattori non inclusi.
- Angoli simultanei **1%** resistori (otto combinazioni) e MIN/MAX riferimento TI: UVLO rise **10.2545–11.0772V**, OVP rise **15.6940–17.0524V**, **senza** pin leakage, tolleranze ambientali extra, transitori, reverse-bias e statistica. Questi angoli sono solo un'approssimazione conservativa dei valori tabellati e non una caratterizzazione del prodotto.
- R203 ILIM **8.2kΩ**: eq.9 `Ilim ≈ 12 / RkΩ` → **1.4634A nominale**, **non** una garanzia di 1.463A. TI specifica 1.425/1.5/1.575 A per 8.0kΩ nelle sue condizioni dichiarate, e lo stesso valore non va copiato sui limiti a 8.2kΩ senza una dimostrazione.
- R204 MODE 402kΩ RTN mantiene latch-off, SW200 SHDN a GND_MAIN non cambia. U200 pin8 RTN / PowerPAD17 EFUSE_RTN resta rigorosamente distinto da U200 pin9 GND_MAIN.

## 3. RISCHIO concreto di coordinamento fusibile–eFuse

Fonte primaria [Littelfuse 451/453 series datasheet](https://www.littelfuse.com/~/media/electronics/datasheets/fuses/littelfuse_fuse_451_453_datasheet.pdf.pdf), e [scheda F200 MPN](https://www.digikey.co.uk/en/products/detail/littelfuse-inc/045101-5MRL/700820). F200 nominale **1.5A**, Littelfuse indica **derating ordinario 25% per carico continuo**, ulteriore derating in temperatura: **1.5 × 0.75 = 1.125A** come valore di progetto continuo a temperatura di riferimento (non tempo di interruzione). R203 limita idealmente a circa **1.46A**, superiore ai 1.125A raccomandati come carico continuo per F200. F200 **NON si apre automaticamente a 1.5A**: dipende dalla curva tempo/corrente, temperatura e condizioni dell'impianto. Il fusibile potrebbe scaldarsi o intervenire prima/dopo le protezioni attese in alcune condizioni. Senza carico reale 5V, spunto, fault current da sorgente 13.8V, capacità, temperature e curva integrale, **non esiste coordinamento comprovato**. Evitare di approvare F200=1.5A e R203 8k2 come coppia definitiva.

## 4. Correzione importante: SHDN 0.76V NON è garanzia

**RETTIFICA della modellazione troppo ottimista presente nel test logico storico V7.64:** TI §7.5 `V(SHUTF)` sulla transizione in discesa è **min 0.55V, tip 0.76V, max 0.94V**. Per un comando garantito sotto la soglia in tutto il range tabellato, occorre portare SHDN **sotto 0.55V**, alle condizioni TI, non assumere che 0.75V garantisca lo spegnimento. Il pulsante reale va misurato ai pin e testato su fault permanente; stato HIGH e tempi reset ancora non provati. I test V7.66 registrano esplicitamente `shdn_v0p76_guaranteed_off=False`, senza falsare test storici versionati. Non è una simulazione di transitori.

## 5. Requisiti prima della produzione

`03_Verifiche/V7.66/test_f200_fuse_ti_uvlo_ovp_ilim_native_v766.py`: 20 nuovi test, verifica 6 cambi letterali nel CAD, KiCad9 native netlist+ERC su entrambi master 7-sheet, mappa pin→rete e 140 componenti/103 reti invariati, nessuna nuova ERC o waiver, rimozione esclusiva di un `endpoint_off_grid` F200 (target **28 errori 206→205 warning**, solo se dimostrato dalla CI). Verifiche numeriche riproducibili per corner 1%, corrente partitore, corrente R203 e derating fusibile e SHDN. Nessuna ESD aggiunta arbitrariamente.

**BLOCKING:** [Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) rimane OPEN, F200 corrente e termica HOLD, TPS26600 RTN/GND separati, D200 TVS DNP, SW200 accessibilità meccanica ESD e reset fisico non verificati, TPS54202 e C103/C104 worst case non verificati, 15 crossmodule OPEN/HOLD, SG48 e Y1 pin10 HOLD, 28 errori ERC non eliminati, assenza di PCB completa e di DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
