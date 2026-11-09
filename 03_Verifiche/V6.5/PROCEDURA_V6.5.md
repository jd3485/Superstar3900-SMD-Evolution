# Ripetizione dei test V6.5

Da cartella radice ZIP estratto (Python ≥3.10, numpy, matplotlib):

```bash
python -B 03_Verifiche/V6.5/simula_mixer_fi_v65.py
python -B 03_Verifiche/V6.5/test_mixer_fi_v65.py
```

Il simulatore usa risposta ideale Butterworth e FFT di un prodotto di coseni. **Nessuna soluzione SPICE, S-parameter, misura fisica o validazione di prestazione hardware**. La tabella CSV contiene tutte le 270 frequenze e la reiezione soltanto ideale. Il tester esegue 50 assert di test indipendenti, con 128 combinazioni logiche esaustive e 10.000 ingressi pseudo-casuali; non è una misura RF.

Suite regresse selezionate, modalità immutabile (`-B` e `PYTHONDONTWRITEBYTECODE=1`): V5.9/V6.0/V6.1×2/V6.2/V6.3/V6.4. I vecchi test geometrici e il KiCad nativo rimangono nel progetto ma **non si dichiara qui di avere eseguito l'intera storia**.
