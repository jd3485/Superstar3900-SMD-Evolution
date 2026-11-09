#!/usr/bin/env python3
"""Fail-closed post-validator for KiCad 10 JSON produced by V5.4 runner.
This verifies report structure and internal consistency, NOT provenance or fabrication.
"""
from pathlib import Path
import json, argparse, re, sys

def check_json(obj,kind):
    issues=[]; counts={}
    if not isinstance(obj,dict):return ['TOP_LEVEL_NOT_OBJECT'],counts
    version=obj.get('kicad_version')
    if not isinstance(version,str) or not re.match(r'^10\.\d+(?:\.\d+)?\b',version):issues.append('KICAD10_VERSION_MISSING')
    if not isinstance(obj.get('source'),str) or not obj['source'].endswith('.kicad_'+('sch' if kind=='erc' else 'pcb')):
        issues.append('SOURCE_MISMATCH')
    if not isinstance(obj.get('$schema'),str) or 'schemas.kicad.org' not in obj['$schema']:
        issues.append('KICAD_JSON_SCHEMA_MISSING')
    checks=['sheets'] if kind=='erc' else ['violations','unconnected_items','schematic_parity']
    for field in checks:
        val=obj.get(field)
        if not isinstance(val,list):issues.append(field.upper()+'_ARRAY_MISSING');continue
        counts[field]=len(val)
        if field=='sheets':
            if len(val)==0:issues.append('NO_SCHEMATIC_SHEETS')
            for i,sheet in enumerate(val):
                if not isinstance(sheet,dict) or not isinstance(sheet.get('violations'),list):
                    issues.append('SCHEMATIC_SHEET_INVALID_'+str(i));continue
                counts['sheet_violations']=counts.get('sheet_violations',0)+len(sheet['violations'])
        elif val:
            # We do not silently treat any warnings/exclusions as a clean report.
            issues.append(field.upper()+'_NONEMPTY')
    if counts.get('sheet_violations',0)>0:issues.append('ERC_VIOLATIONS_NONEMPTY')
    severity=obj.get('included_severities')
    if not isinstance(severity,list) or not {'error','warning'}.issubset(set(map(str,severity))):
        issues.append('SEVERITIES_INCOMPLETE')
    return issues,counts

def validate_folder(folder):
    p=Path(folder)
    issues=[];report_counts={}
    try: status=json.loads((p/'STATUS_V5.4.json').read_text())
    except (OSError,ValueError):
        return {'revision':'V5.5','status':'NOT_RUN_OR_MISSING_STATUS','issues':['STATUS_MISSING'],
                'fabrication_allowed':False}
    if not isinstance(status,dict):return {'revision':'V5.5','status':'INCOMPLETE','issues':['STATUS_INVALID'], 'fabrication_allowed':False}
    if not status.get('source_unchanged'):issues.append('SOURCE_NOT_VERIFIED_UNCHANGED')
    if status.get('release')!='BLOCKED_NOT_FOR_FAB' or status.get('fab_authorized') is not False:
        issues.append('FABRICATION_GATE_INVALID')
    for kind in ['erc','drc']:
        if status.get('native_'+kind)!='EXECUTED_REVIEW_REQUIRED' or status.get('native_'+kind+'_exit_code')!=0:
            issues.append('STATUS_'+kind.upper()+'_NOT_EXECUTED_CLEAN')
        name='ERC_V5.4.json' if kind=='erc' else 'DRC_PARITY_V5.4.json'
        try: obj=json.loads((p/name).read_text())
        except (OSError,ValueError):issues.append(kind.upper()+'_REPORT_MISSING_OR_INVALID');continue
        errs,count=check_json(obj,kind)
        issues.extend(kind.upper()+'_'+e for e in errs)
        report_counts[kind]=count
    return {'revision':'V5.5','status':'STRUCTURE_CHECK_PASS_REVIEW_REQUIRED' if not issues else 'INCOMPLETE_OR_VIOLATIONS',
            'issues':issues,'counts':report_counts,'provenance':'NOT_VERIFIED_BY_JSON_ALONE',
            'native_executed_by_this_script':False,'fabrication_allowed':False,
            'note':'Structural validation is not proof of an authentic KiCad execution; review external runner log and approval gates.'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('folder',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=validate_folder(args.folder)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result['status']=='STRUCTURE_CHECK_PASS_REVIEW_REQUIRED' else 5
if __name__=='__main__':sys.exit(main())
