from pathlib import Path
import re,csv,json
base=Path(__file__).resolve().parents[1]
ks=base/'04_KiCad/Sorgenti_Modulo_PLL_V0.8/S3900E_PLL_V0_8_DECOUPLING_DRAFT.kicad_sch'
s=ks.read_text(encoding='utf8')
assert '(paper "A2")' in s
assert s.count('(lib_id "S3900E:')== 26 # U1 + 5 old loop parts + 20 new
expected=['PLL_VCCDIG','PLL_VCCCP','PLL_VCCMASH','PLL_VCCBUF','PLL_VCCVCO2','PLL_VCCVCO','PLL_VBIASVCO','PLL_VREGIN','PLL_VBIASVCO2','PLL_VREFVCO2','PLL_VBIASVARAC','PLL_VREFVCO','PLL_VREGVCO']
for net in expected:assert s.count('"'+net+'"')==2,(net,s.count('"'+net+'"'))
assert s.count('"3V3_PLL_INPUT_FROM_LDO"')==7
assert '3V3_PLL_PENDING_DECOUPLING' not in s
assert len(list(csv.DictReader((ks.parent/'Pin_to_Net_V0.8.csv').open())))==41
print('PASS: V0.8 schematic structural checks (NOT KiCad ERC)')
