# Audit geometrico V4.2 - istruzioni di riproduzione

- Richiede Python >=3.10 e `shapely >=2.0`. Installare in un ambiente virtuale proprio, se necessario.
- Eseguire dalla cartella dell'archivio: `python3 03_Verifiche/V4.2/audit_geometria_rf_v42.py`.
- Eseguire 19 prove di regressione: `python3 03_Verifiche/V4.2/test_geometria_rf_v42.py`.
- Il rapporto viene scritto in `03_Verifiche/V4.2/RISULTATO_GEOMETRIA_RF_V4.2.json`.
- Baseline del PCB V3.8 immutabile con SHA-256 `57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489`.
- Il parser della geometria dipende dal modulo V4.1 e dal parser storico V3.6 già **inclusi nello ZIP**.
- Le superfici sono modellate per F.Cu; nessuna area di piano GND non riempita è considerata conducente. I pad roundrect sono rettangoli conservativi. Nessun controllo della maschera/stencil, tolleranza di fabbricazione, differenziale, zone refill, impedenza coplanare o CAD meccanico ufficiale.
- Non interpretare l'esito come DRC KiCad, ERC, verifica termica o autorizzazione alla produzione.
