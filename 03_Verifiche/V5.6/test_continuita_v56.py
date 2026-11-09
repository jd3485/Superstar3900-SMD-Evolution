#!/usr/bin/env python3
"""Unit + adversarial tests for the V5.6 static F.Cu topology audit. NOT native DRC."""
from __future__ import annotations
from pathlib import Path
import sys, copy, unittest
from shapely.affinity import translate
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'03_Verifiche/V5.6'))
from audit_continuita_fcu_v56 import (PCB,V48,audit_board,components_for_items,
                                       actual_board_copper,EPSILON_MM,COPPER_LAYERS)

B=PCB.read_text(encoding='utf-8')
REF=V48.read_text(encoding='utf-8')
R=audit_board(B,REF)
ITEMS, COUNTS, NETS=actual_board_copper(B)

class ReferenceBoard(unittest.TestCase):
    def test_counts_are_grounded_in_real_board(self):
        self.assertEqual(R['geometry_counts'],{'pads':44,'segments':44,'vias':70,'zones':4,'filled_zone_polygons':0})
    def test_eight_nets(self):self.assertEqual(R['net_count'],8)
    def test_seven_signal_nets_present(self):self.assertEqual(len(R['fcu_networks'])-1,7)
    def test_seven_signal_nets_each_connected(self):
        self.assertEqual([k for k,v in R['fcu_networks'].items() if k!='GND_RF' and v['component_count']!=1],[])
    def test_ground_is_not_falsely_accepted(self):
        self.assertEqual(R['ground_connectivity'],'PENDING_ZONE_REFILL_AND_NATIVE_DRC')
        self.assertFalse(R['fabrication_allowed'])
    def test_ground_islands_measured(self):self.assertEqual(R['ground_top_islands_count'],64)
    def test_ground_pad_islands_measured(self):self.assertEqual(R['ground_pad_islands_count'],24)
    def test_ground_isolated_via_islands_measured(self):self.assertEqual(R['ground_via_only_islands_count'],40)
    def test_four_zones_unfilled(self):
        self.assertEqual(set(x['layer'] for x in R['ground_zones']),set(COPPER_LAYERS))
        self.assertTrue(all(x['filled_polygons']==0 and x['net']==1 for x in R['ground_zones']))
    def test_six_thermal_vias_plus_external_same_ground_group(self):
        island=[x for x in R['ground_pad_islands'] if any(p.startswith('U101:2:') and p.endswith(':10') for p in x['pads'])]
        self.assertEqual(len(island),1);self.assertEqual(island[0]['vias'],7)
    def test_unchanged_copper_relative_to_v48(self):self.assertTrue(R['copper_identical_to_v48_study'])
    def test_report_no_native_assertion(self):
        self.assertEqual(R['native_erc'],'NOT_RUN');self.assertEqual(R['native_drc'],'NOT_RUN')
        self.assertEqual(R['status'],'STATIC_TOPOLOGY_PASS_GROUND_PENDING')
    def test_deterministic_reproducible(self):self.assertEqual(R,audit_board(B,REF))

class DeliberateFaults(unittest.TestCase):
    def test_remove_lna_input_track_separates_pads(self):
        mutated=[x for x in ITEMS if not (x['net']==2 and x['kind']=='segment')]
        comps=components_for_items(mutated)
        self.assertEqual(sum(n==2 for n,_ in comps),2)
    def test_remove_lna_output_track_separates_pads(self):
        mutated=[x for x in ITEMS if not (x['net']==5 and x['kind']=='segment')]
        comps=components_for_items(mutated)
        self.assertEqual(sum(n==5 for n,_ in comps),2)
    def test_displace_signal_pad_breaks_route(self):
        mutated=[dict(x) for x in ITEMS]
        for x in mutated:
            if x['kind']=='pad' and x['id'].startswith('C101:1:'):
                x['geometry']=translate(x['geometry'],xoff=40)
                break
        comps=components_for_items(mutated)
        self.assertGreater(sum(n==2 for n,_ in comps),1)
    def test_wrong_segment_net_is_detected(self):
        needle='(start 28.000 36.000) (end 51.450 36.000) (width 0.280) (layer "F.Cu") (net 2)'
        self.assertIn(needle,B)
        x=audit_board(B.replace(needle,needle.replace('(net 2)','(net 1)'),1),REF)
        self.assertIn('COPPER_NOT_IDENTICAL_TO_V48',x['errors'])
    def test_wrong_zone_net_is_detected(self):
        needle='(zone (net 1)'
        self.assertIn(needle,B)
        x=audit_board(B.replace(needle,'(zone (net 2)',1),REF)
        self.assertIn('GROUND_ZONE_CONFIG_MISMATCH',x['errors'])
    def test_new_filled_polygon_requires_reaudit(self):
        needle='(zone (net 1)'
        self.assertIn(needle,B)
        x=audit_board(B.replace(needle,'(zone (filled_polygon) (net 1)',1),REF)
        self.assertIn('ZONE_STATE_CHANGED_REAUDIT_REQUIRED',x['errors'])
    def test_reference_swap_cannot_pass_identity(self):
        x=audit_board(B,REF.replace('(net 2 "RF_LNA_INPUT")','(net 2 "NOT_RF_INPUT")',1))
        self.assertIn('COPPER_NOT_IDENTICAL_TO_V48',x['errors'])
    def test_epsilon_rejects_unsafe_values(self):
        with self.assertRaises(ValueError):components_for_items(ITEMS,epsilon=.02)
        with self.assertRaises(ValueError):components_for_items(ITEMS,epsilon=-1)
    def test_signal_count_requires_seven(self):
        x=audit_board(B,REF,minimum_signal_groups=8)
        self.assertIn('SIGNAL_NET_COUNT_CHANGED',x['errors'])
    def test_unfilled_zones_not_a_native_drc(self):
        self.assertTrue('NOT KiCad' in __import__('audit_continuita_fcu_v56').__doc__ or R['native_drc']=='NOT_RUN')

if __name__=='__main__':unittest.main(verbosity=2)
