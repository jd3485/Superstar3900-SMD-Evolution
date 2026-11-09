#!/usr/bin/env python3
from pathlib import Path
import csv,json,unittest
ROOT=Path(__file__).resolve().parents[2]
V=ROOT/'03_Verifiche/V2.6'
class RevisionV26(unittest.TestCase):
 def test_vendor_Q_not_27MHz(self):
  with (ROOT/'07_Componenti/Induttori_Coilcraft_0805CS_Candidati_V2.6.csv').open() as f: rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),4)
  self.assertTrue(all(float(r['Q_test_MHz'])==250 for r in rows))
  self.assertTrue(all(r['Q_at_27MHz'].startswith('UNKNOWN') for r in rows))
 def test_all_bands_and_Q(self):
  with (V/'Confronto_Pari_Q_V2.6.csv').open() as f: rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),30)
  self.assertEqual(set(x['band'] for x in rows),set('ABCDEF'))
  self.assertEqual(set(int(x['Q_assumed']) for x in rows),{20,30,45,60,90})
 def test_switch_loss_offset(self):
  with (V/'Confronto_Pari_Q_V2.6.csv').open() as f: entries=list(csv.DictReader(f))
  for r in entries:
   x=float(r['bank_3tank_pre_switch_max_loss_dB'])
   self.assertAlmostEqual(float(r['bank_plus_2relais_assumed_loss_dB'])-x,0.4,places=7)
   self.assertAlmostEqual(float(r['bank_plus_2SOI_assumed_loss_dB'])-x,1.4,places=7)
 def test_Q_monotonic_loss(self):
  with (V/'Sintesi_Pari_Q_V2.6.csv').open() as f: rows=list(csv.DictReader(f))
  for col in ['one_filter_loss_max_dB','bank_ideal_loss_max_dB']:
   x=[float(r[col]) for r in rows]
   self.assertTrue(all(a>b for a,b in zip(x,x[1:])))
 def test_L_stress_unretuned(self):
  with (V/'Sensibilita_Valori_L_Commerciali_V2.6.csv').open() as f: rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),18)
  self.assertTrue(all(r['cap_reoptimized']=='NO' for r in rows))
 def test_no_manufacturing_approval(self):
  r=json.loads((V/'Risultati_V2.6.json').read_text())
  self.assertFalse(r['qualified_Q_27MHz'])
  self.assertTrue(r['decision'].startswith('NO-GO'))
  self.assertEqual(r['progress_estimate_pct'],33)
if __name__=='__main__':unittest.main(verbosity=2)
