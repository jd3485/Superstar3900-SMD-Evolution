# V7.49 — ECO elettrica: quattro pull-down deboli per ingressi opzionali LMX2572

**13 novembre 2026. Baseline V7.48:** [PR #52](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/52) MERGED. **Questa revisione modifica realmente i collegamenti locali**, non è un nuovo footprint o un waiver ERC. Nessuna interfaccia AUX–MCU o TX viene connessa.

## Problema diagnosticato sull'ERC KiCad9

Dall'artefatto nativo `v743.original.erc.rpt` (già presente nel workspace storico) si ricavano esattamente i **36 errori baseline**:
- **26 × `label_dangling`**: interfacce e stub ancora aperti, incluso Y1 pin10 AFC/GND, TX_ENABLE, PTT e connessioni crossmodule. Non sono stati soppressi.
- **6 × `power_pin_not_driven`**: supply/ground su AUX, PLL e MCU isolati; il root è index-only, non collegato e il power budget resta HOLD; non aggiungere `PWR_FLAG`.
- **4 × `pin_not_driven`**: input `U1 LMX2572RHA` pin **5 SYNC**, **28 SysRefReq**, **30 RampClk**, **32 RampDir**: segnali per ora non pilotati dal host, etichettati `PLL_*_PENDING`.

**Fonte primaria Texas Instruments verificata mediante screenshot PDF:** `LMX2572` datasheet **SNAS740B**, par. **8.1.10 Unused Pins**, pagina stampata **74**, PDF pagina zero-based **73**: https://www.ti.com/lit/ds/symlink/lmx2572.pdf . La raccomandazione TI è di tirare a basso proprio **SYNC (5), SysRefReq (28), RampClk (30), RampDir (32)** se inutilizzati. Il dato non certifica che siano *permanentemente* inutilizzati: potranno in futuro essere pilotati da GPIO con livelli idonei, purché il loro collegamento top-level sia qualificato.

## Scelta elettrica e prestazioni

Scelti quattro **resistori di pull-down 10 kΩ ±1% in package 0402**, contro `GND_MAIN` **locale AUX**, non unire masse fra moduli. La scelta 10k è una **decisione circuitale di progetto**, non un valore obbligatorio TI. È sufficientemente debole da consentire un GPIO futuro di affermare HIGH (corrente statica ≈**0,33 mA a 3,3 V**, ≈0,18mA a 1,8V), e abbastanza forte da ridurre il rischio di ingresso CMOS ad alta impedenza flottante quando non pilotato. Le condizioni di reset/boot host, livelli 1.8–3.3V, tolleranza I/O e transienti EMC restano da validare sul sistema reale. L'uso di pull-down implica un'opzione predefinita **LOW**, non un collegamento fissato permanentemente a massa: non si perdono le funzioni SYNC, SYSREF, ramping in future revisioni se il firmware le richiederà.

| Nuovo Ref | U1 pin | Rete di controllo conservata | Contatto aggiunto |
|---|---:|---|---|
| `R70` | 5 | `PLL_SYNC_PENDING` | R70.1→segnale / R70.2→`GND_MAIN` |
| `R71` | 28 | `PLL_SYSREFREQ_PENDING` | R71.1→segnale / R71.2→`GND_MAIN` |
| `R72` | 30 | `PLL_RAMPCLK_PENDING` | R72.1→segnale / R72.2→`GND_MAIN` |
| `R73` | 32 | `PLL_RAMPDIR_PENDING` | R73.1→segnale / R73.2→`GND_MAIN` |

I resistori sono aggiunti nel foglio PLL locale, nelle coordinate sulla griglia KiCad 1.27 mm (x=600.71 mm, y=365.76 / 388.62 / 411.48 / 434.34 mm) sul formato A1 già esistente, con etichette direttamente sui terminali; nessuna geometria del dispositivo U1, delle sue piste già esistenti o dei resistori R10–R15 è stata toccata. Footprint `Resistor_SMD:R_0402_1005Metric` è una libreria KiCad standard già impiegata nel progetto, da qualificare a DFM/assembly globale. La risposta di questi ingressi a RFI e rumore e l'eventuale valore definitivo dei resistori restano REVIEW.

## CAD e gate

Copia del sottosistema AUX `04_KiCad/Gerarchico_Alimentazioni_V7.49_LMX_UNUSED_PULLDOWN_REVIEW_NOT_FOR_FAB/`: root, eFuse e buck **byte-identici** alla V7.31, PLL `03_PLL_LDO_TCXO.kicad_sch` aggiornato **solo** con 4 R_PLL e 8 etichette. Nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.49_LMX_PULLDOWN_REVIEW_NOT_FOR_FAB/` che referenzia AUX V7.49 e mantiene MCU V7.48 e RX V7.14 senza alcuna connessione intermodulo. J100/J101 restano non qualificati, senza footprint (2 mancanti).

`03_Verifiche/V7.49/test_lmx2572_unused_inputs_native_v749.py` richiede KiCad9 nativo con confronto netlist/ERC sette fogli prima/dopo, strict sorgenti AUX, **134→138 componenti** (4 R nuovi), **tutte le precedenti coppie pin/rete invariate**, esattamente 8 pin nuovi nei quattro resistori, **101 reti** nel baseline e nella ECO, ciascun pull-down fra la corretta rete `PLL_*_PENDING` e `GND_MAIN`, 2 footprint mancanti invariati, nessuna crescita di ERC. Un calo del numero ERC da solo **non** prova il funzionamento del PLL; né è una condizione per rimuovere interfacce intenzionalmente aperte.

**Actions ottimizzata:** esteso il workflow KiCad9 già esistente `.github/workflows/v743_six_ldo_thermal_budget.yml`, senza creare cinquantesima pipeline. Lo stesso runner già precaricato esegue le regressioni V7.43–48 più i 10 test V7.49 e salva le netlist/ERC; gate YAML cost/safety si attiva per il file workflow. Non dichiarare esito prima dei check reali.

**HOLD:** firmware/configurazione effettiva SYNC/SYSREF/RAMP, J100/J101, rail buck e eFuse, `GND_MAIN↔GND`, 15 interfacce crossdomain, Ceff MLCC 1µF/10µF, reverse current TPS7A20, SG48, Y1 pin10 AFC/GND. Nessuna PCB unica completa e nessun DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Percentuale PCB totale storica circa 10%, non aumentare automaticamente con un pull-down.
