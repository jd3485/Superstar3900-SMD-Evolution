# Rapporto di avanzamento V4.1 — Preflight geometrico e attenuatore RF

Data 2026-11-08. **NO FAB / NO PCBWAY.** RX V3.8 non modificato. 37% stima progettuale invariata e 0 moduli hardware collaudati.

## Risultati verificabili

- La sorgente originale PCB ha SHA-256 `57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489` (identico a V3.9).
- Rilevati 15 footprint, 8 reti, 44 segmenti, 64 via e 4 zone dichiarate ma **non riempite**; bordo 110×62 mm.
- J101–J104: piazzola centrale Ø2,05 mm; quattro regioni GND custom per connettore; estensione Y locale 7,40 mm contro 7,76 mm di riferimento TE. Nessuna equivalenza approvata, differenza -0,36 mm.
- U101: paddle 1,80×3,48 mm, parametro di riduzione pasta -0,10, **0** centri via all'interno dell'area paddle; via GND più vicino esterno a 0,50 mm tra i bordi, con pista diretta F.Cu alla piazzola. La geometria e la conduzione termica reale sono da validare.
- R201/R203/R202 nominali 150/37,4/150 Ω: attenuatore π ideale a 50 Ω con attenuazione 6,012876 dB e return loss d'ingresso 67,035926 dB; valori di calcolo, non risultati di VNA. Analisi ipotetica ±1%: perdita 5,9553–6,0710 dB; peggior return loss 47,5113 dB nel modello ideale.
- Dati ADI: alimentazione 5 V, Iq tipica 97 mA, ~0,485 W elettrici a riposo; assoluto massimo dissipazione interna con paddle saldato 650 mW, θJA 30,7 °C/W. Non ricavare margine di affidabilità definitivo.

## Evidenze testabili

Da root dell'archivio:

```bash
python3 03_Verifiche/V4.1/audit_rf_v41.py
python3 03_Verifiche/V4.1/test_audit_rf_v41.py
```

Esito registrato: **12/12 test software statici superati**, output JSON in `03_Verifiche/V4.1/ESITO_PREFLIGHT_RF_V4.1.json`. Il controllo non richiede né sostituisce KiCad.

Quando disponibile KiCad **10 o superiore**, eseguire lo script `03_Verifiche/V4.1/RUN_KICAD_NATIVE_V4.1.sh` su macchina con librerie adeguate. Lo script copia il PCB per refill+DRC e copia lo schema V3.1 per ERC; se l'applicativo manca o non supporta refill non dichiara successi. Se DRC/ERC riescono rimangono comunque APERTI altri cancelli (TE, termica, impedenza, collaudi).

## Decisione

Nessun rilascio progettuale a produzione. Lasciare PCB V3.8 intatto e manuale d'uso PDF V4.0 come bozza ufficiale. Nessun collegamento TX. V4.1 è un incremento dei controlli e della tracciabilità, non un avanzamento del collaudo RF.
