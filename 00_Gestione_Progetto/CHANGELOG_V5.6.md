## V5.6 — 2026-11-08 — continuità topologica del rame F.Cu pre-refill (NO FAB)

- Aggiunto audit indipendente delle isole F.Cu e delle connessioni dei pad, segmenti e via; sette reti non GND continue; 64 gruppi GND sul rame non riempito, di cui 24 con pad e 40 composti solo da via. 4 zone GND da riempire; il numero di gruppi non equivale a violazioni DRC.
- Identità statica del rame V5.2 vs variante termica V4.8 confermata senza modificare CAD.
- Nuovi test 23/23 e regressioni storiche 17/17; runner nativo V5.6 registra NOT_RUN_KICAD_MISSING, GitHub Actions manuale solo predisposta.
- Non chiusi i nove gate V5.0; nessuna autorizzazione PCBWay, PCB o TX.

---
