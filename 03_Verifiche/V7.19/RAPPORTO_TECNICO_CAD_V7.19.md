# Superstar 3900 SMD Evolution — Rapporto tecnico KiCad V7.19

**11 novembre 2026 — correzione elettrica nativa del filtro di anello LMX2572 nel master della radio. NO FAB / NO TX.**

## 1. Risultato effettivo

È stata realizzata **una nuova copia completa dell'indice KiCad a 7 fogli**, lasciando intatti gli originali V1.5, V7.17 e V7.18. Il master `04_KiCad/Assemblaggio_RX_Power_V7.19_PLL_PINNET_NOT_FOR_FAB/` punta esclusivamente a un nuovo ramo AUX `04_KiCad/Gerarchico_Alimentazioni_V7.19_PLL_PINNET_NOT_FOR_FAB/`.

Nel solo foglio `03_PLL_LDO_TCXO.kicad_sch` sono state aggiunte **esattamente 6 etichette su pin esistenti**, senza aggiungere fili, componenti, modelli o collegamenti tra moduli:
- pin R2:1 `PLL_CPOUT`, R3:1 `PLL_CPOUT`;
- pin R3:2 `PLL_VTUNE`;
- pin R2:2 `PLL_R2_C2`, C2:2 `PLL_R2_C2`;
- pin C3:2 `PLL_VTUNE`.

I file `01_EFUSE_AUX.kicad_sch` (incluso l'ECO OUT15/16 verificato in V7.18), `02_BUCK_5V.kicad_sch` e `S3900E_AUX_POWER_V1_5.kicad_sch` sono **byte-identici alla copia V7.18**; la schematica RX e MCU resta immutata, come il PCB coupon.

## 2. Fondamento schematico vendor: non confondere topologia e prestazioni

Fonti primarie realmente confrontate:
- [TI LMX2572 datasheet SNAS740B, Fig.179, pagina 75](https://www.ti.com/lit/ds/symlink/lmx2572.pdf): CPOUT→R3→VTUNE, ramo R2–C2 e C1 verso massa lato CPOUT, C3 verso massa lato VTUNE. CPout è pin U1:12, Vtune U1:35.
- [TI LMX2572EVM SNAU217B Fig.19 p.13 e Tab.1 p.5](https://www.ti.com/lit/ug/snau217b/snau217b.pdf): implementazione EVM e **valori diversi** da quelli ipotizzati per il progetto Superstar.

Il requisito testuale del vendor di almeno **1,5 nF shunt su VTUNE** è soddisfatto **come valore nominale** dal C3 progettuale 2,2 nF; il **posizionamento fisico vicino al pin VTUNE non è verificato**. R2 620Ω, R3 22Ω, C1 220pF, C2 120nF, C3 2,2nF restano **CANDIDATI / HOLD** fino a valutazione con PLLatinum Sim, parametri veri fPD/KVCO/charge-pump, banda, margine fase, spur e PCB.

## 3. Esito della CI KiCad9 nativa

[GitHub Actions 42967147073](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42967147073): **success**. Workflow `.github/workflows/v719_pll_pin_native.yml`:
1. avvia 4 esperimenti KiCad9 su cloni temporanei e conserva ogni ERP/netlist;
2. avvia 2 esperimenti su etichette dirette di pin;
3. esporta la **vera netlist KiCad9** V7.18 e V7.19 da due master reali a 7 fogli;
4. esegue **ERC nativo completo**, senza waiver e senza spegnere errori;
5. richiede tramite `check_loop_full_native_v719.py` **esattamente le 12 associazioni pin-rete del contratto**, e **nessuna modifica ad altre reti**, con controllo sorgente che ammette soltanto 6 label;
6. esegue **13 nuovi test** e tutte le **253 regressioni storiche** = **266 PASS, 0 FAIL, 0 SKIP**.

| Misura reale KiCad9 | Prima V7.18 | Dopo V7.19 |
|---|---:|---:|
| Errori ERC root sette fogli | **42** | **36** |
| Warning ERC | **340** | **340** |
| `pin_not_connected` | 2 | **0** |
| `wire_dangling` | 3 | **0** |
| `pin_not_driven` | 5 | **4** |
| `power_pin_not_driven` | 6 | **6** |
| `label_dangling` | 26 | **26** |
| Reti native esportate | **99** | **100** |
| Unica rete aggiunta | — | **`PLL_R2_C2`** |
| Cambi di membership fuori da PLL_CPOUT / PLL_VTUNE / PLL_R2_C2 | — | **0** |
| Interfacce cross-modulo approvate | 0 | **0** |

**La differenza di 6 errori è interamente spiegata:** -2 `pin_not_connected`, -3 `wire_dangling`, -1 `pin_not_driven` (VTUNE ora raggiungibile da CPOUT attraverso R3). KiCad esporta ora:
- `PLL_CPOUT`: `U1:12, C1:2, R2:1, R3:1`;
- `PLL_R2_C2`: `R2:2, C2:2`;
- `PLL_VTUNE`: `U1:35, R3:2, C3:2`;
- `GND_MAIN` per `C1:1, C2:1, C3:1`, mantenendo il percorso GND storico non ancora qualificato per correnti di ritorno RF.

Il report JSON nativo è `03_Verifiche/V7.19/output-ci/v719.real_full_master_erc_netlist_gate.json` in Artifacts. Tutte le **altre reti e i pin/ref** sono stati confrontati, non soltanto il numero complessivo.

## 4. Limiti espliciti e percorso verso il PCB completo

Lo schema della radio ha **36 errori ERC ancora aperti**, nello specifico **26 etichette pendenti, 6 alimentazioni non riconosciute come pilotate, 4 ingressi non pilotati**, più **340 warning**. L'integrazione AUX/MCU/RX mantiene tutte le **15 interfacce OPEN/HOLD** e `tx_permission=0`. Il PLL non ha ancora verifiche analogiche, campioni misurati, stack-up, footprint/vendor approval, riflessioni RF, EMI o posizionamento reale C3 vicino a VTUNE.

Da fare, ordine prioritario:
1. Verificare con **TI PLLatinum Sim** o modello analogo stabilità e valori del filtro per tutto il piano frequenze radio.
2. Affrontare i **6 power-pin-not-driven** solo quando sorgenti 13,8V e 5V/3V3 e ritorni distinti sono qualificati, senza PWR_FLAG per nascondere problemi.
3. Definire funzione controllata e condizioni statiche dei **4 ingressi PLL** SYNC/SysRefReq/RampClk/RampDir; non unire a massa indiscriminatamente senza architettura.
4. Qualificare **15 interfacce RX/MCU/AUX**, completare stadio `RX_IF_STAGE`, scegliere MPN/footprint e risolvere 340 warning CAD; quindi sviluppare la prima `.kicad_pcb` **unica** della radio e validarla in DRC.
5. Conservare RX coupon SMA J9102/J9104 a 180° fisici e qualificarli secondo vendor prima della fabbricazione.

Questa è una **correzione di connettività schematico** reale, ma non layout della scheda. Stima PCB completa **~10%, invariata**. Nessun Gerber, nessuna spedizione a PCBWay, niente TX né RF in aria. **NO FAB / NO TX.**
