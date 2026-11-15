# V7.78 — ECO reale KiCad U200 TPS26600PWPT, package TI PWP0016H

## Cosa è stato realmente modificato

La libreria **`04_KiCad/Librerie_Footprint_V7.78_TI_PWP0016H_HOLD/S3900E_TI_PWP0016H_Review.pretty/TPS26600_PWP0016H_EXAMPLE_LAND_REVIEW.kicad_mod`** contiene 17 pad logici (16 segnali + thermal pad17) referenziati al disegno produttore Texas Instruments [PWP0016H 4223630/A, 04/2017](https://www.ti.com/lit/ml/pptd333c/pptd333c.pdf), example board layout; confrontare anche [datasheet TPS2660](https://www.ti.com/lit/ds/symlink/tps2660.pdf). Il footprint esistente `Package_SO:TSSOP-16-1EP_4.4x5mm_P0.65mm` è un **generico KiCad**: 16 pad segnale 1.05×0.45, otto primitive di rame tutte numerate EP17, provenienza originaria generica TSSOP-16 e non prova vendor TI. La modifica è una qualifica CAD *candidata*; non pretende compatibilità DFM/sicurezza già provata.

**Misure new candidate dal disegno TI, in mm:** 16 pad lead 1.50 ×0.45, passo 0.65, centri righe sinistra/destra X=±2.90 (5.80 fra i centri), Y da −2.275 a +2.275, centrale EP17 **2.66 ×2.46** a (0,0). Orientamento: pin1 alto sinistra, 8 basso sinistra, 16 alto destra, 9 basso destra. Note importanti: example vendor metal sotto maschera più esteso, note 9 *metal size may vary due to creepage*, via 0.2 mm consigliate solo previa verifica, stencil 0.125mm example. La **forma reale del metallo mascherato/paste, l'assemblaggio e le via termiche** NON sono pienamente qualificati. In questa versione candidato EP17 usa pad di rame/maschera/pasta 2.66×2.46 e nessuna via: realizzarne un layout termico sicuro richiede ulteriore ECO DFM prima di produzione.

`01_EFUSE_AUX.kicad_sch`: **solo** la proprietà `Footprint` di U200 cambia, con valore, MPN, pin e wiring identici. Nuova cartella AUX versionata V7.78 (gli altri tre fogli byte-identici V7.74); master 7sheet versionato punta solo alla nuova cartella AUX, tabelle simboli/progetto conservate, e `fp-lib-table` registra l'impronta versionata. Non vengono cortocircuitati `EFUSE_RTN` (U200.8/17) e `GND_MAIN` (U200.9).

## Gate riproducibile prima di integrare

`03_Verifiche/V7.78/test_ti_pwp0016h_u200_vendor_land_native_v778.py` carica via pcbnew la **vera impronta fisica KiCad9**, misura tutti i 17 pad; nel job CI produce netlist+ERC **prima e dopo** del master completo sette fogli e fallisce se cambia qualsiasi componente oltre U200 footprint, qualsiasi pin-rete, qualsiasi errore/warning originale o se perde la distinzione GND/RTN. Dataset JSON delle dimensioni fisiche nel percorso `03_Verifiche/V7.78/output-ci/`. Esiti da leggere nel run GitHub, NON anticipare successo prima dell'esecuzione.

**Gate ancora OPEN:** effetto del layout EP rame e mask su reverse polarity, creepage e dissipazione; stencil manufacturer/assembler, eventuali via termiche riempite/tentate, criteri package/vendor e tolleranze, eFuse latch-off/SHDN startup, derating F200, Ceff/loop buck, carichi sei 3,3V LDO, 15 cross-module, TX, SG48/Y1 pin10. ERC ultima evidenza V7.74: **28 errori+180 warning**, nessuna PCB radio completa, nessun DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

**Next:** verifica CI, quindi revisionare footprint EP17 con regole del produttore e assemblatore e iniziare posizionamento power-loop su PCB master *solo quando* sorgente/ritorno 13,8V e domini siano definiti. Non usare il conteggio pin-pad per qualificare termica/EMC.
