#!/usr/bin/env python3
import json,importlib.util
from pathlib import Path
p=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rf29',p/'modello_coilcraft_v29.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a=json.loads((p/'Risultati_Coilcraft_V2.9.json').read_text())
for name,e in [('CORE9',m.CORE),('HP3_CORE12',m.HP3+m.CORE)]:
 for k,v in m.metrics(e).items():
  assert abs(v-a[name][k])<1e-8,(name,k,v,a[name][k])
print('PASS: metriche nominali riprodotte e file coerenti')
