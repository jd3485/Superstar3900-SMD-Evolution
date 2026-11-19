# V7.82 — PCB master unica: estensione fisica PLL e connettore host (NO FAB)

## Modifica tecnica concreta

Generatore KiCad9 `03_Verifiche/V7.82/build_master_pll_stage_v782.py` estende lo **stesso master PCB** con **50 impronte fisiche aggiuntive** dal master nativo a 7 fogli V7.79: tutti i 49 componenti del foglio PLL/LDO LMX2572 **eccetto Y1** TCXO non qualificato, più connettore J101 host SPI. Complessivamente **25 power +49 MCU/CODEC/SWD +49 PLL +1 J101 = 124 footprint** su 141 componenti schematici (17 ancora non piazzati). Il PCB di progetto versionato sarà `04_KiCad/PCB_MASTER_V7.82_PLL_PLACEMENT_WIP/S3900E_MASTER_V782_STAGING_NO_FAB.kicad_pcb`, da materializzare e committare realmente dopo CI KiCad9, non chiamare concluso prima.

**PLL:** LMX2572 U1 package TI RHA0040H 40 lead + EP41 e 9 aperture stencil *non elettriche*; U2/U3 TPS7A2033 con capacità realmente definite nel sorgente; tutte le passive di matching/filtraggio e controllo R/C sono assegnate ai loro pin/reticolo di netlist senza modificare o accorpare le reti esistenti. EP41 e GND PLL rimangono separati da `EFUSE_RTN`, con sorgenti / retorn EMI ancora da qualificare. Le quattro LDO MCU precedenti e J6201 SWD restano fisicamente invariati.

**HOLD critico esplicito:** `Y1` TCXO SG48 7N-12.800MBP-T e suo pin10 AFC/GND non qualificati: **escluso fisicamente**; RFOUT di U1 non instradato; **TX non viene abilitata**. J101 connettore host lato AUX presente come scelta meccanica candidata, **non** autorizza interfacce crossmodule né alimentazione esterna a 3,3V. Nessun short tra `GND_MAIN`, `EFUSE_RTN` e `GND` MCU.

## Gate verificabile

- Caricare effettivamente le impronte vendor/standard `.kicad_mod`, includendo **EP41 rame** di U1 ma ignorando solo le nove aperture `F.Paste` non numerate; qualsiasi pad senza numero su rame genera **FAIL**.
- Riutilizzare netlist KiCad9 nativa del master V7.79 (141 componenti/103 reti): ogni pin della PCB di U1/U2/U3, tutte passive e J101 assegnato alle reti reali; nessun PWR_FLAG o waiver.
- Caricare il PCB V7.81 **già committato** via pcbnew e controllare **tutti i 74 ref, footprint, coordinate, pad e net** prima dell'espansione; nessuna regressione camuffata.
- Salvare/ricaricare PCB generato e produrre DRC nativo **NON RELEASE** con errori reali, da classificare e correggere fisicamente quando giustificato.
- Nessun `Edge.Cuts`, stackup approvato, via, piste, zone o routing RF: l'assenza non è un DRC PASS né una forma di reale produzione.

Ultimo ERC dello schema master: **25 errori, 180 warning** (V7.79), ancora reali. Restano sorgente 13,8V, F200/eFuse/TVS D200 DNP, 5V Ceff, LDO thermal, 15 crossmodule OPEN/HOLD, Y1 pin10, Rx/Tx, enclosure, SFDR, EMC/filtraggio, DFM/termica. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Dopo V7.82: verificare effettivi 17 componenti esclusi, completare RX *solo* con componenti/pin verificati, poi architettura fisica, piano di masse, routing con DRC e independent review prima di richiesta autorizzazione.
