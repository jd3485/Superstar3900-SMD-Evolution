# V6.4 — controlli riproducibili

Dalla root dello ZIP estratto, con Python 3 e senza KiCad:

```bash
PYTHONDONTWRITEBYTECODE=1 python -B 03_Verifiche/V6.4/simula_pll_v64.py
PYTHONDONTWRITEBYTECODE=1 python -B 03_Verifiche/V6.4/genera_elaborati_pll_v64.py
PYTHONDONTWRITEBYTECODE=1 python -B 03_Verifiche/V6.4/test_pll_v64.py
```

Il primo comando rigenera CSV 270 RX e JSON Monte Carlo con seme fissato. Il secondo rigenera BOM, pin/reti, diagramma e documenti progettuali. Il terzo fa 60 test, incluso un fuzzing di 10.000 transizioni della logica RX/PLL. **Nessuno dei tre modifica file storici precedenti alla V6.4**.

Non eseguiti: TICS Pro e veri registri 126-word, KiCad native ERC/DRC, NGSpice modello vendor, phase noise, spettro, VNA, misure elettriche e hardware. TX disabilitata.
