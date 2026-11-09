from pathlib import Path
import re,math,collections
RX=Path(__file__).resolve().parents[2]/'04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB'
ST='S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB'
PAT=re.compile(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+')
def parse(t):
 toks=PAT.findall(t); pos=0
 def atom(tok):return tok[1:-1].replace('\\"','"') if tok.startswith('"') else tok
 def one():
  nonlocal pos
  assert toks[pos]=='('; pos+=1;r=[]
  while pos<len(toks) and toks[pos]!=')':
   if toks[pos]=='(':r.append(one())
   else:r.append(atom(toks[pos]));pos+=1
  if pos==len(toks):raise ValueError('unbalanced')
  pos+=1;return r
 root=one()
 if pos!=len(toks):raise ValueError('trailing tokens')
 return root

def child(x,name):return next((y for y in x[1:] if isinstance(y,list) and y and y[0]==name),None)
def children(x,name):return [y for y in x[1:] if isinstance(y,list) and y and y[0]==name]
def pval(obj,name):
 for pr in children(obj,'property'):
  if pr[1]==name:return pr[2]
 return None

def xy(x):return tuple(float(v) for v in x[1:3])
def roundxy(a):return tuple(round(v,3) for v in a)
def extract(sch,pcb):
 schema=parse(sch);board=parse(pcb)
 libs={v[1]:v for v in children(child(schema,'lib_symbols'),'symbol')}
 wires=[]; labels={}
 for w in children(schema,'wire'):
  p=[xy(v) for v in children(child(w,'pts'),'xy')];assert len(p)==2
  wires.append((roundxy(p[0]),roundxy(p[1])))
 for l in children(schema,'label'):
  pos=roundxy(xy(child(l,'at')))
  if pos in labels and labels[pos]!=l[1]:raise ValueError('conflicting label')
  labels[pos]=l[1]
 schem={};warn=[]
 for instance in children(schema,'symbol'):
  if not child(instance,'lib_id'):continue
  ref=pval(instance,'Reference'); symid=child(instance,'lib_id')[1]; lib=libs[symid];at=child(instance,'at')
  cx,cy,rot=map(float,at[1:4]);pinmap={}
  for unit in children(lib,'symbol'):
   for pin in children(unit,'pin'):
    number=child(pin,'number')[1];px,py,ang=map(float,child(pin,'at')[1:4]);
    rad=math.radians(rot); dx=px*math.cos(rad)-py*math.sin(rad);dy=px*math.sin(rad)+py*math.cos(rad)
    point=roundxy((cx+dx,cy-dy));links=[(a,b) for a,b in wires if point==a or point==b]
    if len(links)!=1:warn.append((ref,number,'wire_count',len(links),point));continue
    a,b=links[0];far=b if point==a else a; net=labels.get(far,labels.get(point))
    if not net:warn.append((ref,number,'no_label',point,far))
    pinmap[number]=net
  schem[ref]={'nets':pinmap,'footprint':pval(instance,'Footprint'),'value':pval(instance,'Value'),'uuid':child(instance,'uuid')[1]}
 footprints={}
 for f in children(board,'footprint'):
  ref=pval(f,'Reference'); padnets=collections.defaultdict(set)
  for pad in children(f,'pad'):
   net=child(pad,'net');padnets[pad[1]].add(net[2] if net else None)
  footprints[ref]={'nets':{k:sorted(v,key=str) for k,v in padnets.items()},'footprint':f[1],'value':pval(f,'Value'),'path':child(f,'path')[1] if child(f,'path') else None}
 errors=[]
 if set(schem)!=set(footprints):errors.append(['component list',set(schem)^set(footprints)])
 for ref,x in schem.items():
  if ref not in footprints:continue
  f=footprints[ref]
  for pin,net in x['nets'].items():
   if pin not in f['nets'] or f['nets'][pin]!=[net]: errors.append(['PIN-NET',ref,pin,net,f['nets'].get(pin)])
  if set(x['nets']) != set(f['nets']):errors.append(['pin_set',ref,set(x['nets'])^set(f['nets'])])
  if x['footprint']!=f['footprint']:errors.append(['footprint',ref,x['footprint'],f['footprint']])
  if x['value']!=f['value']: errors.append(['value',ref,x['value'],f['value']])
  exp='/'+child(schema,'uuid')[1]+'/'+x['uuid']
  if f['path']!=exp:errors.append(['path',ref,f['path'],exp])
 return {'errors':errors,'warnings':warn,'schematic_pin_nets':schem,'pcb_pad_nets':footprints,'sch_pins':sum(len(x['nets']) for x in schem.values()),'wires':len(wires),'labels':len(labels)}
def check_footprint_libraries(pcb):
    """Compare pad geometry on each board footprint with its portable library model.
    Static comparison only; does not approve vendor mechanical tolerances.
    """
    import collections
    root = parse(pcb)
    tags = ('at','size','layers','options','primitives','solder_paste_margin_ratio','solder_mask_margin','clearance')
    def sig(pad):
        return (tuple(pad[1:4]), tuple(str(child(pad,t)) for t in tags))
    mismatches=[]
    for fp in children(root,'footprint'):
        ref=pval(fp,'Reference');ident=fp[1]
        try:
            lib,mod=ident.split(':',1)
            libpath=RX/(lib+'.pretty')/(mod+'.kicad_mod')
            library_fp=parse(libpath.read_text())
            if library_fp[0]!='footprint':raise ValueError('Not a footprint library')
            aa=collections.Counter(map(str,map(sig,children(fp,'pad'))))
            bb=collections.Counter(map(str,map(sig,children(library_fp,'pad'))))
            if aa!=bb:mismatches.append({'ref':ref,'problem':'PAD_GEOMETRY_DIFFERENT','library':ident})
        except Exception as ex:mismatches.append({'ref':ref,'problem':str(ex),'library':ident})
    return mismatches

if __name__=='__main__':
 import json
 sch=(RX/(ST+'.kicad_sch')).read_text();pcb=(RX/(ST+'.kicad_pcb')).read_text()
 result=extract(sch,pcb)
 libs=check_footprint_libraries(pcb)
 report={'revision':'V5.3','method':'independent static S-expression parsing, pin-coordinate/wire/label tracing', 'schematic_pin_nets':result['sch_pins'],'wires':result['wires'],'labels':result['labels'],'components':len(result['schematic_pin_nets']),'footprints':len(result['pcb_pad_nets']), 'schematic_pcb_errors':result['errors'],'schematic_connection_warnings':result['warnings'],'footprint_library_mismatches':libs,'pass':not (result['errors'] or result['warnings'] or libs),'native_erc':'NOT_RUN','native_drc':'NOT_RUN','manufacturing_allowed':False}
 print(json.dumps(report,indent=2,ensure_ascii=False))
 raise SystemExit(0 if report['pass'] else 2)
