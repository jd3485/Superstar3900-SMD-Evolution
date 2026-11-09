"""Independent geometric KiCad draft audit. This is NOT KiCad ERC or netlist export."""
from pathlib import Path
import json, re, collections
from sexpr_geometry_v14 import get_pin_points, child, children
ROOT = Path(__file__).resolve().parents[1]
P = ROOT/'04_KiCad'/'Gerarchico_Alimentazioni_V1.5'
files = [P/'S3900E_AUX_POWER_V1_5.kicad_sch',P/'01_EFUSE_AUX.kicad_sch',P/'02_BUCK_5V.kicad_sch',P/'03_PLL_LDO_TCXO.kicad_sch']
report={'revision':'V1.5','check_kind':'independent static geometric + hierarchical structure; NOT native KiCad ERC', 'files':[], 'critical_unresolved':['J100 physical footprint and current qualification','F200 validated footprint','TXC Y1 pin 10 is AFC OR GND depending exact device option','KiCad native ERC/netlist export unavailable','Transient/surge/EMI testing not performed','PCB and hardware prototype absent']}

for f in files:
    d = get_pin_points(f)
    pins=d['pins']; coords={x['coord'] for x in pins}; lbl=d['labels']; ncs=d['no_connect']; wires=d['wires']; wirepoints={xy for pair in wires for xy in pair}
    # Hierarchical sheet pin terminals are legal connection points for root local labels.
    coords.update({tuple(round(float(v),4) for v in child(sp,'at')[1:3]) for sh in children(d['root'],'sheet') for sp in children(sh,'pin')})
    invalid_labels=[x for x in lbl if x['coord'] not in coords|wirepoints]
    invalid_nc=[x for x in ncs if x not in coords]
    unresolved_pins=[p for p in pins if p['coord'] not in coords.intersection({x['coord'] for x in lbl}|set(ncs)|wirepoints) and p['kind']!='no_connect']
    root=d['root']; uuids=[x[1] for x in children(root,'uuid')]
    # enumerate UUIDs throughout this schematic
    def alluuids(n):
        ans=[]
        if isinstance(n,list):
            if n and n[0]=='uuid': ans.append(n[1])
            for item in n[1:]: ans.extend(alluuids(item))
        return ans
    all_ids=alluuids(root)
    bad_uuids=[(x,n) for x,n in collections.Counter(all_ids).items() if n>1]
    physical_pins=[(x['ref'],x['pin']) for x in pins]
    duplicate_pins=[(x,n) for x,n in collections.Counter(physical_pins).items() if n>1]
    assert not invalid_labels,(f.name,'floating labels',invalid_labels)
    assert not invalid_nc,(f.name,'NC not at pin',invalid_nc)
    assert not unresolved_pins,(f.name,'unmarked pins',unresolved_pins)
    assert not bad_uuids,(f.name,'repeated uuid',bad_uuids)
    assert not duplicate_pins,(f.name,'duplicate pin',duplicate_pins)
    info={'file':f.name,'pin_count':len(pins),'labels':len(lbl),'wires':len(wires),'no_connects':len(ncs),'unanchored_labels':0,'unmarked_pins':0,'misplaced_no_connect':0,'duplicate_uuid':0,'duplicate_component_pins':0}
    report['files'].append(info)

main=get_pin_points(files[0]); sr=main['root']
sheets=children(sr,'sheet')
assert len(sheets)==3
for sheet in sheets:
    filename=next(p[2] for p in children(sheet,'property') if p[1]=='Sheetfile')
    sh_pins={p[1] for p in children(sheet,'pin')}
    assert filename in [f.name for f in files[1:]],filename
    leaf=get_pin_points(P/filename)
    leaves={p['name'] for p in leaf['labels'] if p['kind']=='hierarchical_label'}
    assert sh_pins==leaves,(filename,sh_pins,leaves)
    assert 'EFUSE_RTN' not in sh_pins

conn=[x for x in main['pins'] if x['ref']=='J100']
assert len(conn)==2 and {p['pin'] for p in conn}=={'1','2'}
netlabels={p['coord']:p['name'] for p in main['labels']}
assert netlabels[next(p['coord'] for p in conn if p['pin']=='1')]=='PWR_13V8_AUX_RAW'
assert netlabels[next(p['coord'] for p in conn if p['pin']=='2')]=='GND_MAIN'
assert '(property "Footprint" ""' in files[0].read_text() # intentionally pending physical selection
pll=get_pin_points(files[3]); plllabels=pll['labels']
for x,name in [(30,'PLL_VCCDIG'),(78,'PLL_VCCCP'),(126,'PLL_VCCMASH'),(174,'PLL_VCCBUF'),(222,'PLL_VCCVCO2'),(270,'PLL_VCCVCO')]:
    anchor=(float(x),212.5)
    assert any(l['name']==name and l['coord']==anchor for l in plllabels)
    assert ((float(x),206.08),anchor) in pll['wires']
    assert (anchor,(float(x),218.92)) in pll['wires']
for leaf in files[1:]:
    d=get_pin_points(leaf)
    for p in d['pins']:
        # The TPS26600 pin RTN and GND physically must remain distinct. Across other pages no EFUSE_RTN.
        if p['ref']=='U200' and p['pin'] in ('8','9'):
            attached={x['name'] for x in d['labels'] if x['coord']==p['coord']}
            assert attached==({'EFUSE_RTN'} if p['pin']=='8' else {'GND_MAIN'}),attached
    if leaf.name!='01_EFUSE_AUX.kicad_sch':
        assert 'EFUSE_RTN' not in {x['name'] for x in d['labels']}

report['hierarchy_children']=3
report['J100_electrical_nets']={'1':'PWR_13V8_AUX_RAW','2':'GND_MAIN'}
report['PLL_wire_label_splits']=6
report['efuse_rtn_separated_by_named_nets']=True
report['pass_static_geometry']=True
report['native_erc_executed']=False
report['native_netlist_export_executed']=False
out=ROOT/'03_Verifiche'/'Report_Audit_Connettivita_V1.5.json'
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('PASS V1.5: 4 files, 3 child sheets, labels anchored incl. SPI sheet pins, EFUSE_RTN isolated.')
print('WARNING: static geometry audit only; KiCad ERC/netlist NOT performed.')
