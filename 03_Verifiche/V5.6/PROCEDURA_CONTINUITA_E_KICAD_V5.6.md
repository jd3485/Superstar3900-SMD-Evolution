# V5.6 — Procedura verifica continuità F.Cu e successivo KiCad 10 (NO FAB)

## 1. Audit statico immediato

Con Python 3.10+ e Shapely 2 installato, dalla radice dell'archivio:

```bash
python -m pip install 'shapely>=2,<3'
python -B 03_Verifiche/V5.6/audit_continuita_fcu_v56.py --output REPORT_V5.6/AUDIT_CONTINUITA_FCU.json
python -B 03_Verifiche/V5.6/test_continuita_v56.py
```

**Atteso sul PCB V5.2 immutato:** 7 reti di segnale continue su F.Cu, 64 isole GND prima del riempimento (24 con pad, 40 via-only), 4 zone GND senza fill, `STATIC_TOPOLOGY_PASS_GROUND_PENDING`; 23/23 test. Questo non è KiCad DRC.

## 2. Esecuzione nativa su computer con KiCad 10

```bash
python -B 03_Verifiche/V5.6/run_kicad_e_topologia_v56.py --output REPORT_V5.6
```

Il programma esegue prima l'audit statico e, **solo se `kicad-cli` è disponibile**, invoca il runner KiCad V5.5 che crea una copia dei sorgenti e richiede ERC e DRC con refill+parità. Se l'eseguibile manca, il comando termina con codice 5 e scrive `STATUS_V5.6.json` con `NOT_RUN_KICAD_MISSING`. Se i report sono presenti ma falliscono, l'esito resta di errore. Un codice zero non autorizza mai fabbricazione: serve revisione umana dei report e chiusura esplicita dei nove gate V5.0.

**Nessuna scheda Gerber deve essere inviata al produttore sulla base del test statico o del mero codice zero.**

## 3. GitHub Actions (solo se un utente carica il repository)

Il workflow `.github/workflows/kicad_native_v56.yml` è predisposto per avvio manuale (`workflow_dispatch`). Richiede un repository contenente tutte le directory dell'archivio; pubblica i report come artifact anche su errore. **Non è stato eseguito o installato su GitHub in questa sessione.** Verificare concretamente il PPA e le dipendenze sul runner prima dell'uso.

## 4. Criteri per iniziare una revisione PCB

Verificare nel DRC nativo i poligoni GND su tutti e 4 gli strati e tutte le voci `unconnected_items`, oltre a errori di interclearance e differenze schema-PCB. Registrare i report originali e la versione KiCad. Qualsiasi correzione deve avvenire su una nuova copia candidata, con confronto hash e review; non alterare PCB V3.8, V4.8 o V5.2 storici. Continuano i blocchi per TE SMA e per pad termico ADL5535.
