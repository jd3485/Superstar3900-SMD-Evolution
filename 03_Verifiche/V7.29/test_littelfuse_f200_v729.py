"""Littelfuse 045101.5MRL F200 native KiCad9 manufacturer land review: no fab/TX."""
import unittest,json,sys
from pathlib import Path
import pcbnew
ROOT=Path(__file__).resolve().parents[2]
OR=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.28_L100_BOURNS_REVIEW_NOT_FOR_FAB"
NR=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.29_F200_LITTELFUSE_REVIEW_NOT_FOR_FAB"
OA=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.28_L100_BOURNS_REVIEW_NOT_FOR_FAB"
NA=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.29_F200_LITTELFUSE_REVIEW_NOT_FOR_FAB"
FP=ROOT/"04_KiCad/Librerie_Footprint_V7.29_LITTELFUSE_451_HOLD/S3900E_LF451_Review.pretty/LF451_045101_5MRL_VENDOR_CANDIDATE.kicad_mod"
OUT=ROOT/"03_Verifiche/V7.29/output-ci"
OLDFP="S3900E:LF_451_FOOTPRINT_NON_VALIDATO"
NEWFP="S3900E_LF451_V729_HOLD:LF451_045101_5MRL_VENDOR_CANDIDATE"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
def mm(n):return round(pcbnew.ToMM(n),4)
def coordinates(p):
 a=p.GetPosition();b=p.GetSize()
 return(mm(a.x),mm(a.y),mm(b.x),mm(b.y))
def gate():
 f=pcbnew.FootprintLoad(str(FP.parent),FP.stem)
 assert f is not None
 pads={}
 for p in f.Pads():
  num=p.GetNumber();layers=p.GetLayerSet()
  assert num in ("1","2") and num not in pads
  assert layers.Contains(pcbnew.F_Cu) and layers.Contains(pcbnew.F_Mask) and layers.Contains(pcbnew.F_Paste)
  pads[num]=coordinates(p)
 assert pads=={"1":(-2.4525,0.0,1.955,3.15),"2":(2.4525,0.0,1.955,3.15)}
 # Exact nominal overall 6.86 and gap 2.95 from manufacturer recommended land; pad width
 # 1.955 derived, manufacturer diagram prints rounded 1.96 mm.
 assert abs((pads["2"][0]+pads["2"][2]/2)-(pads["1"][0]-pads["1"][2]/2)-6.86)<1e-6
 assert abs((pads["2"][0]-pads["2"][2]/2)-(pads["1"][0]+pads["1"][2]/2)-2.95)<1e-6
 a=compmap(OUT/"v729.original.net");b=compmap(OUT/"v729.revised.net")
 assert len(a)==len(b)==132 and {k for k in a if a[k]!=b[k]}=={"F200"}
 assert a["F200"]==(OLDFP,"1.5A 045101.5MRL CANDIDATO")
 assert b["F200"]==(NEWFP,"1.5A 045101.5MRL CANDIDATO")
 assert sum(not x[0] for x in b.values())==42
 n0=nets(OUT/"v729.original.net");n1=nets(OUT/"v729.revised.net")
 assert len(n0)==100 and n0==n1
 e0=native_erc(OUT/"v729.original.erc.rpt");e1=native_erc(OUT/"v729.revised.erc.rpt")
 assert (e0["errors"],e0["warnings"])==(36,221)
 assert (e1["errors"],e1["warnings"])==(36,220),(e0,e1)
 t0=(OUT/"v729.original.erc.rpt").read_text();t1=(OUT/"v729.revised.erc.rpt").read_text()
 assert (t0.count("[footprint_link_issues]"),t1.count("[footprint_link_issues]"))==(2,1)
 for rule in ("endpoint_off_grid","label_dangling","power_pin_not_driven","pin_not_driven","lib_symbol_issues"):
  assert t0.count("["+rule+"]")==t1.count("["+rule+"]"),rule
 # Manufacturer 2025 451 datasheet: rated 1.5A 125V AC/DC, cold R 0.063ohm,
 # I2t 0.853A2s and 25% recommended continuous current derating.
 nominal=1.5;continuous_upper=nominal*.75
 assert continuous_upper==1.125
 assert nominal*.063==.0945
 assert .85<.853<.86
 d={"rev":"V7.29","KiCad9":pcbnew.GetBuildVersion(),"pads":pads,
    "land_outer_mm":6.86,"land_inner_gap_mm":2.95,
    "manufacturer":"Littelfuse","MPN":"045101.5MRL","rated_A":nominal,
    "rated_V_DC":125,"cold_R_ohm":.063,"melting_I2t_A2s":.853,
    "continuous_derated_A_25C_pre_temp":continuous_upper,
    "full_13V8_input_current_known":False,"fault_breaking_capacity_qualified":False,
    "inrush_I2t_qualified":False,"fuse_fabrication_approved":False,
    "components":132,"nets":100,"net_delta":0,"missing_footprints":42,
    "changed_only_F200_footprint":True,"erc_before":[36,221],"erc_after":[36,220],
    "footprint_link_before":2,"footprint_link_after":1,"Y1_still_unvalidated":True,
    "15_interfaces_OPEN_HOLD":True,"SG48_HOLD":True,"NO_FAB":True,"NO_TX":True}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"v729.native_littelfuse_f200.json").write_text(json.dumps(d,indent=2)+"\n")
 return d
class TestF200FuseHOLD(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=gate()
 def test_01_native_package_two_pads(self):self.assertEqual(len(self.d["pads"]),2)
 def test_02_vendor_outer_span(self):self.assertEqual(self.d["land_outer_mm"],6.86)
 def test_03_vendor_inner_gap(self):self.assertEqual(self.d["land_inner_gap_mm"],2.95)
 def test_04_original_mpn_schematic_retained(self):self.assertEqual(self.d["MPN"],"045101.5MRL")
 def test_05_only_f200_link_changed(self):self.assertTrue(self.d["changed_only_F200_footprint"])
 def test_06_nets_all_unchanged(self):self.assertEqual((self.d["components"],self.d["nets"],self.d["net_delta"]),(132,100,0))
 def test_07_42_missing_still(self):self.assertEqual(self.d["missing_footprints"],42)
 def test_08_exact_one_warning_repaired(self):self.assertEqual((self.d["erc_before"],self.d["erc_after"]),([36,221],[36,220]))
 def test_09_one_Y1_link_warning_remains(self):self.assertEqual(self.d["footprint_link_after"],1)
 def test_10_25_percent_derating_not_waived(self):self.assertEqual(self.d["continuous_derated_A_25C_pre_temp"],1.125)
 def test_11_no_inrush_or_breaking_assumption(self):self.assertFalse(self.d["inrush_I2t_qualified"] or self.d["fault_breaking_capacity_qualified"])
 def test_12_unchanged_other_aux_byte_identical(self):
  for file in ("S3900E_AUX_POWER_V1_5.kicad_sch","02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch"):
   self.assertEqual((OA/file).read_bytes(),(NA/file).read_bytes())
 def test_13_f200_is_only_schematic_footprint_modification(self):
  old=(OA/"01_EFUSE_AUX.kicad_sch").read_text()
  new=(NA/"01_EFUSE_AUX.kicad_sch").read_text()
  pos=old.index('(property "Reference" "F200"')
  fp=old.index('(property "Footprint" "'+OLDFP+'"',pos)
  self.assertLess(fp,old.index('(instances ',pos))
  expected=old[:fp]+old[fp:].replace('(property "Footprint" "'+OLDFP+'"','(property "Footprint" "'+NEWFP+'"',1)
  self.assertEqual(new,expected)
 def test_14_lib_still_HOLD(self):
  self.assertEqual((OR/"sym-lib-table").read_bytes(),(NR/"sym-lib-table").read_bytes())
  self.assertEqual((NR/"fp-lib-table").read_text().count('(lib (name "S3900E_LF451_V729_HOLD")'),1)
  self.assertTrue(self.d["NO_FAB"] and self.d["NO_TX"] and self.d["SG48_HOLD"])
if __name__=="__main__":unittest.main()
