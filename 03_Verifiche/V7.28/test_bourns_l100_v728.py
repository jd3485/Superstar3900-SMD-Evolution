"""Bourns SRP1038A-150M L100 vendor land review - NO FAB/TX."""
import json,math,sys,unittest
from pathlib import Path
import pcbnew
ROOT=Path(__file__).resolve().parents[2]
OR=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.27_PLL_RHA41_REVIEW_NOT_FOR_FAB"
NR=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.28_L100_BOURNS_REVIEW_NOT_FOR_FAB"
OA=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.27_PLL_RHA41_REVIEW_NOT_FOR_FAB"
NA=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.28_L100_BOURNS_REVIEW_NOT_FOR_FAB"
FP=ROOT/"04_KiCad/Librerie_Footprint_V7.28_BOURNS_L100_HOLD/S3900E_Bourns_Review.pretty/SRP1038A_150M_BOURNS_VENDOR_CANDIDATE.kicad_mod"
OUT=ROOT/"03_Verifiche/V7.28/output-ci"
OLDFP="Inductor_SMD:L_10.0x10.0_H5.0"
NEWFP="S3900E_BOURNS_SRP1038A_V728_HOLD:SRP1038A_150M_BOURNS_VENDOR_CANDIDATE"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
def mm(x):return round(pcbnew.ToMM(x),4)
def geom(p):
 a=p.GetPosition();b=p.GetSize()
 return(mm(a.x),mm(a.y),mm(b.x),mm(b.y))
def ripple(vin,vout,ind,freq):
 return vout*(1-vout/vin)/(ind*freq)
def gate():
 f=pcbnew.FootprintLoad(str(FP.parent),FP.stem)
 assert f is not None
 pads={}
 for pad in f.Pads():
  n=pad.GetNumber();l=pad.GetLayerSet()
  assert n in ("1","2") and n not in pads
  assert l.Contains(pcbnew.F_Cu) and l.Contains(pcbnew.F_Mask) and l.Contains(pcbnew.F_Paste)
  pads[n]=geom(pad)
 assert pads=={"1":(-4.75,0.,4.1,3.5),"2":(4.75,0.,4.1,3.5)}
 assert abs(pads["2"][0]+2.05-(-pads["1"][0]-2.05)-5.4)<1e-6
 # This Bourns drawing gives 13.6mm EXTERNAL span and 5.4mm INTERNAL gap.
 assert (pads["2"][0]+pads["2"][2]/2)-(pads["1"][0]-pads["1"][2]/2)==13.6
 old=compmap(OUT/"v728.original.net");new=compmap(OUT/"v728.revised.net")
 assert len(old)==len(new)==132
 assert {ref for ref in old if old[ref]!=new[ref]}=={"L100"}
 assert old["L100"]==(OLDFP,"15uH / 3.5A")
 assert new["L100"]==(NEWFP,"15uH SRP1038A-150M")
 assert sum(not x[0] for x in new.values())==42
 n0=nets(OUT/"v728.original.net");n1=nets(OUT/"v728.revised.net")
 assert len(n0)==100 and n0==n1
 er0=native_erc(OUT/"v728.original.erc.rpt");er1=native_erc(OUT/"v728.revised.erc.rpt")
 assert (er0["errors"],er0["warnings"])==(36,222)
 assert (er1["errors"],er1["warnings"])==(36,221),(er0,er1)
 t0=(OUT/"v728.original.erc.rpt").read_text();t1=(OUT/"v728.revised.erc.rpt").read_text()
 assert (t0.count("[footprint_link_issues]"),t1.count("[footprint_link_issues]"))==(3,2)
 for rule in ("endpoint_off_grid","label_dangling","power_pin_not_driven","pin_not_driven","lib_symbol_issues"):
  assert t0.count("["+rule+"]")==t1.count("["+rule+"]"),rule
 # TI TPS54202 2026 Rev C: f 390..630 kHz, output rated <=2A, Vin <=28V.
 # Bourns SRP1038A-150M: L=15uH +/-20%, Isat=10A/25C, Irms=6.25A, DCR(max)=0.045 ohm.
 worst_ripple=ripple(28.,5.0772030075,12e-6,390e3)
 ipk=2.+worst_ripple/2
 dc_loss=(2**2+worst_ripple**2/12)*.045
 assert 0.8<worst_ripple<0.95 and 2.4<ipk<2.5
 assert ipk<10 and dc_loss<.20
 data={"rev":"V7.28","pcbnew":pcbnew.GetBuildVersion(),"component":132,"nets":100,
       "node_delta":0,"only_L100_MPN_value_and_footprint_changed":True,
       "missing_footprints":42,"ERC_before":[36,222],"ERC_after":[36,221],
       "footprint_link_before":3,"footprint_link_after":2,
       "Bourns_MPN":"SRP1038A-150M","L_uH_nominal":15,"L_uH_min_20pct":12,
       "DCR_max_ohm":.045,"Irms_25C_A":6.25,"Isat_25C_A":10,
       "buck_VOUT_V":5.0772030075,"Vin_worst_envelope_V":28,"f_min_Hz":390000,
       "buck_max_output_A":2,"max_ripple_A":worst_ripple,"peak_current_A":ipk,"winding_DC_loss_W":dc_loss,
       "native_pads":pads,"thermal_board_qualified":False,"real_design_output_load_measured":False,
       "15_crossmodule_HOLD":True,"SG48_HOLD":True,"NO_FAB":True,"NO_TX":True}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"v728.native_bourns_review.json").write_text(json.dumps(data,indent=2)+"\n")
 return data
class TestBournsL100Review(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=gate()
 def test_01_two_native_bourns_land_pads(self):self.assertEqual(len(self.d["native_pads"]),2)
 def test_02_real_mpn(self):self.assertEqual(self.d["Bourns_MPN"],"SRP1038A-150M")
 def test_03_worst_case_peak_below_25C_Isat(self):self.assertLess(self.d["peak_current_A"],self.d["Isat_25C_A"])
 def test_04_worst_case_DC_loss_recorded(self):self.assertLess(self.d["winding_DC_loss_W"],.20)
 def test_05_MPN_and_fp_one_component_only(self):self.assertTrue(self.d["only_L100_MPN_value_and_footprint_changed"])
 def test_06_132_comp_100_net_no_delta(self):self.assertEqual((self.d["component"],self.d["nets"],self.d["node_delta"]),(132,100,0))
 def test_07_missing_footprints_42(self):self.assertEqual(self.d["missing_footprints"],42)
 def test_08_only_one_footprint_warning_removed(self):self.assertEqual((self.d["ERC_before"],self.d["ERC_after"]),([36,222],[36,221]))
 def test_09_no_fake_warranty(self):self.assertFalse(self.d["thermal_board_qualified"] or self.d["real_design_output_load_measured"])
 def test_10_AUX_parent_PLL_EFUSE_identical(self):
  for name in ("S3900E_AUX_POWER_V1_5.kicad_sch","01_EFUSE_AUX.kicad_sch","03_PLL_LDO_TCXO.kicad_sch"):
   self.assertEqual((OA/name).read_bytes(),(NA/name).read_bytes())
 def test_11_only_l100_fields_changed_on_buck_sheet(self):
  old=(OA/"02_BUCK_5V.kicad_sch").read_text()
  pos=old.index('(property "Reference" "L100"')
  self.assertLess(old.index('(property "Footprint" "'+OLDFP+'"',pos),old.index('(instances ',pos))
  wanted=old[:pos]+old[pos:].replace('(property "Value" "15uH / 3.5A"','(property "Value" "15uH SRP1038A-150M"',1).replace('(property "Footprint" "'+OLDFP+'"','(property "Footprint" "'+NEWFP+'"',1)
  self.assertEqual(wanted,(NA/"02_BUCK_5V.kicad_sch").read_text())
 def test_12_safe_project_symbol_registry(self):
  self.assertEqual((OR/"sym-lib-table").read_bytes(),(NR/"sym-lib-table").read_bytes())
  s=(NR/"fp-lib-table").read_text()
  self.assertEqual(s.count('(lib (name "S3900E_BOURNS_SRP1038A_V728_HOLD")'),1)
 def test_13_safety_15hold_no_tx(self):self.assertTrue(self.d["15_crossmodule_HOLD"] and self.d["SG48_HOLD"] and self.d["NO_FAB"] and self.d["NO_TX"])
if __name__=="__main__":unittest.main()
