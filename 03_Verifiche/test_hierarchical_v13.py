from pathlib import Path
import re
P=Path(__file__).resolve().parents[1]/"04_KiCad"/"Gerarchico_Alimentazioni_V1.3"
root=(P/"S3900E_AUX_POWER_V1_3.kicad_sch").read_text()
assert root.count("(sheet (at ")==3
for k,fn,signals in [("EFUSE","01_EFUSE_AUX.kicad_sch",["PWR_13V8_AUX_RAW","BUCK_VIN_PROTECTED","GND_MAIN"]),("BUCK","02_BUCK_5V.kicad_sch",["BUCK_VIN_PROTECTED","5V_RF_PREREGULATED","GND_MAIN"]),("PLL","03_PLL_LDO_TCXO.kicad_sch",["5V_RF_PREREGULATED","GND_MAIN"])]:
 t=(P/fn).read_text()
 assert fn in root
 for sig in signals:
  assert re.search(r'\(hierarchical_label\s+"'+re.escape(sig)+r'"',t),(k,sig)
  assert re.search(r'\(pin\s+"'+re.escape(sig)+r'"',root),(k,sig)
assert '(xy 115 90) (xy 155 90)' in root
assert '(xy 245 90) (xy 280 90)' in root
assert '(xy 148 135) (xy 148 193)' in root
assert '(pin "EFUSE_RTN"' not in root
print('V1.3: hierarchical sheet matching and power paths static checks PASSED (not KiCad/ERC)')
