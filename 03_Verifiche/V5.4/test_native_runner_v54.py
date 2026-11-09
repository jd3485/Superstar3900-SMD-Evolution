#!/usr/bin/env python3
"""Tests are MOCKS of CLI behavior, NOT KiCad ERC/DRC runs."""
from pathlib import Path
import importlib.util, json, os, stat, tempfile, unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('v54', Path(__file__).with_name('run_native_v54.py'))
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class NativeRunnerSafety(unittest.TestCase):
    def test_real_candidate_exists(self):
        self.assertTrue((ROOT / MOD.REL / (MOD.STEM+'.kicad_pcb')).is_file())
        self.assertTrue((ROOT / MOD.REL / (MOD.STEM+'.kicad_sch')).is_file())

    def test_unavailable_cli_stays_not_run(self):
        with tempfile.TemporaryDirectory() as t, patch.object(MOD.shutil, 'which', return_value=None):
            self.assertEqual(MOD.main(['--output', t]), 3)
            s=json.loads((Path(t)/'STATUS_V5.4.json').read_text())
            self.assertEqual(s['native_erc'], 'NOT_RUN')
            self.assertEqual(s['native_drc'], 'NOT_RUN')
            self.assertFalse(s['fab_authorized'])
            self.assertTrue(s['source_unchanged'])
            self.assertFalse(list(Path(t).glob('*.kicad_*')))

    def fake_cli(self, folder, variant):
        executable=Path(folder)/'mock-kicad-cli'
        content='''#!/usr/bin/env python3
import sys,json,pathlib
p=sys.argv[1:]
if p==['version']:
 print('''+repr('9.0.10' if variant=='v9' else '10.0.8')+''');sys.exit(0)
if '--help' in p:
 print('--format --severity-all --exit-code-violations --refill-zones --schematic-parity');sys.exit(0)
if '--output' in p:
 target=pathlib.Path(p[p.index('--output')+1]);
 target.write_text('''+repr('invalid' if variant=='badjson' else '{"violations": [], "source":"MOCK_NOT_NATIVE"}')+''')
sys.exit('''+str(5 if variant=='violation' else 0)+''')
'''
        executable.write_text(content)
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        return str(executable)

    def test_rejects_wrong_kicad_major(self):
        with tempfile.TemporaryDirectory() as t:
            mockcli=self.fake_cli(t,'v9')
            with patch.object(MOD.shutil,'which',return_value=mockcli):
                self.assertEqual(MOD.main(['--output',str(Path(t)/'out')]),3)
            s=json.loads((Path(t)/'out/STATUS_V5.4.json').read_text())
            self.assertEqual(s['native_erc'],'NOT_RUN')

    def test_mock_good_still_blocked(self):
        with tempfile.TemporaryDirectory() as t:
            mockcli=self.fake_cli(t,'success')
            with patch.object(MOD.shutil,'which',return_value=mockcli):
                self.assertEqual(MOD.main(['--output',str(Path(t)/'out')]),0)
            s=json.loads((Path(t)/'out/STATUS_V5.4.json').read_text())
            self.assertEqual(s['native_erc'],'EXECUTED_REVIEW_REQUIRED')
            self.assertEqual(s['native_drc'],'EXECUTED_REVIEW_REQUIRED')
            self.assertFalse(s['fab_authorized'])
            self.assertTrue(s['source_unchanged'])
            self.assertEqual(s['release'],'BLOCKED_NOT_FOR_FAB')
            self.assertEqual(json.loads((Path(t)/'out/DRC_PARITY_V5.4.json').read_text())['source'],'MOCK_NOT_NATIVE')

    def test_mock_violations_fail(self):
        with tempfile.TemporaryDirectory() as t:
            mockcli=self.fake_cli(t,'violation')
            with patch.object(MOD.shutil,'which',return_value=mockcli):
                self.assertEqual(MOD.main(['--output',str(Path(t)/'out')]),5)
            s=json.loads((Path(t)/'out/STATUS_V5.4.json').read_text())
            self.assertEqual(s['native_drc'],'VIOLATIONS_OR_INCOMPLETE')
            self.assertFalse(s['fab_authorized'])

    def test_mock_corrupt_report_fail(self):
        with tempfile.TemporaryDirectory() as t:
            mockcli=self.fake_cli(t,'badjson')
            with patch.object(MOD.shutil,'which',return_value=mockcli):
                self.assertEqual(MOD.main(['--output',str(Path(t)/'out')]),5)
            s=json.loads((Path(t)/'out/STATUS_V5.4.json').read_text())
            self.assertEqual(s['native_erc'],'VIOLATIONS_OR_INCOMPLETE')

    def test_workflow_has_no_fabrication_or_deploy(self):
        work=(ROOT/'.github/workflows/kicad_native_v54.yml').read_text()
        self.assertIn('workflow_dispatch:',work)
        self.assertIn('if: always()',work)
        self.assertIn('upload-artifact@v4',work)
        self.assertIn('ppa:kicad/kicad-10.0-releases',work)
        self.assertNotIn('gerber',work.lower())
        self.assertNotIn('pcbway',work.lower())

    def test_all_gate_items_remain_open(self):
        gate=json.loads((ROOT/'03_Verifiche/V5.0/GATE_RELEASE_V5.0.json').read_text())
        self.assertEqual(len(gate['gate_items']),9)
        self.assertTrue(all(x['status']=='OPEN' for x in gate['gate_items']))
        self.assertFalse(gate['fabrication_allowed'])

if __name__=='__main__':unittest.main(verbosity=1)
