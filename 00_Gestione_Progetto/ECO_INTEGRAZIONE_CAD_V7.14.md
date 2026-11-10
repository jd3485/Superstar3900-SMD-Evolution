# ECO V7.14 — risoluzione librerie KiCad, warning RX e diagnosi footprint

**10 novembre 2026. Baseline V7.13 `main` `02f2aeaa4f1a37c232a3840016bf743f71ab8424`. NO FAB / NO TX.**

1. Ripristinato un **progetto KiCad effettivo** per coupon RX, con `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, libreria simboli locale e tabelle footprint e simboli. Non è un modello solo testuale: GitHub Actions esegue `kicad-cli` nativo su tutti e tre gli artefatti. Lo schema e il PCB mantengono **le stesse nets/componenti/pin e tutto il rame** delle versioni precedenti.
2. Risolta la causa delle **15 lib_symbol_issues +15 footprint_link_issues**: senza `.kicad_pro` le tabelle locali `sym-lib-table`/`fp-lib-table` venivano ignorate dal CLI. Il primo esperimento di mera copia simboli aveva ancora 30 warning, mentre il vero file di progetto li ha portati **30→0** (ERC RX 0 errori/0 warning), con severità e controlli invariati.
3. `kicad-cli pcb drc` sul file PCB identico e con librerie caricate passa da **85→72 violazioni**: restano **70 via_dangling** e **2 lib_footprint_mismatch** su **J9102/J9104** che richiedono documenti vendor. Le **63 unconnected** restano invariate. Non è DRC PASS; non sono stati cancellati o disabilitati marker.
4. Nuova gerarchia KiCad V7.14 con `.kicad_pro` collega sette fogli (power V1.5, MCU V7.12, RX V7.14) **solo gerarchicamente**. Netlist native **99→99 identiche per (nome rete, ref, pin)**. ERC root **43 errori invariati**, warning **370→340**; le 15 interfacce sono ancora OPEN/HOLD, senza rail o bus collegati.
5. Nuovo script `03_Verifiche/V7.14/probe_library_erc_v714.py` impone ERC RX 30→0 e netlist RX identica, `verifica_root_kicad_v714.py` prova netlist root e non-regressione ERC, 15 test sorgenti di progetto, storico DSP/firmware/PLL da V7.1 a V7.13 in regressione.
6. Nessun nuovo test Icarus/Yosys o laboratorio in V7.14. I risultati di vecchie revisioni restano storici; non inventare un PASS sulla fabbricazione.
7. Prossima V7.15: comparazione pad reali SMA/J9102/J9104, GND via-in-pad e zone copper, routing pad/net nelle 63 unconnected, root power ERC 43 e certificazione pin/rail vendor. Il codice DSP e firmware resta parte integrante del progetto.

**NESSUN PCB completo, Gerber, prototipo, PA/antenna o TX autorizzati. NO FAB / NO TX.**
