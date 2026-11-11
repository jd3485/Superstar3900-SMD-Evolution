"""V7.20: independent ngspice passive filter verification + exact 270-N linear PLL stress.

This is NOT TI PLLatinum Sim and NOT a guarantee of actual VCO gain / phase
noise, calibrations, spurs, lock time, chip register settings or hardware
function. Historical V0.6 model assumptions are exercised, not endorsed.
Python stdlib only. Need ngspice CLI and original .cir source from repository.
"""
import csv
import cmath
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.20"/"output-ci"
OUT.mkdir(parents=True,exist_ok=True)
CIR=ROOT/"04_KiCad"/"Bozze_pre_KiCad"/"Filtro_LMX2572_V0.6_ac.cir"
HIST=ROOT/"03_Verifiche"/"Report_PLL_LMX2572_V0.6.json"
PLAN=ROOT/"02_Piano_Frequenze"/"Tabella_LMX2572_270_Integer_N_V0.5.csv"
CONTRACT=ROOT/"01_Specifiche"/"V7.19"/"CONTRATTO_TOPOLOGIA_LOOP_PLL_TI_V7_19.json"
PREFIX={"p":1e-12,"n":1e-9,"u":1e-6,"m":1e-3,"k":1e3,"meg":1e6}

def number(s):
    m=re.fullmatch(r"([0-9.]+)(meg|[pnumk])?",s.lower())
    if not m:raise ValueError("Unrecognized SPICE value "+s)
    return float(m[1])*PREFIX.get(m[2],1)

def fixture():
    s=CIR.read_text()
    if not s.startswith("* Superstar 3900 V0.6"):
        raise ValueError("Unexpected original SPICE fixture")
    elements={}
    for line in s.splitlines():
        if line.startswith(("C","R","I")) and not line.startswith("*"):
            tokens=line.split()
            if tokens[0] in ("C1","C2","C3","R2","R3"):
                if len(tokens)!=4 or tokens[0] in elements:raise ValueError("Unexpected SPICE element syntax")
                elements[tokens[0]]={"from":tokens[1],"to":tokens[2],"value":number(tokens[3])}
    if set(elements)!={"C1","C2","C3","R2","R3"}:
        raise ValueError("Filter component missing")
    topology={
        "C1":("cp","0"),"C2":("c2node","0"),"C3":("vt","0"),
        "R2":("cp","c2node"),"R3":("cp","vt")}
    for component,(a,b) in topology.items():
        item=elements[component]
        if {item["from"],item["to"]}!={a,b}:
            raise ValueError("Real source SPICE filter not TI 3-pole topology: "+component)
    values={name:elements[name]["value"] for name in elements}
    expected={"C1":220e-12,"C2":120e-9,"C3":2.2e-9,"R2":620.,"R3":22.}
    for name in expected:
        if not math.isclose(values[name],expected[name],rel_tol=1e-12):
            raise ValueError("Unexpected R/C change "+name)
    if "(pin " not in CONTRACT.read_text():
        pass
    contract=json.loads(CONTRACT.read_text())
    if not contract["cad_pin_net_verified"] or contract["vendor_approved_values"]:
        raise ValueError("Contract should be CAD connected only, values still HOLD")
    return values

def z_vtune(f,v):
    s=2j*math.pi*f
    g=1/v["R3"]
    ya=s*v["C1"]+1/(v["R2"]+1/(s*v["C2"]))+g
    yb=s*v["C3"]+g
    return g/(ya*yb-g*g)

def open_loop(f,v,kvco_hz_per_v,n,icp_amp):
    s=2j*math.pi*f
    return icp_amp*kvco_hz_per_v/n * z_vtune(f,v)/s

def crossover(v,kv,n,icp):
    lo,hi=10.,100_000.
    if not(abs(open_loop(lo,v,kv,n,icp))>1 and abs(open_loop(hi,v,kv,n,icp))<1):
        raise ValueError("Unity gain crossing missing from model domain")
    for _ in range(52):
        mid=math.sqrt(lo*hi)
        if abs(open_loop(mid,v,kv,n,icp))>=1:lo=mid
        else:hi=mid
    fc=math.sqrt(lo*hi)
    margin=180+math.degrees(cmath.phase(open_loop(fc,v,kv,n,icp)))
    return fc,margin

def ngspice_crosscheck(v):
    if ".print ac vm(vt) vp(vt)" not in CIR.read_text():
        raise ValueError("Original ngspice fixture no longer exports magnitude/phase")
    with tempfile.TemporaryDirectory() as d:
        log=Path(d)/"ngspice_native.log"
        p=subprocess.run(["ngspice","-b","-o",str(log),str(CIR)],
                         capture_output=True,text=True,timeout=60)
        text=log.read_text(errors="replace") if log.exists() else ""
        if p.returncode:
            raise RuntimeError("ngspice failed: "+text[-1200:]+p.stderr[-700:])
    # AC .print writes tables with columns: Index, frequency, vm(vt), vp(vt).
    # Headers repeat across ngspice pagination; only accept physically valid
    # strictly increasing frequencies in declared sweep [10,1MHz].
    points={}
    for line in text.splitlines():
        m=re.match(r"^\s*\d+\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*$",line)
        if not m:continue
        freq,mag,phase=map(float,m.groups())
        if 9.99<=freq<=1_000_010 and mag>0 and math.isfinite(phase):
            points[freq]={"ngspice_magnitude_ohm":mag,"ngspice_phase_reported":phase}
    if len(points)<90:
        raise ValueError("Expected >=90 genuine ngspice .ac samples, got "+str(len(points))+" "+text[-1100:])
    errors=[]
    for f,row in sorted(points.items()):
        analytical=abs(z_vtune(f,v))
        relative=abs(row["ngspice_magnitude_ohm"]-analytical)/analytical
        errors.append(relative)
    result={"ngspice_ac_points":len(points),"first_freq_hz":min(points),
            "last_freq_hz":max(points),
            "max_relative_magnitude_error":max(errors),
            "examples":[]}
    for target in (100.,1000.,10000.,100000.):
        f=min(points,key=lambda t:abs(math.log(t/target)))
        result["examples"].append({
            "freq_hz":f,"ngspice_zmag_ohm":points[f]["ngspice_magnitude_ohm"],
            "independent_nodal_zmag_ohm":abs(z_vtune(f,v))})
    if max(errors)>0.001:
        raise ValueError("ngspice fixture does not match independent R/C admittance model "+repr(result))
    return result

def ti_vco_kvco_typical(f_vco_hz):
    """TI LMX2572 datasheet SNAS740B Table 135 p64, equation 4 p65.
    These are TYPICAL manufacturer application figures, not process/thermal
    guarantees. VCO calibration or core selection has NOT been configured.
    """
    mhz=f_vco_hz/1e6
    cores=(("VCO3",4200.,4650.,47.,64.),("VCO4",4650.,5200.,50.,73.))
    match=[(name,low,high,kvlow,kvhigh) for name,low,high,kvlow,kvhigh in cores
           if low<=mhz<high]
    if len(match)!=1:
        raise ValueError("VCO frequency outside planned VCO3/VCO4 range "+str(mhz))
    core,fmin,fmax,kvmin,kvmax=match[0]
    kv=kvmin+(kvmax-kvmin)*(mhz-fmin)/(fmax-fmin)
    return core,kv*1e6

def band_sweep(v):
    with PLAN.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=270:
        raise ValueError("Expected exact 270 official project channel entries")
    ns=[int(x["pll_n_integer"]) for x in rows]
    if sorted(ns)!=list(range(3631,3901)) or not all(
        x["status"]=="frequency_arithmetic_only" and
        int(x["pfd_hz"])==1280000 and
        int(x["pll_num"])==0 and int(x["pll_den"])==1 and
        int(x["vco_hz"])==int(x["pll_n_integer"])*1280000 for x in rows):
        raise ValueError("Channel plan not same arithmetic-only 270 integer N")
    out=[]
    for row in rows:
        n=int(row["pll_n_integer"])
        for kv in (39e6,55e6,85e6):
            for icp in (2.3e-3,2.5e-3,2.7e-3):
                fc,pm=crossover(v,kv,n,icp)
                out.append({"n":n,"kvco_hz_per_v":kv,"icp_A":icp,
                            "crossover_hz":fc,"phase_margin_deg":pm})
    # Additional TI typical VCO gain overlay: 270 x one typical CpGain
    # (CPG=4 or 8 both 2500uA, *not* configured in firmware), no PVT claim.
    by_vendor=[]
    for row in rows:
        n=int(row["pll_n_integer"])
        core,kvco=ti_vco_kvco_typical(int(row["vco_hz"]))
        fc,pm=crossover(v,kvco,n,2.5e-3)
        by_vendor.append({"banda":row["banda"],"canale":row["canale"],
                          "n":n,"f_vco_hz":int(row["vco_hz"]),
                          "vco_core_typical":core,"ti_typical_kvco_hz_per_v":kvco,
                          "hypothetical_cpg":4,"crossover_hz":fc,
                          "phase_margin_deg":pm})
    with (OUT/"v720.TI_typical_270_channel_linear_model.csv").open(
            "w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(by_vendor[0]))
        writer.writeheader()
        writer.writerows(by_vendor)
    cores={name:sum(x["vco_core_typical"]==name for x in by_vendor)
           for name in ("VCO3","VCO4")}
    vendor={
        "source":"TI LMX2572 SNAS740B Table 135 p64 and equation 4; charge-pump Table2 p16",
        "status":"TYPICAL_EXTRAPOLATION_ONLY_NOT_HARDWARE_CHARACTERIZATION",
        "core_counts":cores,"cases":len(by_vendor),
        "CPG_nominal_assumed_not_programmed":4,
        "CPG_8_also_gives_2_5mA":True,
        "min_crossover_case":min(by_vendor,key=lambda x:x["crossover_hz"]),
        "max_crossover_case":max(by_vendor,key=lambda x:x["crossover_hz"]),
        "min_phase_margin_case":min(by_vendor,key=lambda x:x["phase_margin_deg"]),
        "max_phase_margin_case":max(by_vendor,key=lambda x:x["phase_margin_deg"]),
        "cases_below_45deg":sum(x["phase_margin_deg"]<45 for x in by_vendor)
    }
    if cores!={"VCO3":2,"VCO4":268}:
        raise ValueError("Project 270 integer VCO3/VCO4 split changed")
    by_fc=sorted(out,key=lambda x:x["crossover_hz"])
    by_pm=sorted(out,key=lambda x:x["phase_margin_deg"])
    return {"channels":len(rows),"cases":len(out),
            "ti_vendor_typical_270_channel_linear_model":vendor,
            "kvco_hz_per_v_assumed":[39e6,55e6,85e6],
            "icp_A_assumed":[2.3e-3,2.5e-3,2.7e-3],
            "min_crossover_case":by_fc[0],"max_crossover_case":by_fc[-1],
            "min_margin_case":by_pm[0],"max_margin_case":by_pm[-1],
            "assumed_cases_below_45deg":sum(x["phase_margin_deg"]<45 for x in out),
            "all_cases_are_hypothetical":True}

def main():
    v=fixture()
    historical=json.loads(HIST.read_text())
    fc,pm=crossover(v,55e6,3750,2.5e-3)
    old=historical["nominal"]
    if not (abs(fc-old["crossover_Hz"])<3 and abs(pm-old["phase_margin_deg"])<0.1):
        raise SystemExit("Independent analytic check differs from V0.6 nominal")
    spice=ngspice_crosscheck(v)
    sweep=band_sweep(v)
    result={
      "revision":"V7.20","method":"actual ngspice passive AC and independent stdlib 2-node complex nodal solver",
      "vendor_product":"TI LMX2572", "pllatinum_sim_executed":False,
      "actual_vco_gain_characterized":False,
      "assumed_icp_registers_programmed":False,
      "validated_phase_noise_or_spurs":False,
      "historical_linear_model_only":True,
      "source_netlist":"04_KiCad/Bozze_pre_KiCad/Filtro_LMX2572_V0.6_ac.cir",
      "component_values_ohm_F":v,
      "nominal_assumptions":{"Kvco_hz_per_v":55e6,"n":3750,"icp_A":2.5e-3},
      "nominal":{"crossover_hz":fc,"phase_margin_deg":pm},
      "historical_nominal_reproduced":True,
      "ngspice_passive_analytical_crosscheck":spice,
      "sweep_exact_270_channel_project_plan":sweep,
      "acceptance":"MODEL_COHERENCE_ONLY_NOT_RF_APPROVAL",
      "all_15_crossmodule_interfaces_open_hold":True,
      "not_for_fabrication":True,"no_tx":True
    }
    out=OUT/"v720.linear_pll_spice_270_channels.json"
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("PASS: ngspice AC matches independent linear model; 270 channel hypothetical sensitivity done. PLLatinum Sim and RF measurements HOLD. NO FAB/TX.")
if __name__=="__main__":main()
