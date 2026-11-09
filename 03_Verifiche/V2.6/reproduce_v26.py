#!/usr/bin/env python3
"""Regenerate V2.6 numerical work with the archived V2.5 and V2.4 models.

Run from root: python 03_Verifiche/V2.6/reproduce_v26.py
The original implementation is preserved as 03_Verifiche/V2.6/source_analysis_v26.py.
IMPORTANT: Q-at-27-MHz is NOT manufacturer qualified.
"""
import runpy
from pathlib import Path
source=Path(__file__).with_name('source_analysis_v26.py')
runpy.run_path(str(source),run_name='__main__')
