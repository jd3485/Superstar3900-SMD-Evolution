## V5.8 — 2026-11-09 — diagnostica geometrica prossimità via GND delle piste RF (NO FAB)

- Analizzati 13 segmenti di 6 reti RF e 70 via GND, campioni ≤0,20 mm su ciascun segmento, bound distanza ≤0,10 mm; max centro-via 9,5811 mm su RF_ATTEN_IN, 6,9385 mm su RF_ATTEN_OUT. Dato NON equivalente a un return path, una violazione RF, un DRC o una regola produttiva.
- Generati verificatore `audit_ritorno_rf_v58.py`, CSV per rete, SVG diagnostico e sorgente, 30 test (incluse mutazioni), lanciatore KiCad 10 fail-closed e rapporto riproducibile.
- 30/30 nuovi test e 19/19 suite di regressione software. KiCad CLI non disponibile: ERC/DRC/refill/parità `NOT_RUN`, 9 gate produttivi OPEN.
- Nessun file KiCad, schemi, librerie, firmware e manuali modificati. Copie integrali dei documenti di gestione aggiornati.

---
