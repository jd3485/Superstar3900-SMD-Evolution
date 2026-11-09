import re, math, json
from pathlib import Path

def parse(s):
    pattern=re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+)',re.S)
    toks=pattern.findall(s)
    stack=[]; root=None
    for t in toks:
        if t=='(':
            node=[]
            if stack: stack[-1].append(node)
            stack.append(node)
            if root is None: root=node
        elif t==')':
            if not stack: raise ValueError('too many closing parens')
            stack.pop()
        elif t.startswith('"'):
            stack[-1].append(bytes(t[1:-1], 'utf8').decode('unicode_escape'))
        else: stack[-1].append(t)
    if stack: raise ValueError('unclosed parentheses')
    return root

def children(node, name):
    return [n for n in node[1:] if isinstance(n,list) and n and n[0]==name]

def child(node, name):
    xs=children(node,name)
    return xs[0] if xs else None

def pos(xy): return (round(float(xy[1]),4),round(float(xy[2]),4))

def props(item):
    return {x[1]:x[2] for x in children(item,'property')}

def pins_of_lib(lib):
    parts=[]
    def walk(node):
        for n in node[1:]:
            if isinstance(n,list) and n:
                if n[0]=='pin' and len(n)>2 and n[1] in ('input','output','power_in','power_out','passive','no_connect','open_collector','bidirectional','tri_state'):
                    parts.append(n)
                else: walk(n)
    walk(lib)
    return parts

def get_pin_points(file):
    root=parse(Path(file).read_text())
    lib_syms=child(root,'lib_symbols')
    libs={x[1]:pins_of_lib(x) for x in children(lib_syms,'symbol')}
    instances=[]
    for s in children(root,'symbol'):
        name=child(s,'lib_id')[1]; xy=child(s,'at'); angle=float(xy[3]) if len(xy)>3 else 0
        x,y=pos(xy); ref=props(s).get('Reference','?')
        # schematic symbol rotation, KiCad rotation 90 opposite local XY in world after y-inversion
        theta=math.radians(angle)
        for p in libs[name]:
            pp=child(p,'at'); px,py=map(float,pp[1:3]); num=child(p,'number')[1]; pinname=child(p,'name')[1]
            # rotate in cartesian, with local convention and paper Y down. +90 x_pin goes up, as seen in existing schematic
            X=x+px*math.cos(theta)-py*math.sin(theta)
            Y=y-px*math.sin(theta)-py*math.cos(theta)
            instances.append({'ref':ref,'pin':num,'name':pinname,'coord':(round(X,3),round(Y,3)), 'lib_id':name, 'kind':p[1]})
    labels=[]
    for kind in ('label','hierarchical_label','global_label'):
        for l in children(root,kind): labels.append({'name':l[1], 'coord':pos(child(l,'at')), 'kind':kind})
    ncs=[pos(child(n,'at')) for n in children(root,'no_connect')]
    wires=[]
    for w in children(root,'wire'):
        pts=children(child(w,'pts'),'xy')
        if len(pts)==2: wires.append((pos(pts[0]),pos(pts[1])))
    return {'pins':instances,'labels':labels,'no_connect':ncs,'wires':wires,'root':root}

if __name__=='__main__':
    p=Path('/mnt/data/Superstar3900_SMD_Evolution_V1.3/04_KiCad/Gerarchico_Alimentazioni_V1.3')
    for f in sorted(p.glob('*.kicad_sch')):
        d=get_pin_points(f)
        pin_coords={a['coord'] for a in d['pins']}
        labels_bad=[n for n in d['labels'] if n['coord'] not in pin_coords and n['coord'] not in {p for seg in d['wires'] for p in seg}]
        nc_bad=[n for n in d['no_connect'] if n not in pin_coords]
        assigned={a['coord'] for a in d['labels']}|set(d['no_connect'])|{n for xy in d['wires'] for n in xy}
        p_unconn=[n for n in d['pins'] if n['coord'] not in assigned and n['kind'] not in ('no_connect',)]
        print('\n',f.name,'pins',len(d['pins']),'labels',len(d['labels']),'wire',len(d['wires']),'NC',len(d['no_connect']))
        print('unattached labels',len(labels_bad),labels_bad[:12])
        print('unattached NC',len(nc_bad),nc_bad[:12])
        print('unconnected pins',len(p_unconn),p_unconn[:25])
