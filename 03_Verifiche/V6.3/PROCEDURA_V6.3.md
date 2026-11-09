# Procedure riproducibili V6.3

Avviare da root dell'archivio con Python 3, **senza KiCad o SPICE richiesti**:

```bash
PYTHONDONTWRITEBYTECODE=1 python -B 03_Verifiche/V6.3/simula_alimentazioni_v63.py
PYTHONDONTWRITEBYTECODE=1 python -B 03_Verifiche/V6.3/test_alimentazioni_v63.py
```

Allegati: SIMULAZIONI_NUMERICHE_V6.3.json, TRANSITORIO_IDEALE_V6.3.csv e AVVIO_ALIMENTAZIONE_V6.3.svg. Fare riferimento alle *ipotesi e ai limiti* nel rapporto. **Non esegue ERC/DRC, SPICE transistor, test TVS/fusibili, EMC o abilitazione RF.**
