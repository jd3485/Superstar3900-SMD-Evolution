# Istruzioni V5.3: validazione con KiCad 10 e ripresa

1. Estrarre completamente `Superstar3900_SMD_Evolution_V5.3.zip`. Non lanciare KiCad direttamente dentro lo ZIP.
2. Nella radice, eseguire `python3 -B 03_Verifiche/V5.3/audit_indipendente_v53.py` e `python3 -B 03_Verifiche/V5.3/run_regressioni_v53.py` (Python 3.10 o superiore). I test sono **statici** e richiedono soltanto la libreria standard.
3. Aprire `04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB`. I file `.kicad_sch` e `.kicad_pcb` hanno lo stesso nome base; gli archivi `.pretty`, il file `.kicad_sym` e le tabelle sono portabili e incluse.
4. Verificare da terminale che `kicad-cli version` riporti 10.x. Eseguire dalla radice il comando `python3 03_Verifiche/V5.2/run_kicad_v52.py --output REPORT_NATIVE_V5.3`. La procedura è fail-closed e lavora su copia; se non può produrre i rapporti, segnala `NOT_RUN` o `FAILED_OR_INCOMPLETE`.
5. Esaminare i rapporti ERC e DRC completi e controllare **anche** le voci di parità schema/PCB, le zone riempite, gli eventuali elementi non connessi, gli avvisi e le esclusioni. Allegare i report alla chat di ripresa per creare una copia corretta.
6. Non ordinare PCB. Per abilitare la produzione occorrono anche CAD TE verificato, risposta DFM scritta VIPPO/stencil, termica, stack-up RF, BOM completa e collaudi.

**Nota:** nessuna funzionalità TX deve essere abilitata. Conservare sempre i vecchi file con hash e snapshot integrali.
