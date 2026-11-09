from pathlib import Path
import csv, importlib.util, math
b=Path(__file__).parents[2]/'04_KiCad/Modulo_RX_Test_50ohm_V3.2'
with (b/'Piano_Posizionamento_V3.2_PRELIMINARE.csv').open(encoding='utf-8-sig') as f: d=list(csv.DictReader(f))
assert len(d)==15,len(d)
a={v['Ref']:v for v in d}
assert len(a)==15
assert [a[x]['Descrizione'] for x in ['J101','J102','J103','J104']]
assert all(0<float(p['X_mm'])<110 and 0<float(p['Y_mm'])<62 for p in d)
assert all('DA VALIDARE' in a[j]['Stato'] for j in ['J101','J102','J103','J104'])
assert a['J105']['Stato']=='FOOTPRINT DA SELEZIONARE'
for ja,jb in [('J101','J103'),('J102','J104')]:
    dist=abs(float(a[ja]['Y_mm'])-float(a[jb]['Y_mm']))
    assert dist>=25,dist
assert 'ADL5535' in a['U101']['Descrizione']
p=Path(__file__).with_name('microstrip_study_v32.py')
spec=importlib.util.spec_from_file_location('microstrip_study',p)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
z=mod.microstrip_z0(0.34,0.1855,4.74)
assert 49<z<51,z
assert abs(mod.solve_width(.1855,4.74)-.337)<.01
print('V3.2: 10 controlli piano/ingombro/modello nominale SUPERATI; nessun ERC/DRC eseguito')
