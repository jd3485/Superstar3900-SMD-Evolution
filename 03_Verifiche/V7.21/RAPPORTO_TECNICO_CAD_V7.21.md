# Superstar 3900 SMD Evolution — V7.21 | Rapporto PCB: componenti, footprint e sicurezza power/termica

**11 novembre 2026 · PRE-LAYOUT della PCB UNICA · NO FAB / NO TX.**

## 1. Decisione tecnica

La V7.21 non finge di creare una PCB «completa» da schemi ancora elettricamente separati. Prima viene eliminata la possibilità di sbagliare la **scelta delle impronte (footprint), i limiti dei regolatori e la corrente/temperatura**. È una decisione concreta di qualità: i controlli del progetto devono poter bloccare il rilascio, anche se il risultato non aumenta visivamente lo sbroglio.

## 2. Risultati ottenuti con la netlist KiCad9 nativa

La CI [GitHub Actions 42986310630](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42986310630) **success** esegue `kicad-cli sch export netlist` e `kicad-cli sch erc` sul **master V7.19 a sette fogli**, non su una simulazione dei componenti.

| Audit automatico | Risultato nativo |
|---|---:|
| Totale componenti dello schema radice | **132** |
| Footprint valorizzati nella netlist | **84** |
| Footprint assenti | **48** |
| Assenti nel modulo MCU/CODEC | **46** |
| Assenti nei connettori AUX J100/J101 | **2** |
| Footprint già scritti ma dichiarati non validati | **2** (F200 e Y1) |
| ERC root | **36 errori / 340 warning** |
| Interfacce RX/MCU/AUX ancora OPEN/HOLD | **15** |

Il file CSV `v721.missing_footprints.csv` con tutti e 48 i reference designator è nell'artefatto CI. **Le altre 82 assegnazioni non sono automaticamente «vendor-qualified»**: l'audit riconosce soltanto 2 evidenti riferimenti `UNVALIDATED`, non certifica le altre.

### Sei footprint candidati studiati nel database KiCad9 vero, senza modificarli

`03_Verifiche/V7.21/audit_candidate_packages_v721.py` legge le **librerie KiCad9 installate**, conta e confronta i pad, senza assegnare un footprint alla schematica. I candidati passati alla prova *numero pad* sono:

| IC | Package/manufacturer | Impronta KiCad candidata | Pad reali nel file |
|---|---|---|---:|
| U6201 STM32G474RET6 | [ST DS12288](https://www.st.com/resource/en/datasheet/stm32g474vb.pdf) LQFP64 10×10 passo 0,5 | `Package_QFP:LQFP-64_10x10mm_P0.5mm` | 64 |
| U6202 TLV320AIC3204 | [TI SLOS602E](https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf) RHB VQFN 32 5×5 passo 0,5, pad termico ~3,45×3,45 | `Package_DFN_QFN:VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm` | **33** |
| U6203/04/05/06 TPS7A2033PDBVR | [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf) DBV SOT23-5 | `Package_TO_SOT_SMD:SOT-23-5` | 5 ciascuno |

**BLOCCO CAD verificato: il simbolo KiCad nativo del codec U6202 espone soltanto i pin 1–32, mentre il footprint TI RHB porta anche EP33.** Il [datasheet TI SLOS602E §12.1](https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf) richiede che il thermal pad venga saldato e collegato al piano di massa (non è internamente collegato). V7.22 dovrà introdurre un pin EP33 nello schema versionato, collegarlo al GND approvato e validare stencil/land pattern. **Questo non libera ancora nessun componente**: anche i restanti simboli `DRAFT` richiedono confronto completo pin↔pad, quote rame, courtyard, assemblaggio e MPN definitivo. I 42 footprint rimanenti sono ancora da scegliere. F200 fusibile candidato ha nome `FOOTPRINT_NON_VALIDATO` e Y1 oscillatore 7N TXC ha `UNVALIDATED`.

## 3. Prima valutazione quantitativa delle alimentazioni

La netlist KiCad e le istanze dei componenti sono state esaminate direttamente.

| Pezzo / blocco | Datasheet e limite | Implicazioni progettuali |
|---|---|---|
| **U200 TPS26600PWPT** | [TI TPS2660](https://www.ti.com/product/TPS2660), corrente limite regolabile 0,1–2,23 A, protezione inversione | Effettivo limite impostato da ILIM, input surge e ritorno `EFUSE_RTN` ancora da verificare. F200 è un fusibile **1,5 A candidato** |
| **U100 TPS54202DDCR** | [TI TPS54202](https://www.ti.com/product/TPS54202), uscita **2 A continui** | Non è sufficiente conoscere la portata: servono consumo reale dei rami 5V, inrush, ripple, efficienza, induttore, termica, EMI |
| **U2/U3 e U6203–U6206 TPS7A2033PDBVR** | [TI TPS7A20](https://www.ti.com/product/TPS7A20), **300 mA ciascuno** | Esistono **6 LDO**; due alimentati dalla rete AUX 5V, quattro dalla rete MCU `5V_DIGITAL_FILTERED`, ancora **non collegata realmente** all'uscita buck AUX |

La somma astratta dei sei limiti di targa è **1,8 A**, ma NON rappresenta il consumo della radio e non può essere considerata il carico reale del buck; le due linee 5V sono ancora separate. Il confronto diretto «fusibile input 1,5 A contro buck output 2 A» sarebbe errato senza considerare i livelli di tensione e l'efficienza.

### Rischio termico reale da dimensionare, non un guasto già dimostrato

Per un singolo **TPS7A20 in DBV SOT23-5**, TI SBVS338H indica `RθJA=187,1 °C/W` su PCB test JEDEC. Se l'LDO ricevesse 5,0V e fornisse 3,3V a **300 mA continuativi**, la perdita sarebbe **0,51W** e il calcolo JEDEC darebbe `ΔT≈95,4°C`. Con **40°C** ambiente, `TJ≈135,4°C` supera 125°C di temperatura operativa. A **60°C** si stimerebbero 155,4°C nello stesso scenario, più rischioso.

**Azione obbligatoria:** definire assorbimenti effettivi per tutti i rami, margine e dissipazione di ogni LDO, condizioni di ambiente e stackup termico PCB, con simulazione/validazione fisica. L'RθJA di JEDEC NON descrive automaticamente il PCB futuro: il rapporto è uno **screening che blocca la conclusione «300mA sempre sicuri»**, non una misura hardware.

### VOUT reale del TPS54202: non basta dire «5V»

Il divisore effettivo del foglio buck è `R101=100kΩ 1%` sopra `R102=13,3kΩ 1%`. Il riferimento TI `Vref=0,596V tipico` (min 0,581; max 0,611), produce:
- `Vout_nom≈5,0772V` con parti nominali.
- `Vout≈4,8629…5,2978V` come combinazione aritmetica estrema **solo** di Vref e tolleranze R.

Questi non sono limiti garantiti della tensione con carico: restano da sommare cadute, ripple switching, transitori, layout, compensazione, valori reali dei condensatori e EMI. La decisione sul valore nominale e sul margine dei carichi va effettuata prima dello sbroglio.

## 4. Gate automatizzati e test

**Pipeline V7.21**: [CI 42986310630](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42986310630) **success**, KiCad9 reale + ngspice storici e **24 test nuovi V7.21 +284 regressioni storiche =308 Python PASS, 0 FAIL, 0 SKIP**. Output:
- `v721.root_v719.net`, `v721.root_v719.erc.rpt` da KiCad9 originale;
- `v721.native_board_foundations.json` (132/48/termica/buck/rail);
- `v721.missing_footprints.csv` (48 righe con tutti i REF);
- `v721.candidate_IC_packages_native.json` e `v721.candidate_IC_packages.csv` (6 candidati, pad reali della KiCad9, nessuna approvazione di produzione).

Gli script rifiutano modifiche impreviste della lista componenti, delle impronte candidate, delle reti GND/5V o delle 15 interfacce OPEN/HOLD.

## 5. Conseguenza e decisione per la PCB unica

**Non creo ancora una falsa PCB unificata**, perché 48 footprint non sono assegnati, 2 sono esplicitamente non validati, gli assorbimenti/ritorni non sono dimostrati e il master a 7 fogli conserva 36 ERC/340 warning. La geometria della scheda e i punti di fissaggio chassis non sono ancora documentati e non saranno inventati. Lo sviluppo della PCB completa è tuttora **~10% stimato**: è progredita la *qualità di progetto*, non la percentuale di piste sbrogliate.

**Prossima V7.22:** iniziare **l'assegnazione in una copia schematica versionata dei sei package con confronto esatto dei pin**, a partire da U6201, U6202 e quattro TPS7A20; esplicitare il pad termico codec e il suo collegamento conforme al vendor. Poi selezionare footprint/MPN dei 42 residui, richiedere revisione attuale delle reti di alimentazione e passare a pre-layout meccanico a quote certificate. Lo stack-up 4 strati è *solo ipotesi* fino a ritorno di massa/impedenza/meccanica validati.

**NO FAB / NO GERBER / NO PCBWAY / NO TX, SG48 HOLD, no antenna/PA attivati.**
