"""V7.17 fail-closed contracts for KiCad full-radio integration planning."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from audit_full_board_native_v717 import (
    ROOT,MATRIX,EXPECTED,DANGER,MAPPING,audit_interfaces,native_erc,
    native_nets,port_candidates,
)

class TestWholeRadioV717(unittest.TestCase):
    def test_01_native_baseline_categories_are_full_and_precise(self):
        self.assertEqual(sum(EXPECTED.values()),383)
        self.assertEqual(sum(EXPECTED[k] for k in DANGER),17)
        self.assertEqual(EXPECTED["label_dangling"],26)
        self.assertEqual(EXPECTED["endpoint_off_grid"],219)

    def test_02_all_15_interfaces_still_open_hold_tx_zero(self):
        with MATRIX.open(newline="",encoding="utf-8") as fh:
            items=list(csv.DictReader(fh))
        self.assertEqual(len(items),15)
        self.assertTrue(all(r["physical_connection"]=="OPEN"
                            and r["qualification"]=="HOLD"
                            and r["tx_permission"]=="0" for r in items))

    def test_03_unqualified_voltage_5v_must_not_be_3v3(self):
        with MATRIX.open(newline="",encoding="utf-8") as fh:
            items=list(csv.DictReader(fh))
        p=[r for r in items if r["domain"]=="power_codec"]
        self.assertEqual(len(p),1)
        self.assertEqual(p[0]["source_net"],"5V_RF_PREREGULATED")
        self.assertEqual(p[0]["candidate_destination_net"],"3V3_CODEC_IO")
        self.assertIn("wrong voltage",p[0]["blocker"].lower())

    def test_04_mcu_rx_if_stage_is_not_already_an_rf_chain(self):
        with MATRIX.open(newline="",encoding="utf-8") as fh:
            items=list(csv.DictReader(fh))
        rx=[r for r in items if r["domain"]=="rx_after_atten"][0]
        self.assertEqual(rx["candidate_destination_net"],"RX_IF_STAGE")
        self.assertEqual(rx["physical_connection"],"OPEN")

    def test_05_no_gpio_pin_assignment_is_qualified_by_shared_label(self):
        n=["/MCU_CODEC_AFE_existing_V2_1_UNQUALIFIED/PLL_SCK",
           "/AUX_POWER_existing_V1_5_UNQUALIFIED/PLL_SCK"]
        self.assertEqual(port_candidates(n,"MCU_CODEC_V2.1","PLL_SCK")["status"],
                         "EXACT_NATIVE_NET_NAME")
        self.assertEqual(port_candidates(n,"AUX_V1.5","PLL_SCK")["status"],
                         "EXACT_NATIVE_NET_NAME")
        self.assertNotEqual(port_candidates(n,"MCU_CODEC_V2.1","PLL_SCK")["exact_matches"],
                            port_candidates(n,"AUX_V1.5","PLL_SCK")["exact_matches"])

    def test_06_similar_fm_labels_must_not_automatically_merge(self):
        n=["/MCU_CODEC_AFE_existing_V2_1_UNQUALIFIED/FM_DISCRIM_RAW"]
        p=port_candidates(n,"MCU_CODEC_V2.1","FM_DISCR_RAW")
        self.assertEqual(p["status"],"NOT_FOUND_NATIVE_NETLIST")
        self.assertIn("FM_DISCRIM_RAW",p["similar"])

    def test_07_external_ports_are_not_cad_qualified(self):
        p=port_candidates([],"external_discriminator","FM_DISCR_RAW")
        self.assertEqual(p["status"],"EXTERNAL_NOT_IN_CAD")
        self.assertEqual(p["exact_matches"],[])

    def test_08_all_15_preserved_in_machine_interface_audit(self):
        fake=list(MAPPING.values())
        n=[p+"PLL_SCK" for p in fake]
        records=audit_interfaces(n)
        self.assertEqual(len(records),15)
        self.assertEqual(len({r["id"] for r in records}),15)
        self.assertTrue(all(r["physical_connection"]=="OPEN"
                         and r["qualification"]=="HOLD"
                         and r["tx_permission"]==0 for r in records))

    def test_09_unapproved_unrouted_tx_has_no_physical_permission(self):
        with MATRIX.open(newline="",encoding="utf-8") as fh:
            records=list(csv.DictReader(fh))
        interlock=[r for r in records if r["domain"]=="interlock"]
        self.assertEqual(len(interlock),1)
        self.assertEqual(interlock[0]["tx_permission"],"0")
        self.assertEqual(interlock[0]["candidate_destination_net"],"RF_TX_UNROUTED")

    def test_10_native_erc_requires_valid_real_report(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"spoof.rpt"
            p.write_text("ERC messages: 0 Errors 0 Warnings")
            with self.assertRaises(ValueError):
                native_erc(p)

    def test_11_native_netlist_rejects_textual_guess(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"not-native.net"
            p.write_text("99 nets, looks good")
            with self.assertRaises(ValueError):
                native_nets(p)

    def test_12_no_whole_radio_fab_board_added_by_diagnostic(self):
        self.assertFalse(list((ROOT/"04_KiCad").glob("*V7.17*/*.kicad_pcb")))
        self.assertEqual(len(MAPPING),3)

    def test_13_source_matrix_retains_5v_bench_qualification_gate(self):
        with MATRIX.open(newline="",encoding="utf-8") as fh:
            records=list(csv.DictReader(fh))
        p=[x for x in records if x["domain"]=="rf_bench_power"]
        self.assertEqual(len(p),1)
        self.assertIn("NO_ASSUMED_EQUIVALENCE",p[0]["blocker"])

    def test_14_pll_ce_requires_physical_inhibit_and_safe_boot(self):
        with MATRIX.open(newline="",encoding="utf-8") as fh:
            records=list(csv.DictReader(fh))
        p=[x for x in records if x["domain"]=="spi_ce"]
        self.assertEqual(len(p),1)
        self.assertIn("inhibit",p[0]["blocker"].lower())
        self.assertEqual(p[0]["tx_permission"],"0")

if __name__=="__main__":
    unittest.main()
