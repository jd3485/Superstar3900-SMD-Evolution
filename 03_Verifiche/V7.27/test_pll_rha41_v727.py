"""TI LMX2572 RHA0040H real native KiCad9 footprint review; NOT FOR FAB / TX."""
import sys,json,unittest
from pathlib import Path
import pcbnew
ROOT=Path(__file__).resolve().parents[2]
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.26_UNIFIED_SYMBOL_LIB_NOT_FOR_FAB"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.27_PLL_RHA41_REVIEW_NOT_FOR_FAB"
OLDAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.26_UNIQUE_SYMBOLS_NOT_FOR_FAB"
NEWAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.27_PLL_RHA41_REVIEW_NOT_FOR_FAB"
FP=ROOT/"04_KiCad/Librerie_Footprint_V7.27_TI_RHA_HOLD/S3900E_TI_RHA_Review.pretty/LMX2572_RHA0040H_VENDOR_CANDIDATE.kicad_mod"
OUT=ROOT/"03_Verifiche/V7.27/output-ci"
OLDFP="Package_DFN_QFN:VQFN-40-1EP_6x6mm_P0.5mm_EP4.35x4.35mm"
NEWFP="S3900E_TI_RHA_V727_HOLD:LMX2572_RHA0040H_VENDOR_CANDIDATE"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
def mm(x):return round(pcbnew.ToMM(x),4)
def geom(p):
 v=p.GetPosition();s=p.GetSize()
 return (mm(v.x),mm(v.y),mm(s.x),mm(s.y))
def expected():
 p={}
 for i in range(10):p[i+1]=(-2.9,round(-2.25+.5*i,2),.6,.25)
 for i in range(10):p[i+11]=(round(-2.25+.5*i,2),2.9,.25,.6)
 for i in range(10):p[i+21]=(2.9,round(2.25-.5*i,2),.6,.25)
 for i in range(10):p[i+31]=(round(2.25-.5*i,2),-2.9,.25,.6)
 p[41]=(0.,0.,4.5,4.5)
 return p
def gate():
 f=pcbnew.FootprintLoad(str(FP.parent),FP.stem)
 assert f is not None,"KiCad native footprint library parser failed"
 pads={};paste=[]
 for pad in f.Pads():
  num=pad.GetNumber();layers=pad.GetLayerSet()
  if num:
   assert num.isdecimal() and int(num) not in pads
   assert layers.Contains(pcbnew.F_Cu) and layers.Contains(pcbnew.F_Mask)
   assert layers.Contains(pcbnew.F_Paste)==(num!="41")
   pads[int(num)]=geom(pad)
  else:
   assert layers.Contains(pcbnew.F_Paste) and not layers.Contains(pcbnew.F_Cu) and not layers.Contains(pcbnew.F_Mask)
   paste.append(geom(pad))
 assert pads==expected(),str(pads)
 assert len(paste)==9 and set(paste)=={(x,y,1.26,1.26) for x in (-1.46,0,1.46) for y in (-1.46,0,1.46)}
 n0=nets(OUT/"v727.original.net");n1=nets(OUT/"v727.revised.net")
 assert len(n0)==100 and n0==n1,"Must conserve all original pin-net connections"
 c0=compmap(OUT/"v727.original.net");c1=compmap(OUT/"v727.revised.net")
 assert len(c0)==len(c1)==132
 assert {ref for ref in c0 if c0[ref]!=c1[ref]}=={"U1"}
 assert c0["U1"]==(OLDFP,"LMX2572RHA")
 assert c1["U1"]==(NEWFP,"LMX2572RHA")
 assert sum(not x[0] for x in c0.values())==sum(not x[0] for x in c1.values())==42
 e0=native_erc(OUT/"v727.original.erc.rpt");e1=native_erc(OUT/"v727.revised.erc.rpt")
 assert (e0["errors"],e0["warnings"])==(36,223)
 assert (e1["errors"],e1["warnings"])==(36,222),(e0,e1)
 t0=(OUT/"v727.original.erc.rpt").read_text();t1=(OUT/"v727.revised.erc.rpt").read_text()
 assert (t0.count("[footprint_link_issues]"),t1.count("[footprint_link_issues]"))==(4,3)
 for rule in ("endpoint_off_grid","label_dangling","power_pin_not_driven","pin_not_driven","lib_symbol_issues"):
  assert t0.count("["+rule+"]")==t1.count("["+rule+"]"),rule
 # TI pin 41 DAP is already one node in the existing AUX GND_MAIN net.
 gnd=[nodes for name,nodes in n1.items() if name.endswith("/GND_MAIN")]
 assert len(gnd)==1 and ("U1","41") in gnd[0]
 result={"revision":"V7.27","pcbnew_version":pcbnew.GetBuildVersion(),
         "native_copper_pad_count":len(pads),"native_paste_windows":len(paste),
         "paste_area_fraction":9*1.26**2/4.5**2,
         "U1_thermal_DAP41_already_GND_MAIN":True,
         "changed_only_U1_review_footprint":True,"components":132,"nets":100,
         "node_deltas":0,"footprints_missing":42,
         "erc_original":[36,223],"erc_revised":[36,222],
         "link_warnings_old":4,"link_warnings_new":3,
         "other_3_footprint_warnings_HOLD":True,
         "15_interfaces_OPEN_HOLD":True,"SG48_HOLD":True,
         "assembly_approved":False,"full_pcb_exists":False,"NO_FAB":True,"NO_TX":True}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"v727.native_rha41_review.json").write_text(json.dumps(result,indent=2)+"\n")
 return result
class TestV727HOLD(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.s=gate()
 def test_01_native_41_pads(self):self.assertEqual(self.s["native_copper_pad_count"],41)
 def test_02_native_paste_9(self):self.assertEqual(self.s["native_paste_windows"],9)
 def test_03_Ti_stencil_ratio(self):self.assertAlmostEqual(self.s["paste_area_fraction"],.7056,4)
 def test_04_reference_unchanged(self):self.assertTrue(self.s["changed_only_U1_review_footprint"])
 def test_05_132_comp_100_net(self):self.assertEqual((self.s["components"],self.s["nets"]),(132,100))
 def test_06_no_net_change(self):self.assertEqual(self.s["node_deltas"],0)
 def test_07_42_missing_remain(self):self.assertEqual(self.s["footprints_missing"],42)
 def test_08_erc_only_one_warning_removed(self):
  self.assertEqual(self.s["erc_original"],[36,223]);self.assertEqual(self.s["erc_revised"],[36,222])
 def test_09_only_one_link_warning_repaired(self):self.assertEqual((self.s["link_warnings_old"],self.s["link_warnings_new"]),(4,3))
 def test_10_EP41_grounds_preserved(self):self.assertTrue(self.s["U1_thermal_DAP41_already_GND_MAIN"])
 def test_11_untouched_aux_byte_identical(self):
  for filename in ("S3900E_AUX_POWER_V1_5.kicad_sch","01_EFUSE_AUX.kicad_sch","02_BUCK_5V.kicad_sch"):
   self.assertEqual((OLDAUX/filename).read_bytes(),(NEWAUX/filename).read_bytes())
 def test_12_only_U1_footprint_source_replaced(self):
  old=(OLDAUX/"03_PLL_LDO_TCXO.kicad_sch").read_text()
  new=(NEWAUX/"03_PLL_LDO_TCXO.kicad_sch").read_text()
  pos=old.index('(property "Reference" "U1"')
  start=old.index('(property "Footprint" "'+OLDFP+'"',pos)
  self.assertLess(start,old.index('(instances ',pos))
  old=old[:start]+old[start:].replace('(property "Footprint" "'+OLDFP+'"','(property "Footprint" "'+NEWFP+'"',1)
  self.assertEqual(old,new)
 def test_13_table_and_schematic_library_hold(self):
  tbl=(NEWROOT/"fp-lib-table").read_text()
  self.assertEqual(tbl.count('(lib (name "S3900E_TI_RHA_V727_HOLD")'),1)
  self.assertEqual((OLDROOT/"sym-lib-table").read_bytes(),(NEWROOT/"sym-lib-table").read_bytes())
 def test_14_holds(self):
  self.assertTrue(self.s["15_interfaces_OPEN_HOLD"] and self.s["SG48_HOLD"])
  self.assertFalse(self.s["assembly_approved"] or self.s["full_pcb_exists"])
  self.assertTrue(self.s["NO_FAB"] and self.s["NO_TX"])
if __name__=="__main__":unittest.main()
