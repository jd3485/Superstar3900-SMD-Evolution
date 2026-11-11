"""V7.21: audit the REAL 7-sheet KiCad BOM/netlist before a single PCB.

Quality gate: 48 not-yet-placed symbols, two unqualified library footprints,
six TI 300mA LDOs, buck/eFuse/fuse headroom, regulator thermal envelope,
input returns and all 15 cross-module signals remain OPEN/HOLD. Numerical
scenarios are design warnings, NOT actual loads or thermal predictions.
"""
import csv,json,re,sys,math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.21"/"output-ci"
OUT.mkdir(parents=True,exist_ok=True)
NET=OUT/"v721.root_v719.net"
ERC=OUT/"v721.root_v719.erc.rpt"
AUX=ROOT/"04_KiCad"/"Gerarchico_Alimentazioni_V7.19_PLL_PINNET_NOT_FOR_FAB"
MCU=ROOT/"04_KiCad"/"Modulo_MCU_CODEC_V7.12_REANNOTATED_NOT_FOR_FAB"/"S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
INTERFACE=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB"/"MATRICE_INTERFACCE_PROPOSTE_V7_17_OPEN_HOLD.csv"
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.17"))
from audit_full_board_native_v717 import native_erc

def native_components(file):
    s=file.read_text(encoding="utf-8",errors="replace")
    if not s.startswith("(export (version ") or "(components" not in s:raise ValueError("not native KiCad netlist")
    chunks=re.findall(r'^    \(comp \(ref "([^"]+)"\)(.*?)(?=^    \(comp |^  \(libparts)',s,re.M|re.S)
    if len(chunks)!=132:raise ValueError(f"unexpected current seven-sheet KiCad component count {len(chunks)}")
    result=[]
    for ref,data in chunks:
        value=re.search(r'^      \(value "([^"]+)"\)',data,re.M)
        footprint=re.search(r'^      \(footprint "([^"]+)"\)',data,re.M)
        path=re.search(r'\(sheetpath \(names "([^"]+)"',data)
        if not value or not path:raise ValueError("Bad native component "+ref)
        result.append({"ref":ref,"value":value.group(1),"footprint":footprint.group(1) if footprint else None,
                       "sheet":path.group(1)})
    if len(set(x["ref"] for x in result))!=132:
        raise ValueError("duplicate component in root netlist")
    return result

def schematic_values(path):
    src=path.read_text(encoding="utf-8")
    rows=re.findall(r'\(symbol \(lib_id "([^"]+)"\) \(at [^)]+\)[\s\S]*?'
                    r'\(property "Reference" "([^"]+)"[\s\S]*?'
                    r'\(property "Value" "([^"]+)"[\s\S]*?'
                    r'\(property "Footprint" "([^"]*)"',src)
    return {ref:{"lib":lib,"value":value,"footprint":footprint}
            for lib,ref,value,footprint in rows}

def parse_resistor(lex):
    m=re.fullmatch(r'([0-9]+)(?:k([0-9]+)|R([0-9]+)?)?(?:\s+1%)?',lex)
    if not m: raise ValueError("Cannot parse known resistor "+lex)
    val=int(m.group(1))
    if m.group(2) is not None:
        val=val*1000+int(m.group(2))*10**(3-len(m.group(2)))
    elif "k" in lex:
        val=val*1000
    elif m.group(3) is not None:
        val+=int(m.group(3))*10**(-len(m.group(3)))
    return float(val)

def map_power_nets(path):
    s=path.read_text(encoding="utf-8")
    chunks=list(re.finditer(r'^    \(net \(code "\d+"\) \(name "([^"]+)"\)',s,re.M))
    if len(chunks)!=100:raise ValueError("Unexpected native KiCad net total")
    nets={}
    for i,m in enumerate(chunks):
        section=s[m.end():chunks[i+1].start() if i+1<len(chunks) else len(s)]
        pins=re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)'
                        r'(?: \(pinfunction "[^"]*"\))? \(pintype "([^"]+)"\)\)',section)
        nets[m.group(1)]=pins
    return nets

def audit():
    comp=native_components(NET)
    byref={x["ref"]:x for x in comp}
    main=schematic_values(AUX/"02_BUCK_5V.kicad_sch")
    efuse=schematic_values(AUX/"01_EFUSE_AUX.kicad_sch")
    mcu=schematic_values(MCU)
    pll=schematic_values(AUX/"03_PLL_LDO_TCXO.kicad_sch")
    if main["U100"]["value"]!="TPS54202DDCR":
        raise ValueError("Buck chip changed")
    if efuse["U200"]["value"]!="TPS26600PWPT":
        raise ValueError("eFuse chip changed")
    if efuse["F200"]["value"]!="1.5A 045101.5MRL CANDIDATO":
        raise ValueError("Candidate fuse changed; requalify its actual part")
    if main["R101"]["value"]!="100k 1%" or main["R102"]["value"]!="13k3 1%":
        raise ValueError("Feedback resistor net-value baseline changed")
    if any(byref[x]["value"]!="TPS7A2033PDBVR" for x in ("U2","U3","U6203","U6204","U6205","U6206")):
        raise ValueError("Six TI 3.3V LDO candidates changed")
    for ref in ("U6201","U6202","U6203","U6204","U6205","U6206"):
        if mcu[ref]["footprint"]!="":
            raise ValueError("Original MCU actual footprint baseline changed; redo certification")
    erc=native_erc(ERC)
    if (erc["errors"],erc["warnings"])!=(36,340):
        raise ValueError("Root KiCad ERC 36/340 baseline changed")
    nets=map_power_nets(NET)
    get=lambda suffix:[(name,pins) for name,pins in nets.items() if name.endswith("/"+suffix)]
    buck=[row for row in get("5V_RF_PREREGULATED") if row[0].startswith("/AUX_POWER_existing")]
    unqualified_mcu_candidate=[row for row in get("5V_RF_PREREGULATED")
                               if row[0].startswith("/MCU_CODEC_AFE_existing")]
    if len(buck)!=1 or len(unqualified_mcu_candidate)!=1:
        raise ValueError("Expected two isolated AUX and MCU 5V candidate names, NOT physically shorted")
    if sum(ref in ("U2","U3") and pin=="1" for ref,pin,_ in buck[0][1])!=2:
        raise ValueError("AUX two LDO input pins not on exact five-volt net")
    digital=get("5V_DIGITAL_FILTERED")
    if len(digital)!=1 or not digital[0][0].startswith("/MCU_CODEC_AFE_existing"):
        raise ValueError("Expected separate MCU filtered five-volt net")
    if sum(ref in ("U6203","U6204","U6205","U6206") and pin=="1"
           for ref,pin,_ in digital[0][1])!=4:
        raise ValueError("Four MCU LDO input nets changed")
    if buck[0][0]==digital[0][0]:
        raise ValueError("Do not automatically short 5V rails across modules")
    aux_gnd=get("GND_MAIN")
    mcu_gnd=get("GND")
    if len(aux_gnd)!=1 or len(mcu_gnd)!=1 or aux_gnd[0][0]==mcu_gnd[0][0]:
        raise ValueError("GND partition/architecture unexpectedly changed")
    with INTERFACE.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=15 or any(r["physical_connection"]!="OPEN" or
                            r["qualification"]!="HOLD" or r["tx_permission"]!="0" for r in rows):
        raise ValueError("Crossmodule interface contract prematurely released")
    missing=[x for x in comp if not x["footprint"]]
    if len(missing)!=48:
        raise ValueError("Number of missing footprints changed: explicit update required")
    missing_by_module=Counter("MCU_CODEC" if "MCU_CODEC" in x["sheet"]
                              else "AUX_ROOT" if x["sheet"]=="/AUX_POWER_existing_V1_5_UNQUALIFIED/"
                              else "OTHER" for x in missing)
    if dict(missing_by_module)!={"MCU_CODEC":46,"AUX_ROOT":2}:
        raise ValueError("Mismatch in missing-footprint module partition")
    unvalidated=[x for x in comp if x["footprint"] and
                 ("UNVALIDATED" in x["footprint"] or "NON_VALIDATO" in x["footprint"])]
    if set(x["ref"] for x in unvalidated)!={"Y1","F200"}:
        raise ValueError("Unvalidated third-party footprint references changed")
    if any(x["ref"] in {ref for ref in ("U6201","U6202","U6203","U6204","U6205","U6206")}
           for x in comp if x["footprint"]):
        raise ValueError("Major MCU and codec parts improperly declared placed")
    # TI component ratings: TPS54202 2A continuous, TPS7A20 300mA, TPS2660 up to 2.23A adjustable.
    # Buck output is *not* same-domain current as upstream 13.8 V fuse.
    buck_max_A=2.0
    efuse_adjmax_A=2.23
    ldo_max_A=.3
    n_ldo=6
    rtheta_dbv_K_W=187.1  # TI TPS7A20 SBVS338H 5.4 JEDEC DBV 5-pin
    vinput=5.0
    voutput=3.3
    power_W=(vinput-voutput)*ldo_max_A
    rise_K=power_W*rtheta_dbv_K_W
    ambient_C=40
    je_dec_junction_C=ambient_C+rise_K
    tj_opmax_C=125
    t_ambient_cases={str(t):{"Iout_case_A":ldo_max_A,
                 "p_loss_case_W":power_W,
                 "je_dec_dbv_rtheta_rise_C":rise_K,
                 "modelled_Tj_C":t+rise_K,
                 "maximum_current_at_Tj125_case_A":(tj_opmax_C-t)/(rtheta_dbv_K_W*(vinput-voutput))}
                 for t in (25,40,60)}
    upper=100000.0;lower=13300.0
    ref_nom=.596
    fb={"ratio_nominal":upper/lower,
        "vout_nominal_V":ref_nom*(1+upper/lower),
        "vout_min_reference_tolerance_and_resistor_V":.581*(1+upper*.99/(lower*1.01)),
        "vout_max_reference_tolerance_and_resistor_V":.611*(1+upper*1.01/(lower*.99)),
        "source":"TI TPS54202 SLVSD26C 2026 Vref 0.581 to 0.611 / 0.596 nominal, R101 100k1%, R102 13k3 1%",
        "not_guaranteed_final_vout_without_load_and_layout":True}
    if not (5.07<fb["vout_nominal_V"]<5.09):
        raise ValueError("Buck feedback sanity check failed")
    if not je_dec_junction_C>125:
        raise ValueError("Critical thermal derating scenario no longer in warning range")
    if not math.isclose(ldo_max_A*n_ldo,1.8,abs_tol=1e-9):
        raise ValueError("LDO inventory unexpectedly changed")
    bysheet=defaultdict(lambda:{"total":0,"assigned":0,"missing":0})
    for row in comp:
        r=bysheet[row["sheet"]]
        r["total"]+=1
        r["assigned" if row["footprint"] else "missing"]+=1
    result={
       "revision":"V7.21","native_method":"real KiCad9 export of full seven-sheet V7.19 root and unrestricted KiCad ERC",
       "board_status":"BLOCKED_NOT_READY_FOR_LAYOUT_RELEASE",
       "full_radio_netlist_components":len(comp),
       "footprints_assigned":len(comp)-len(missing),
       "footprints_missing":len(missing),
       "missing_by_module":dict(missing_by_module),
       "not_vendor_qualified_assigned_footprints":[{"ref":r["ref"],"footprint":r["footprint"]} for r in unvalidated],
       "missing_footprint_full_ledger":"v721.missing_footprints.csv",
       "module_component_counts":dict(bysheet),
       "power_rails":{
          "aux_5v_native_net":buck[0][0],
          "mcu_5v_native_net":digital[0][0],
          "AUX_5v_to_MCU_5v_connected":False,
          "GND_MAIN_and_MCU_GND_connected":False,
          "source_13V8_qualified":False,
          "EFUSE_RTN_return_path_qualified":False
       },
       "manufacturer_ratings":{
          "TPS54202_output_continuous_max_A":buck_max_A,
          "TPS26600_adjustable_limit_high_end_A":efuse_adjmax_A,
          "TPS7A20_each_ldo_max_A":ldo_max_A,
          "number_of_ldos":n_ldo,
          "ldos_on_aux_5v":2,
          "ldos_on_isolated_mcu_5v":4,
          "six_LDOs_simultaneous_nameplate_upper_A":1.8,
          "two_AUX_LDOs_simultaneous_nameplate_upper_A":.6,
          "MCU_5v_load_not_physically_added_to_buck":True,
          "fuse_F200_candidate_A":1.5,
          "nameplate_currents_are_not_measured_load":True
       },
       "TPS54202_schematic_feedback_nominal_and_tolerance_scenario":fb,
       "TPS7A20_DBV_JEDEC_thermal_screen":{
          "TI_thermal_resistance_RthetaJA_C_per_W":rtheta_dbv_K_W,
          "LDO_candidate_input_V":vinput,
          "LDO_candidate_output_V":voutput,
          "maximum_nameplate_current_A":ldo_max_A,
          "test_case_ambient_C":ambient_C,
          "test_case_junction_C":je_dec_junction_C,
          "at_40C_300mA_exceeds_Tj125":je_dec_junction_C>tj_opmax_C,
          "JEDEC_theta_depends_on_PCB_not_certification":True,
          "case_table":t_ambient_cases,
          "ldo_loads_typical_max_inrush_known":False,
          "actual_PCB_thermal_qualified":False
       },
       "acceptance_gate":{
          "no_existing_comp_value_changed":True,
          "no_new_crossmodule_net_ties":True,
          "no_fictitious_current_budget_filled":True,
          "no_power_net_driver_faked":True,
          "component_or_mechanical_footprint_qualified":False,
          "mechanical_enclosure_dimensions_known":False,
          "full_radio_single_pcb_created":False,
          "root_erc_errors":erc["errors"],"root_erc_warnings":erc["warnings"],
          "crossmodule_interfaces_OPEN_HOLD":15,
          "NO_FAB":True,"NO_TX":True
       }
    }
    with (OUT/"v721.missing_footprints.csv").open("w",newline="",encoding="utf-8") as handle:
        w=csv.DictWriter(handle,fieldnames=["ref","value","sheet","footprint","qualification"])
        w.writeheader()
        for item in sorted(missing,key=lambda x:x["ref"]):
            w.writerow({**item,"qualification":"HOLD_MISSING_PACKAGE_AND_PINOUT"})
    (OUT/"v721.native_board_foundations.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("PASS V7.21: exact 132 native components / 48 footprints missing / 2 vendor-unverified / 6 LDO thermal HOLD; root 36/340, no PCB or TX released")
    return result

if __name__=="__main__":audit()
