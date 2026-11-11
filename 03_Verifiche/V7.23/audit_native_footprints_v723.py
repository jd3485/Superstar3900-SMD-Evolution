#!/usr/bin/python3
"""Native pcbnew footprint-load gate for vendor review libraries. NO FAB/TX.

This script intentionally does not write .kicad_pcb, assign symbols or export
Gerbers. It independently tests pcbnew's *actual parsed* pad objects instead of
regex matching S-expressions. Manufacturer geometry alone is not DRC signoff.
"""
import json
from pathlib import Path
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"03_Verifiche/V7.23/output-ci/v723.native_footprint_load.json"
FILES={
    "ST_LQFP64": ROOT/"04_KiCad/Librerie_Footprint_V7.22_ST_LQFP_TI_HOLD/S3900E_ST_LQFP_Review.pretty/STM32G474RE_LQFP64_ST_DS12288_CANDIDATE.kicad_mod",
    "TI_RHB0032E": ROOT/"04_KiCad/Librerie_Footprint_V7.22_RHB_TI_HOLD/S3900E_TI_RHB_Review.pretty/TLV320AIC3204_RHB0032E_VENDOR_CANDIDATE.kicad_mod",
    "TI_DBV0005A": ROOT/"04_KiCad/Librerie_Footprint_V7.22_DBV_TI_HOLD/S3900E_TI_DBV_Review.pretty/TPS7A20_DBV0005A_VENDOR_CANDIDATE.kicad_mod",
}
def expected():
    st={}
    for i in range(16): st[i+1]=(-3.75+0.5*i,5.75,.30,1.20)
    for i in range(16): st[i+17]=(5.75,3.75-0.5*i,1.20,.30)
    for i in range(16): st[i+33]=(3.75-0.5*i,-5.75,.30,1.20)
    for i in range(16): st[i+49]=(-5.75,-3.75+0.5*i,1.20,.30)
    rhb={}
    for i in range(8): rhb[i+1]=(-2.40,-1.75+0.5*i,.60,.25)
    for i in range(8): rhb[i+9]=(-1.75+0.5*i,2.40,.25,.60)
    for i in range(8): rhb[i+17]=(2.40,1.75-0.5*i,.60,.25)
    for i in range(8): rhb[i+25]=(1.75-0.5*i,-2.40,.25,.60)
    rhb[33]=(0,0,3.45,3.45)
    dbv={
        1:(-1.30,-.95,1.10,.60),
        2:(-1.30,0,1.10,.60),
        3:(-1.30,.95,1.10,.60),
        4:(1.30,.95,1.10,.60),
        5:(1.30,-.95,1.10,.60),
    }
    return {"ST_LQFP64":st,"TI_RHB0032E":rhb,"TI_DBV0005A":dbv}
def mm(v): return round(pcbnew.ToMM(v),4)
def physical(p):
    at=p.GetPosition()
    size=p.GetSize()
    return (mm(at.x),mm(at.y),mm(size.x),mm(size.y))
def main():
    truth=expected()
    output={"revision":"V7.23","gate":"pcbnew_FootprintLoad_real_native_CAD", "pcbnew_version":pcbnew.GetBuildVersion(), "fabrication_release":False,"TX_release":False,"pcb_created":False,"footprint_assignment":False,"footprints":[]}
    for name,path in FILES.items():
        assert path.is_file(),f"Footprint missing: {path}"
        # KiCad9 native loader reads library path + exact footprint name.
        f=pcbnew.FootprintLoad(str(path.parent),path.stem)
        assert f is not None, f"Native KiCad cannot parse/load: {path}"
        pads=list(f.Pads())
        electrical={}
        pastes=[]
        for pad in pads:
            num=pad.GetNumber()
            layers=pad.GetLayerSet()
            if num:
                assert num.isdecimal(), f"{name}: invalid pad name {num!r}"
                assert layers.Contains(pcbnew.F_Cu), f"{name}: no top copper on physical pad {num}"
                assert layers.Contains(pcbnew.F_Mask), f"{name}: no solder-mask opening on pad {num}"
                n=int(num)
                assert n not in electrical, f"{name}: duplicate physical pad {n}"
                electrical[n]=physical(pad)
                if name=="TI_RHB0032E" and n==33:
                    assert not layers.Contains(pcbnew.F_Paste), "EP33 paste must have windowed apertures"
                else:
                    assert layers.Contains(pcbnew.F_Paste), f"{name}: no paste on pad {n}"
            else:
                assert name=="TI_RHB0032E", f"{name}: unexpected unnumbered pad"
                assert layers.Contains(pcbnew.F_Paste) and not layers.Contains(pcbnew.F_Cu) and not layers.Contains(pcbnew.F_Mask),f"{name}: paste-only pad has copper or mask"
                pastes.append(physical(pad))
        assert electrical==truth[name],f"{name}: vendor pad geometry differs (actual {electrical}, expected {truth[name]})"
        if name=="TI_RHB0032E":
            target={(x,y,1.49,1.49) for x in (-.845,.845) for y in (-.845,.845)}
            assert len(pastes)==4 and set(pastes)==target,f"{name}: incorrect native stencil window geometry {pastes}"
        else: assert not pastes,f"{name}: unexpected extra paste-only pads"
        record={"id":name,"library":str(path.relative_to(ROOT)),"native_loaded":True,
                "numbered_copper_pads":len(electrical),"unnumbered_paste_windows":len(pastes),
                "land_geometry_matches_vendor_example":True,"mask_paste_layers_verified":True,
                "vendor_assembly_release":False}
        output["footprints"].append(record)
    assert sum(x["numbered_copper_pads"] for x in output["footprints"])==102
    assert sum(x["unnumbered_paste_windows"] for x in output["footprints"])==4
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2))
    print("PASS: native KiCad9 PCBNEW loaded 64+33+5 pads and 4 RHB paste windows; HOLD NO FAB/TX")
if __name__=="__main__":
    main()
