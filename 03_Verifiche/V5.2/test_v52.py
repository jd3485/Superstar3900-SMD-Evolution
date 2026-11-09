#!/usr/bin/env python3
from pathlib import Path
import unittest,importlib.util,re
p=Path(__file__).with_name('audit_associazioni_v52.py')
s=importlib.util.spec_from_file_location('auditv52',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
old=a.OLD;new=a.NEW
olds=(old/(a.OLDSTEM+'.kicad_sch')).read_text();oldb=(old/(a.OLDSTEM+'.kicad_pcb')).read_text()
news=(new/(a.NEWSTEM+'.kicad_sch')).read_text();newb=(new/(a.NEWSTEM+'.kicad_pcb')).read_text()
class T(unittest.TestCase):
 def test_pass(self):self.assertEqual(a.check(olds,oldb,news,newb),[])
 def test_rename_instance(self):self.assertTrue(a.check(olds,oldb,news.replace('(project "'+a.NEWSTEM+'"','(project "OTHER"',1),newb))
 def test_remove_link(self):self.assertTrue(a.check(olds,oldb,news,re.sub(r' \(path "/[a-f0-9-]+/[a-f0-9-]+"\)','',newb,count=1)))
 def test_corrupt_link(self):self.assertTrue(a.check(olds,oldb,news,newb.replace('/'+next(iter(re.findall(r'\(path "/[a-f0-9-]+/([a-f0-9-]+)"\)',newb))),'/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',1)))
 def test_copper_invariant(self):self.assertTrue(a.check(olds,oldb,news,newb.replace('(size 2.050 2.050)','(size 2.100 2.050)',1)))
 def test_net_invariant(self):self.assertTrue(a.check(olds,oldb,news,newb.replace('RF_LNA_INPUT','RF_WRONG',1)))
 def test_schematic_values_invariant(self):self.assertTrue(a.check(olds,oldb,news.replace('37.4R','33R',1),newb))
 def test_schematic_footprint_invariant(self):self.assertTrue(a.check(olds,oldb,news.replace('C_0402','C_0805',1),newb))
 def test_unexpected_extra_symbol(self):self.assertTrue(a.check(olds,oldb,news.replace('(lib_id "S3900E:COAX_R")','(lib_id "S3900E:OTHER")',1),newb))
 def test_15_pcb_paths(self):self.assertEqual(len(re.findall(r'\(path "/[a-f0-9-]+/[a-f0-9-]+"\)',newb)),15)
 def test_15_instances(self):self.assertEqual(news.count('(project "'+a.NEWSTEM+'"'),15)
 def test_15_components(self):self.assertEqual(set(a.components(news,'sch')),set(a.components(newb,'pcb')))
if __name__=='__main__':unittest.main(verbosity=2)
