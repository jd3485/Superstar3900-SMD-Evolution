"""Fail-closed KiCad9 7-sheet native comparison for V7.34 TPS3840PL30 candidate ECO.
No PCB or production approval. One U6206.EN net move, new U6207 three nets and C6231 VDD bypass.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.34/output-ci"
OLD=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEW=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
MCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def memberships(ns):
    return {(ref,pin,name.rsplit("/",1)[-1]) for name,nodes in ns.items() for ref,pin in nodes}

def gate():
    src=MCU.read_text(encoding="utf-8")
    root=NEW.read_text(encoding="utf-8")
    assert root.count("../Modulo_MCU_CODEC_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB/")==1
    assert '(property "Reference" "U6207"' in src
    assert '(property "Reference" "C6231"' in src
    assert '(property "Value" "100nF" (at 1050.0000 424.0000 0)' in src
    assert '(property "MPN" "TPS3840PL30DBVR"' in src
    assert '(symbol "S3900E:TPS3840PL30_DBV5_REVIEW"' in src
    assert src.count('(label "CODEC_LDOIN_EN_SUPERVISED"')==2
    assert '(label "5V_DIGITAL_FILTERED" (at 919.8400 415.0000 0)' not in src
    assert '(no_connect (at 1020.1600 404.8400)' in src
    assert '(no_connect (at 1020.1600 425.1600)' in src
    oldc=compmap(OUT/"v734.original.net")
    newc=compmap(OUT/"v734.revised.net")
    assert len(oldc)==132 and len(newc)==134,(len(oldc),len(newc))
    assert set(newc)-set(oldc)=={"U6207","C6231"}
    assert set(oldc)-set(newc)==set()
    assert all(oldc[k]==newc[k] for k in oldc),"Pre-existing 132 values/footprints must not change"
    assert newc["U6207"]==("","TPS3840PL30DBVR"),newc["U6207"]
    assert newc["C6231"]==("","100nF"),newc["C6231"]
    n0=nets(OUT/"v734.original.net")
    n1=nets(OUT/"v734.revised.net")
    assert len(n0)==100 and len(n1)==101,(len(n0),len(n1))
    a,b=memberships(n0),memberships(n1)
    deleted=a-b;added=b-a
    assert deleted=={("U6206","3","5V_DIGITAL_FILTERED")},deleted
    assert added=={
        ("U6206","3","CODEC_LDOIN_EN_SUPERVISED"),
        ("U6207","1","CODEC_LDOIN_EN_SUPERVISED"),
        ("U6207","2","3V3_CODEC_IO"),
        ("U6207","3","GND"),
        ("C6231","1","3V3_CODEC_IO"),
        ("C6231","2","GND"),
    },added
    # Check no intermodule net changed (except intentionally local MCU pins).
    for n in n0:
        if not n.endswith("/5V_DIGITAL_FILTERED"):
            assert n in n1 or n.rsplit("/",1)[-1] in {x.rsplit("/",1)[-1] for x in n1},n
    er0=native_erc(OUT/"v734.original.erc.rpt")
    er1=native_erc(OUT/"v734.revised.erc.rpt")
    assert er0["errors"]==36 and er0["warnings"]==218,er0
    assert er1["errors"]<=er0["errors"],er1
    for rule in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert er1["categories"].get(rule,0)<=er0["categories"].get(rule,0),(rule,er0,er1)
    # Geometric label warnings are not waived: retain full ERC reports, no signoff.
    assert er1["warnings"]<=er0["warnings"]+12,(er0,er1)
    evidence={"revision":"V7.34","status":"CAD_REVIEW_ONLY_NOT_FOR_FAB","components_before":132,
      "components_after":134,"nets_before":100,"nets_after":101,
      "deleted_pin_net_memberships":sorted(list(deleted)),
      "added_pin_net_memberships":sorted(list(added)),
      "missing_footprints_before":sum(not x[0] for x in oldc.values()),
      "missing_footprints_after":sum(not x[0] for x in newc.values()),
      "erc_before":er0,"erc_after":er1,
      "part":"TPS3840PL30DBVR","module":"MCU_CODEC","NO_FAB":True,"NO_TX":True,
      "hardware_validation":False,"sequencing_signoff":False}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v734.native.json").write_text(json.dumps(evidence,indent=2,default=str)+"\n")
    return evidence

class TestNativeV734(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=gate()
    def test_01_new_supervisor(self):self.assertEqual(self.d["components_after"],134)
    def test_02_one_new_net(self):self.assertEqual(self.d["nets_after"],101)
    def test_03_net_moves_exact(self):self.assertEqual(len(self.d["added_pin_net_memberships"]),6)
    def test_04_no_production(self):self.assertTrue(self.d["NO_FAB"] and self.d["NO_TX"] and not self.d["sequencing_signoff"])
    def test_05_no_erc_error_growth(self):self.assertLessEqual(self.d["erc_after"]["errors"],36)

if __name__=="__main__":
    unittest.main()
