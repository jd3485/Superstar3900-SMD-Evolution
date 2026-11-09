## V5.5 — 2026-11-08 — clearance top-copper e validazione dei rapporti (NO FAB)

- Analisi geometrica indipendente `F.Cu` per 44 pad, 44 segmenti, 70 vie; 5.267 coppie cross-net; distanza minima 0,45mm, test soglia 0,30mm superato. Quattro zone GND UNFILLED, NON DRC.
- Postvalidatore di JSON KiCad 10 con protezione su ERC sheets, DRC violations/unconnected_items/schematic_parity e metadati; riporta espressamente che un JSON valido non autentica la provenienza.
- Runner e workflow CI manuale V5.5 pronti ma **NON ESEGUITI su KiCad reale**; KiCad locale assente; NATIVE_NOT_RUN.
- Test software 22/22 nuovi, regressioni V4.0–V5.5 16/16. Nessuna modifica a PCB, schema, librerie o manuale.
- Tutti i nove gate di rilascio V5.0 restano OPEN. Fabbricazione PCBWay e TX bloccate.

---
