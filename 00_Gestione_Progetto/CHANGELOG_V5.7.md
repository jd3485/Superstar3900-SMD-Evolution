## V5.7 — 2026-11-08 — contorno teorico piani GND, nessuna modifica al PCB (NO FAB)

- Studio geometrico su zone UNFILLED dei quattro layer: stima permissiva F.Cu 6.323,1039 mm² / 6.581,16 mm² (96,08%), una regione ideale per layer, 70/70 via completamente entro ciascun contorno, margine minimo del bordo rame-via al contorno 2,05 mm.
- Il modello non calcola fill KiCad, spoke termici, clearance netclass prevalente, min-neck, isole rimosse; nessuna prova di connessione RF reale né produzione.
- Test V5.7 30/30, regressioni V4.0–V5.7 18/18, runner KiCad locale NOT_RUN_KICAD_MISSING, workflow CI soltanto predisposto.
- Sorgenti KiCad, firmware e manuale illustrato immutati; 9 gate di rilascio V5.0 aperti.

---
