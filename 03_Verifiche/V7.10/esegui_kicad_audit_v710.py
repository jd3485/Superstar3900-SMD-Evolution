"""Native KiCad 9 ERC/DRC issue inventory, not a production release.

Runs the real KiCad CLI. All reports retained. V5.2 RX standalone currently
fails to load as a root schematic: record that BLOCKER without claiming PASS.
Successful diagnostic inventory != zero violations, valid nets, or approved PCB.
"""
import json
import re
from collections import Counter
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.10"/"output-ci"
FILES={
 "integration_erc":("sch","erc",
     "04_KiCad/Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch"),
 "rx_v52_erc":("sch","erc",
     "04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB/S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_sch"),
 "aux_power_v15_erc":("sch","erc",
     "04_KiCad/Gerarchico_Alimentazioni_V1.5/S3900E_AUX_POWER_V1_5.kicad_sch"),
 "mcu_codec_v21_erc":("sch","erc",
     "04_KiCad/Modulo_MCU_CODEC_V2.1/S3900E_MCU_CODEC_AFE_V2_1_DRAFT.kicad_sch"),
 "rx_v52_pcb_drc":("pcb","drc",
     "04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB/S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_pcb"),
}

def summarize(report):
    categories=Counter(re.findall(r"^\[([^\]]+)\]:",report,re.M))
    d={"categories":dict(categories)}
    erc=re.search(r"ERC messages:\s*(\d+)\s+Errors\s+(\d+)\s+Warnings\s+(\d+)",report)
    if erc:
        d.update(erc_total=int(erc.group(1)),erc_errors=int(erc.group(2)),
                 erc_warnings=int(erc.group(3)))
    drc=re.search(r"Found\s+(\d+)\s+DRC violations",report)
    if drc:
        d["drc_violations"]=int(drc.group(1))
    unconnected=re.search(r"Found\s+(\d+)\s+unconnected",report)
    if unconnected:
        d["drc_unconnected"]=int(unconnected.group(1))
    return d

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    entries={}
    hard_fail=[]
    legacy_unloadable=[]
    for name,(kind,command,relative_path) in FILES.items():
        path=ROOT/relative_path
        output=OUT/(name+".rpt")
        commandline=["kicad-cli",kind,command,"-o",str(output),str(path)]
        proc=subprocess.run(commandline,cwd=ROOT,capture_output=True,
                            text=True,timeout=150)
        log=proc.stdout+"\n"+proc.stderr
        (OUT/(name+".stdout_stderr.txt")).write_text(log,encoding="utf-8")
        report=output.read_text(encoding="utf-8",errors="replace") if output.exists() else ""
        entries[name]={
           "returncode":proc.returncode,
           "report_generated":bool(report),
           "native_kicad_findings":summarize(report),
           "report_path":"output-ci/"+output.name,
           "erc_drc_zero_violations":False,
           "pcb_manufacturing_release":False,
        }
        print(name,"return",proc.returncode,"report_bytes",len(report),
              "counts",entries[name]["native_kicad_findings"],flush=True)
        if proc.returncode!=0 or not report:
            if (name=="rx_v52_erc" and proc.returncode==3 and
                "Failed to load schematic" in log):
                legacy_unloadable.append(name)
            else:
                hard_fail.append(name)
    result={
       "revision":"V7.10",
       "meaning":"Real KiCad 9 diagnostic reports; not qualified for fabrication",
       "checks":entries,
       "known_legacy_root_erc_load_failures":legacy_unloadable,
       "unexpected_native_command_failures":hard_fail,
       "full_native_erc_drc_pass":False,
       "all_commands_generating_reports":not(hard_fail or legacy_unloadable),
       "integration_electrically_complete":False,
       "TX_RF_enabled":False,
       "NO_FAB_NO_TX":True,
    }
    (OUT/"cad_audit_summary.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if legacy_unloadable:
        print("KNOWN LEGACY BLOCKER:",legacy_unloadable,flush=True)
    if hard_fail:
        print("UNEXPECTED KIcad COMMAND FAILURE:",hard_fail,file=sys.stderr)
        return 2
    print("DIAGNOSTIC COMPLETED, VIOLATIONS NOT WAIVED, NO FAB / NO TX")
    return 0

if __name__=="__main__":
    sys.exit(main())
