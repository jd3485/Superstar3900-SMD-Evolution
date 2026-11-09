# Come riprodurre V6.2

Dalla cartella radice del progetto estratto, con Python 3 standard:

```bash
python 03_Verifiche/V6.2/test_interblocchi_v62.py
python 03_Verifiche/V6.2/simula_soglie_v62.py
```

I file di uscita includono `STUDIO_SOGLIE_V6.2.json`, `CURVA_FINESTRA_V6.2.svg` e `REGRESSIONI_SELEZIONATE_V6.2.json`. La simulazione numerica non utilizza modelli transistor/SPICE. Non modificare J801 per abilitare la TX: è di proposito non montato. Verifiche esterne richieste: schema KiCad, ERC/DRC, qualificazione circuito 13,8V, test di guasto e collaudo analogico hardware.
