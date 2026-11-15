"""V7.76: actual V7.74 master 13.8V/eFuse/BUCK electrical dependency gate.

This program proves schematic pin nets and resistor/current arithmetic, NOT a
qualified fuse, SOA, startup, measured load, operating safety or production PCB.
"""
from pathlib import Path
import json
import math
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_KiCad/Gerarchico_Alimentazioni_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD/01_EFUSE_AUX.kicad_sch"
OUT = ROOT / "03_Verifiche/V7.74/output-ci/v774.revised.net"
RESULT = ROOT / "03_Verifiche/V7.76/output-ci/v776_efuse_buck_design_gate.json"
sys.path.insert(0, str(ROOT / "03_Verifiche/V7.22"))
from test_ep33_v722 import nets

# Datasheet TPS2660 SLVSDG2G (2019) section 10.2.2.2 Eq.9:
# R_ILIM [kOhm] = 12 / I_LIM [A]; nominal *design equation*, not a worst
# current threshold. Figure 48 SHDN is an externally pulled-low input.
TI_ILIM_NUMERATOR = 12.0


def current_limit_nominal(r_kohms):
    return TI_ILIM_NUMERATOR / r_kohms


def design_gate():
    source = SRC.read_text(encoding="utf8")
    def component(ref):
        pattern = r'\(property "Reference" "' + re.escape(ref) + r'"[^\n]*\n\s*\(property "Value" "([^"]+)"'
        hits = re.findall(pattern, source)
        assert len(hits) == 1, (ref, hits)
        return hits[0]
    resistor = component("R203")
    fuse = component("F200")
    mode = component("R204")
    switch = component("SW200")
    tvs = component("D200")
    assert resistor == "8k2 1%" and "1.5A " in fuse and "CANDIDATO" in fuse
    assert "402k" in mode and "CANDIDATE" in mode
    assert "CANDIDATE" in switch and "DNP" in tvs

    by_pin = {}
    for net, nodes in nets(OUT).items():
        for node in nodes:
            assert node not in by_pin, node
            by_pin[node] = net
    pin = lambda ref, n: by_pin[(ref, str(n))]
    # These prove actual pins in KiCad9 exported seven-sheet netlist:
    assert pin("U200",1) == pin("U200",2)
    assert pin("U200",1) in (pin("F200",1),pin("F200",2))
    assert pin("F200",1) != pin("F200",2)  # physical fuse NOT bypassed
    assert pin("U200",8) == pin("U200",17)
    assert pin("U200",8) != pin("U200",9)  # no illegal RTN↔GND bridge
    assert pin("U200",15) == pin("U200",16) == pin("U100",3)
    assert pin("R203",1) != pin("R203",2)
    assert {pin("R203",1), pin("R203",2)} == {pin("U200",11),pin("U200",8)}
    assert {pin("R204",1), pin("R204",2)} == {pin("U200",6),pin("U200",8)}
    assert pin("SW200",1) == pin("SW200",4) == pin("U200",7)
    assert pin("SW200",2) == pin("SW200",3) == pin("U200",9)
    assert pin("SW200",1) != pin("SW200",2)
    assert pin("U200",7) != pin("U200",8)

    i_limit = current_limit_nominal(8.2)
    # Ideal buck power conservation. Illustrative efficiency scenarios only,
    # not a datasheet worst-case prediction or an approved load budget.
    corners=[]
    for vin in (10.5, 13.8, 17.0):
        for efficiency in (.70,.80,.90):
            i_in=5.0*2.0/(vin*efficiency)
            corners.append(dict(vin_v=vin, efficiency_assumed=efficiency,
              five_v_load_a_assumed=2.0, buck_input_a_idealized=round(i_in,6),
              nominal_ilim_margin_a_not_guaranteed=round(i_limit-i_in,6)))
    assert len(corners)==9
    assert math.isclose(i_limit,1.4634146341463417,rel_tol=1e-12)
    assert any(x["nominal_ilim_margin_a_not_guaranteed"] < 0 for x in corners) is False
    # Even when nominal current arithmetic appears to fit, tolerances,
    # transient demand, 5V load, 13.8V source, F200 I2t, and eFuse
    # current limit MIN/MAX / thermal latch-off are all UNKNOWN.
    result = dict(revision="V7.76",target="native V7.74 unchanged",
      source_r203=resistor,f200=fuse,r204=mode,sw200=switch,d200=tvs,
      ilim_equation_ti="R_ILIM[kOhm]=12/I_LIM[A]",
      ilim_nominal_a=round(i_limit,8),
      fuse_nominal_candidate_a=1.5,
      fuse_rating_is_not_trip_current=True,
      nominal_fuse_minus_eFuse_limit_a=round(1.5-i_limit,8),
      fuse_eFuse_coordination_qualified=False,
      efuse_rtn_separate_from_main_ground=True,
      efuse_power_path_through_fuse_and_u200=True,
      shdn_manual_reset_uses_main_ground=True,
      shdn_mechanical_esd_qualified=False,
      reverse_polarity_qualified=False,
      actual_5v_load_qualified=False,
      regulator_efficiency_qualified=False,
      output_capacitance_ceff_qualified=False,
      fault_inrush_thermal_qualified=False,
      global_pcb_drc_completed=False,
      pcb_production_authorized=False,
      numerical_screen_not_hardware_measurement=True,
      example_idealized_buck_input_corners=corners,
      no_fab=True,no_tx=True)
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    return result


class TestV776EfuseBuckSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=design_gate()
    def test_01_nominal_current(self):
        self.assertAlmostEqual(self.r["ilim_nominal_a"],12/8.2,places=7)
    def test_02_fuse_candidate_not_coordinated(self):
        self.assertFalse(self.r["fuse_eFuse_coordination_qualified"])
    def test_03_actual_power_path(self):
        self.assertTrue(self.r["efuse_power_path_through_fuse_and_u200"])
    def test_04_returns_untied(self):
        self.assertTrue(self.r["efuse_rtn_separate_from_main_ground"])
    def test_05_shdn_requires_mechanical_esd_review(self):
        self.assertFalse(self.r["shdn_mechanical_esd_qualified"])
    def test_06_no_fictitious_load_budget(self):
        self.assertFalse(self.r["actual_5v_load_qualified"])
    def test_07_corners(self):
        self.assertEqual(len(self.r["example_idealized_buck_input_corners"]),9)
    def test_08_no_fab(self):
        self.assertTrue(self.r["no_fab"] and self.r["no_tx"] and not self.r["pcb_production_authorized"])

if __name__=="__main__":
    unittest.main()
