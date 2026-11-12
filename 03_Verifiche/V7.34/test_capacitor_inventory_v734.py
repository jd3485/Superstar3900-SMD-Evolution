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
    for match in re.finditer(r'\(property "Reference" "(C62\d{2})"(?:(?!\(instances ).){0,1600}?\(property "Value" "([^"]+)"', text, re.S):
        ref, val = match.groups()
        window = text[match.start():text.index("(instances ", match.start())]
        fp = re.search(r'\(property "Footprint" "([^"]*)"', window)
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


# Exact native schematic coordinates: capacitor symbol pins (0,+5.08) and (0,-5.08)
# are mirrored vertically in sheet coordinates, so pin1 is y-5.08 and pin2 y+5.08.
EXPECTED_PIN_LABELS = {
    "C6201": ("3V3_CODEC_IO", "GND"),
    "C6202": ("CODEC_REF", "GND"),
    "C6203": ("CODEC_AVDD_LDO_OUT", "GND"),
    "C6204": ("CODEC_AVDD_LDO_OUT", "GND"),
    "C6205": ("CODEC_DVDD_LDO_OUT", "GND"),
    "C6206": ("CODEC_DVDD_LDO_OUT", "GND"),
    "C6207": ("3V3_CODEC_LDOIN", "GND"),
    "C6208": ("3V3_CODEC_LDOIN", "GND"),
    "C6209": ("3V3_MCU", "GND"),
    "C6210": ("3V3_MCU", "GND"),
    "C6211": ("3V3_MCU", "GND"),
    "C6212": ("3V3_MCU", "GND"),
    "C6213": ("3V3_MCU", "GND"),
    "C6214": ("3V3_ANA_MCU", "GND"),
    "C6215": ("5V_DIGITAL_FILTERED", "GND"),
    "C6216": ("3V3_AUDIO_CLK", "GND"),
    "C6217": ("3V3_AUDIO_CLK", "GND"),
    "C6218": ("3V3_AUDIO_CLK", "GND"),
    "C6219": ("5V_DIGITAL_FILTERED", "GND"),
    "C6220": ("5V_DIGITAL_FILTERED", "GND"),
    "C6221": ("5V_DIGITAL_FILTERED", "GND"),
    "C6222": ("3V3_MCU", "GND"),
    "C6223": ("5V_DIGITAL_FILTERED", "GND"),
    "C6224": ("3V3_CODEC_IO", "GND"),
    "C6225": ("5V_DIGITAL_FILTERED", "GND"),
    "C6226": ("3V3_CODEC_LDOIN", "GND"),
    "C6227": ("MIC_PREAMP_OUT", "MIC_AC_COUPLED"),
    "C6228": ("MIC_CODEC_IN", "GND"),
    "C6229": ("FM_DISCRIM_RAW", "FM_AC_COUPLED"),
    "C6230": ("FM_CODEC_IN", "GND"),
}

def pin_labels_from_sheet():
    text = SOURCE.read_text(encoding="utf-8")
    instances = re.findall(r'\\(symbol \\(lib_id "S3900E:C_DRAFT"\\) \\(at ([\\d.]+) ([\\d.]+) 0\\)[\\s\\S]{0,360}?\\(property "Reference" "(C62\\d\\d)"', text)
    labels = {(round(float(x), 4), round(float(y), 4)): name for name,x,y in
              re.findall(r'\\(label "([^"]+)" \\(at ([\\d.]+) ([\\d.]+)', text)}
    result = {}
    for sx,sy,ref in instances:
        x,y = float(sx),float(sy)
        top = labels.get((round(x,4),round(y-5.08,4)))
        bottom = labels.get((round(x,4),round(y+5.08,4)))
        if ref in result:
            raise AssertionError(f"Duplicate capacitor: {ref}")
        result[ref] = (top,bottom)
    return result

class TestPinLabelAudit(unittest.TestCase):
    def test_exact_labels_all_thirty(self):
        self.assertEqual(pin_labels_from_sheet(), EXPECTED_PIN_LABELS)
    def test_series_audio_not_ground_shunts(self):
        self.assertEqual(EXPECTED_PIN_LABELS["C6227"], ("MIC_PREAMP_OUT","MIC_AC_COUPLED"))
        self.assertEqual(EXPECTED_PIN_LABELS["C6229"], ("FM_DISCRIM_RAW","FM_AC_COUPLED"))
    def test_codecref_and_internal_regulator_distinct(self):
        self.assertEqual(EXPECTED_PIN_LABELS["C6202"], ("CODEC_REF","GND"))
        self.assertEqual(EXPECTED_PIN_LABELS["C6204"], ("CODEC_AVDD_LDO_OUT","GND"))
        self.assertEqual(EXPECTED_PIN_LABELS["C6206"], ("CODEC_DVDD_LDO_OUT","GND"))

if __name__ == "__main__":
    unittest.main()
