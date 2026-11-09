#!/usr/bin/env python3
"""Static integrity / mutation tests. These are not KiCad ERC/DRC."""
import csv, io, json, re, shutil, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import genera_bom_net_v51 as m

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[2]
        cls.d=m.audit(cls.root)
        cls.source=(cls.root/m.BOARD_REL).read_text('utf-8')
    def test_components(self):self.assertEqual(self.d['total_components'],15)
    def test_nets(self):self.assertEqual(self.d['non_empty_nets'],8)
    def test_pins(self):self.assertEqual(self.d['distinct_electrical_pins'],31)
    def test_rf_smas(self):self.assertEqual(len([x for x in self.d['components'] if x['type']=='RF connector']),4)
    def test_lna_power(self):
        net={(x['reference'],x['pin']):x['net'] for x in self.d['pins']}
        self.assertEqual(net[('J105','1')],'+5V_BENCH')
        self.assertEqual(net[('U101','3')],'RF_BIAS_OUT')
        self.assertEqual(net[('L101','2')],'RF_BIAS_OUT')
    def test_attenuator(self):self.assertAlmostEqual(self.d['attenuator_ideal_50ohm_db'],6.012876,places=5)
    def test_local_libs(self):self.assertTrue(self.d['footprint_local_files_present'])
    def test_never_authorized(self):
        self.assertFalse(self.d['fabrication_allowed']); self.assertEqual(self.d['native_drc'],'NOT_RUN')
    def with_board_mutation(self,old,new):
        if old not in self.source:raise AssertionError('Bad test fixture')
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source_dir=self.root/m.BOARD_REL.parent;dst=root/m.BOARD_REL.parent
            shutil.copytree(source_dir,dst)
            (dst/m.BOARD_REL.name).write_text(self.source.replace(old,new,1),'utf-8')
            with self.assertRaises(ValueError):m.audit(root)
    def test_detects_ref_duplicate(self):
        self.with_board_mutation('(property "Reference" "J102"','(property "Reference" "J101"')
    def test_detects_wrong_net(self):
        self.with_board_mutation('(net 2 "RF_LNA_INPUT")','(net 2 "CORRUPTED")')
    def test_detects_wrong_attenuator(self):
        self.with_board_mutation('(property "Value" "37.4R"','(property "Value" "40R"')
    def test_detects_missing_library(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);dst=root/m.BOARD_REL.parent
            shutil.copytree(self.root/m.BOARD_REL.parent,dst)
            x=dst/'S3900E_v33.pretty'/'R_0402.kicad_mod';x.unlink()
            with self.assertRaises(ValueError):m.audit(root)
    def test_csv_header(self):
        with tempfile.TemporaryDirectory() as t:
            m.save(self.root,Path(t))
            with (Path(t)/'BOM_RX_CANDIDATA_V5.1.csv').open(newline='',encoding='utf-8') as handle:
                rows=list(csv.DictReader(handle))
            self.assertEqual(len(rows),15)
            self.assertTrue(all(r['approval_status'] for r in rows))

if __name__=='__main__':
    unittest.main(verbosity=2)
