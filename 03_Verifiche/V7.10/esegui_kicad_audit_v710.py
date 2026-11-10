"""Run REAL installed KiCad ERC/DRC on preexisting unqualified sheets and PCB.

Exit code 0 from kicad-cli does NOT imply 0 reported violations unless KiCad
was invoked with --exit-code-violations. Here failures are recorded (not hidden):
the objective is to expose the legacy blockers without treating a draft PCB
as approved for fabrication or exporting fabrication files.
"""
import json
from pathlib import Path
import re
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


def violation_summary(report):
    # Keep raw original report: parsers differ across KiCad 8/9/10.
    # This heuristic is NOT used to certify a design. Counts may be unknown.
    counts={}
    for kind in ("errors","warnings","violations","unconnected"):
        patterns=[
            rf"Found\s+(\d+)\s+{kind}",
            rf"(\d+)\s+{kind}\s+found",
        ]
        for p in patterns:
            m=re.search(p,report,flags=re.I)
            if m:
                counts[kind]=int(m.group(1))
                break
    return counts


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    entries={}
    fatal=[]
    for name,(category,action,relative) in FILES.items():
        f=ROOT/relative
        output=OUT/(name+".rpt")
        args=["kicad-cli",category,action,"-o",str(output),str(f)]
        proc=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,text=True,timeout=150)
        log=(proc.stdout or "")+"\n"+(proc.stderr or "")
        (OUT/(name+".stdout_stderr.txt")).write_text(log,encoding="utf-8")
        text=output.read_text(encoding="utf-8",errors="replace") if output.exists() else ""
        entries[name]={
            "command":" ".join(args),
            "cli_returncode":proc.returncode,
            "report_written":bool(text),
            "heuristic_violation_counts":violation_summary(text),
            "report":"output-ci/"+output.name,
            "legacy_unqualified":True,
            "erc_or_drc_zero_violations_certified":False,
            "manufacturing_release":False,
        }
        if proc.returncode!=0 or not text:
            fatal.append(name)
        print(name,"CLI return=",proc.returncode,"report chars=",len(text),
              "counts=",entries[name]["heuristic_violation_counts"])
    result={
        "revision":"V7.10",
        "meaning":"Native KiCad diagnostic audit of existing drafts, NOT fab certification",
        "kicad_cli_attempts":entries,
        "failed_to_execute":fatal,
        "all_native_checks_executed":not bool(fatal),
        "full_radio_PCB_completed":False,
        "electrical_integration_validated":False,
        "hardware_TX_enabled":False,
        "NO_FAB_NO_TX":True
    }
    (OUT/"cad_audit_summary.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if fatal:
        print("Native KiCad audit BLOCKED or failed:",fatal,file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    sys.exit(main())
