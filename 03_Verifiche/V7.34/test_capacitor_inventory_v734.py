"""V7.34 non-invasive source inventory gate: exact C6201-C6230 and no speculative footprints."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "04_KiCad/Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
EXPECTED = {
    "100nF": {"C6201","C6203","C6205","C6207","C6209","C6210","C6211","C6212","C6214","C6217","C6220","C6227"},
    "10uF": {"C6202","C6204","C6206","C6208","C6219"},
    "1uF": {"C6213","C6215","C6216","C6218","C6221","C6222","C6223","C6224","C6225","C6226","C6229"},
    "4.7nF": {"C6228"},
    "10nF": {"C6230"},
}

def inventory():
    text = SOURCE.read_text(encoding="utf-8")
    output = {}
    # Reference and Value and Footprint are properties in the same symbol instance;
    # bounds prevent accidental scanning into a subsequent symbol.
    for match in re.finditer(r'\\(property "Reference" "(C62\\d{2})"(?:(?!\\(instances ).){0,1600}?\\(property "Value" "([^"]+)"', text, re.S):
        ref, val = match.groups()
        window = text[match.start():text.index("(instances ", match.start())]
        fp = re.search(r'\\(property "Footprint" "([^"]*)"', window)
        assert fp is not None, f"Missing footprint property: {ref}"
        assert ref not in output, f"Duplicate reference: {ref}"
        output[ref] = (val, fp.group(1))
    return output

class TestV734SourceInventory(unittest.TestCase):
    def test_all_thirty_values(self):
        actual = inventory()
        self.assertEqual(len(actual), 30)
        for value, refs in EXPECTED.items():
            self.assertEqual({ref for ref, pair in actual.items() if pair[0] == value}, refs)
    def test_no_premature_footprints(self):
        self.assertTrue(all(fp == "" for _, fp in inventory().values()))
    def test_source_not_board(self):
        self.assertTrue(SOURCE.name.endswith(".kicad_sch"))

if __name__ == "__main__":
    unittest.main()
