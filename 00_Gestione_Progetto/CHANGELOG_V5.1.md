# CHANGELOG V5.1 — 8 novembre 2026

**Base:** archivio cumulativo V5.0. **Modifiche al circuito/schema/footprint:** nessuna. **Rilascio fabbricazione:** VIETATO.

- Generata distinta preliminare del PCB candidato V4.8: 15 riferimenti, 31 pin elettrici unici, 8 reti; stato non approvato e MPN mancanti evidenziati.
- Creati `03_Verifiche/V5.1/genera_bom_net_v51.py`, CSV BOM e pin-rete e rapporto macchina JSON; ideale attenuatore 6,012876 dB a 50 Ω, non misura RF.
- 13/13 test nuovi: includono mutazioni intenzionali di reti, valori, footprint e riferimenti; nessun test equivale a un ERC/DRC nativo.
- Rieseguite con successo le suite V4.0–V5.0, inclusa matrice software 2.400 casi.
- Preparata richiesta tecnica DFM/assemblaggio per PCBWay, **NON INVIATA**; opzioni VIPPO/riempimento/cappatura e stencil richiedono approvazione scritta.
- Tentato aggiornamento degli indici di installazione di KiCad, non completato per timeout. `kicad-cli` e `pcbnew` assenti: ERC/DRC/refill/parità non eseguiti.
- I nove gate della V5.0 restano OPEN, lo stato resta 37% storico stimato / zero hardware validato. Tutti gli storici V5.0 conservati; i documenti attivi aggiornati sono disponibili anche come copie integrali byte-identiche.
