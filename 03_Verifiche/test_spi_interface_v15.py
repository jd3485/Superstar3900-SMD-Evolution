"""V1.5 static net contract test. NOT KiCad native ERC/netlist."""
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from sexpr_geometry_v14 import get_pin_points,child,children,pos
P=ROOT/'04_KiCad'/'Gerarchico_Alimentazioni_V1.5'
EXPECTED={'PLL_SCK':('16','input',1), 'PLL_SDI':('17','input',2), 'PLL_CSB':('24','input',3), 'PLL_CE':('1','input',4), 'PLL_MUXOUT':('20','output',5)}
class TestSpiConnections(unittest.TestCase):
 def test_root_and_child_pins(self):
    root=get_pin_points(P/'S3900E_AUX_POWER_V1_5.kicad_sch')
    leaf=get_pin_points(P/'03_PLL_LDO_TCXO.kicad_sch')
    ps={n['name']:n for n in root['pins'] if n['ref']=='J101'}
    labels={(n['name'], n['coord']) for n in root['labels']}
    hlabels={(n['name'], n['coord']) for n in leaf['labels'] if n['kind']=='hierarchical_label'}
    root_sheetpins={p[1]:p for s in children(root['root'],'sheet') for p in children(s,'pin')}
    for name,(pinnum,kind,jpin) in EXPECTED.items():
       onchip=next(n for n in leaf['pins'] if n['ref']=='U1' and n['pin']==pinnum)
       # A child hierarchical label must touch that chip pin through a wire segment:
       possible=[p for n,p in hlabels if n==name]
       self.assertEqual(len(possible),1)
       all_endpoints={c for w in leaf['wires'] for c in w}
       self.assertTrue(possible[0] == onchip['coord'] or (possible[0] in all_endpoints and onchip['coord'] in all_endpoints),(name,onchip))
       self.assertIn(name,root_sheetpins)
       self.assertEqual(root_sheetpins[name][2],kind)
       xy=pos(child(root_sheetpins[name],'at'))
       self.assertIn((name,xy),labels)
       host=next(n for n in root['pins'] if n['ref']=='J101' and n['pin']==str(jpin))
       self.assertIn((name,host['coord']),labels)
    g=next(n for n in root['pins'] if n['ref']=='J101' and n['pin']=='6')
    self.assertIn(('GND_MAIN',g['coord']),labels)
 def test_project_paths(self):
    for p in P.glob('*.kicad_sch'):
     self.assertIn('S3900E_AUX_POWER_V1_5',p.read_text(),p.name)
if __name__=='__main__': unittest.main()
