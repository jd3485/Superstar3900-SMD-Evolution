"""Manufacturer pin-number verification for TLV320AIC3204 RHB (source-only; no native ERC).

Pin names derived from TI SLOS602E pin-function table, pp. 5-7.
The exposed thermal pad is EP33 and must connect to ground.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCHEMATIC = ROOT / "04_KiCad/Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
MANUFACTURER = {
    1:"MCLK",2:"BCLK",3:"WCLK",4:"DIN/MFP1",5:"DOUT/MFP2",
    6:"IOVDD",7:"IOVSS",8:"SCLK/MFP3",9:"SCL/SS",10:"SDA/MOSI",
    11:"MISO/MFP4",12:"SPI_SELECT",13:"IN1_L",14:"IN1_R",15:"IN2_L",
    16:"IN2_R",17:"AVSS",18:"REF",19:"MICBIAS",20:"IN3_L",
    21:"IN3_R",22:"LOL",23:"LOR",24:"AVDD",25:"HPL",
    26:"LDOIN",27:"HPR",28:"DVSS",29:"DVDD",30:"LDO_SELECT",
    31:"RESET",32:"GPIO/MFP5",33:"EP_GND_THERMAL_PAD",
}
EXPECTED_LABELS = {
    1:"AUDIO_MCLK_12M288",2:"AUDIO_BCLK",3:"AUDIO_WCLK",
    4:"AUDIO_I2S_TX",5:"AUDIO_I2S_RX",6:"3V3_CODEC_IO",7:"GND",
    8:None,9:"CODEC_I2C_SCL",10:"CODEC_I2C_SDA",11:None,
    12:"GND",13:"MIC_CODEC_IN",14:None,15:None,
    16:"FM_CODEC_IN",17:"GND",18:"CODEC_REF",19:"MICBIAS",
    20:None,21:None,22:"AUDIO_LINE_L",23:"AUDIO_LINE_R",
    24:"CODEC_AVDD_LDO_OUT",25:None,26:"3V3_CODEC_LDOIN",
    27:None,28:"GND",29:"CODEC_DVDD_LDO_OUT",
    30:"CODEC_LDO_SELECT",31:"CODEC_RESET_N",32:None,33:"GND",
}

def extract_pinmap():
    source = SCHEMATIC.read_text(encoding="utf8")
    anchor = '(symbol "S3900E:TLV320AIC3204_RHB32_DRAFT"'
    begin = source.index(anchor)
    end = source.index('(symbol "S3900E:',begin+len(anchor))
    body = source[begin:end]
    pin_re = r'\(pin [a-z_]+ line \(at ([\d.-]+) ([\d.-]+) ([\d.-]+)\) \(length [\d.]+\) \(name "([^"]+)"[^\n]*\(number "(\d+)"'
    found = {}
    for m in re.finditer(pin_re,body):
        x,y,angle,name,num = m.groups()
        num = int(num)
        if num in found:
            raise ValueError(f"Duplicate pin {num}")
        found[num]=(name,round(400+float(x),4),round(160-float(y),4),float(angle))
    labels = {}
    for name,x,y in re.findall(r'\(label "([^"]+)" \(at ([\d.-]+) ([\d.-]+)',source):
        key = (round(float(x),4),round(float(y),4))
        if key in labels and labels[key] != name:
            raise ValueError(f"Conflicting labels at {key}")
        labels[key]=name
    return {num:(name,labels.get((x,y)),angle) for num,(name,x,y,angle) in found.items()}

class TestCodecPhysicalPins(unittest.TestCase):
    def test_01_all_33_manufacturer_pins_and_names(self):
        actual=extract_pinmap()
        self.assertEqual(set(actual),set(MANUFACTURER))
        self.assertEqual({n:pin for n,(pin,_,_) in actual.items()},MANUFACTURER)
    def test_02_mic_fm_to_distinct_analog_pins(self):
        actual=extract_pinmap()
        self.assertEqual(actual[13][:2],("IN1_L","MIC_CODEC_IN"))
        self.assertEqual(actual[16][:2],("IN2_R","FM_CODEC_IN"))
    def test_03_all_local_labels_equal_audited_baseline(self):
        actual=extract_pinmap()
        self.assertEqual({n:label for n,(_,label,_) in actual.items()},EXPECTED_LABELS)
    def test_04_exposed_pad_and_reset(self):
        actual=extract_pinmap()
        self.assertEqual(actual[33][:2],("EP_GND_THERMAL_PAD","GND"))
        self.assertEqual(actual[31][:2],("RESET","CODEC_RESET_N"))
    def test_05_spi_i2c_select_is_grounded_locally(self):
        actual=extract_pinmap()
        self.assertEqual(actual[12][:2],("SPI_SELECT","GND"))
        self.assertEqual(actual[9][1],"CODEC_I2C_SCL")
        self.assertEqual(actual[10][1],"CODEC_I2C_SDA")


def resistor_local_pin_labels(ref):
    """Read exact 0-degree R symbol terminal labels on V7.33 baseline."""
    source=SCHEMATIC.read_text(encoding="utf8")
    pattern=r'\(symbol \(lib_id "S3900E:R_DRAFT"\) \(at ([\d.]+) ([\d.]+) 0\)[\s\S]{0,360}?\(property "Reference" "'+re.escape(ref)+r'"[\s\S]{0,160}?\(property "Value" "([^"]+)"'
    matches=list(re.finditer(pattern,source))
    if len(matches)!=1:
        raise AssertionError((ref,len(matches)))
    x,y,value=matches[0].groups()
    x,y=float(x),float(y)
    lab={}
    for name,lx,ly in re.findall(r'\(label "([^"]+)" \(at ([\d.]+) ([\d.]+)',source):
        lab[(round(float(lx),4),round(float(ly),4))]=name
    return (value,lab.get((round(x,4),round(y-5.08,4))),
                  lab.get((round(x,4),round(y+5.08,4))))

class TestCodecStartupBias(unittest.TestCase):
    def test_06_ldo_select_has_4k7_pullup_to_3v3_codec_io(self):
        self.assertEqual(resistor_local_pin_labels("R6206"),
                         ("4.7k","3V3_CODEC_IO","CODEC_LDO_SELECT"))
    def test_07_codec_reset_has_47k_pulldown(self):
        self.assertEqual(resistor_local_pin_labels("R6201"),
                         ("47k","CODEC_RESET_N","GND"))
    def test_08_i2c_pullups_have_intended_rail(self):
        self.assertEqual(resistor_local_pin_labels("R6202"),
                         ("4.7k","CODEC_I2C_SCL","3V3_CODEC_IO"))
        self.assertEqual(resistor_local_pin_labels("R6203"),
                         ("4.7k","CODEC_I2C_SDA","3V3_CODEC_IO"))

if __name__=="__main__":
    unittest.main()
