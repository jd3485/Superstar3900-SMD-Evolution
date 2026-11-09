"""Monte Carlo idealized contact timing on panel switches.
Random bounce is a synthetic test, not a physical measurement or SPICE.
"""
from pathlib import Path
import importlib.util,sys,json,random
HERE=Path(__file__).resolve();ROOT=HERE.parents[2]
p=ROOT/'08_Firmware_Prototipi/V6.1/panel_controller_v61.py'
spec=importlib.util.spec_from_file_location('panel_controller_v61',p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
F=m.load_frequency_table(ROOT/'02_Piano_Frequenze'/'Tabella_270_canali.csv')
def run(trials=2000,seed=20261109):
 rnd=random.Random(seed)
 results=[];invalid_during_bounce=0
 for _ in range(trials):
  c=m.Controller(F)
  for i in range(4):c.update(m.Inputs(bands=('D',)))
  end_bounce=rnd.randrange(0,20,5)
  states=[]
  for ms in range(0,65,5):
   if ms<end_bounce:
    new=rnd.choice([(),('D',),('F',),('D','F')])
   else:new=('F',)
   v=c.update(m.Inputs(bands=new))
   if ms<end_bounce and v.rx_mute:invalid_during_bounce+=1
   if v.state.startswith('RX') and v.band=='F':states.append(ms)
   assert v.rf_tx_permission is False
  assert states, 'did not settle into F after bounce'
  results.append(states[0])
 return {'model':'RANDOM_CONTACT_BOUNCE_TIMING_NOT_PHYSICAL_MEASUREMENT',
         'seed':seed,'trials':trials,'sample_interval_ms':5,'stable_samples':4,
         'max_bounce_duration_ms':15,'min_settle_ms':min(results),'max_settle_ms':max(results),
         'average_settle_ms':sum(results)/len(results),'bounces_muted':invalid_during_bounce,
         'tx_permission_observed':False}
if __name__=='__main__':
 d=run();print(json.dumps(d,indent=2))
