#!/usr/bin/env python3
"""Test sintetici riproducibili V1.6. NON collaudi del ricetrasmettitore."""
import sys, math, json, pathlib
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'08_Firmware_Prototipi'))
from dsp_control_v16 import CTCSS_50,detect_ctcss,VoxGate,DualWatch

def run():
    assert len(CTCSS_50)==50 and len(set(CTCSS_50))==50
    fs=8000;n=6400;t=np.arange(n)/fs
    # Scansione di tutti i 50 toni sintetici: test del banco numerico, non del demodulatore.
    for f in CTCSS_50:
        samples=0.17*np.sin(2*np.pi*f*t)
        out=detect_ctcss(samples)
        assert out==f,(f,out)
    # Rumore puro basso non deve aprire il rilevatore demo.
    rng=np.random.default_rng(3900)
    assert detect_ctcss(rng.normal(0,0.01,n)) is None
    # Interferenza voce a 800 Hz e rumore bianco: target non perso in simulazione.
    samples=0.12*np.sin(2*np.pi*100.0*t)+0.07*np.sin(2*np.pi*800*t)+rng.normal(0,.01,n)
    assert detect_ctcss(samples)==100.0
    # Test adiacente: 69.3 non riconosciuto come 67.
    assert detect_ctcss(0.12*np.sin(2*np.pi*69.3*t))==69.3
    gate=VoxGate()
    assert not any(gate.update(.001) for _ in range(20))
    assert not gate.update(.1,speaker_audio_active=True)
    assert not gate.update(.1)
    assert not gate.update(.1)
    assert gate.update(.1)
    assert all(gate.update(.0001) for _ in range(44))
    assert not gate.update(.0001)
    assert not gate.update(.1,pa_mode=True)
    dw=DualWatch()
    assert dw.update(500,enabled=True)=='B'
    assert dw.update(100,enabled=True,signal_valid=True)=='B'
    assert dw.update(600,enabled=True)=='B'
    assert dw.update(100,enabled=True,tx=True)=='A'
    assert dw.update(100,enabled=True,ch9=True)=='CH9'
    assert dw.update(100,enabled=True,pa=True)=='PA'
    # Rigore numerico: ingressi impropri vanno rifiutati.
    try: detect_ctcss(np.zeros(500))
    except ValueError: pass
    else: raise AssertionError('wrong length not rejected')
    return dict(pass_status=True,ctcss_tones_synth_tested=len(CTCSS_50),noise_rejection_samples=1,
                ctcss_mixed_test=1,vox_state_test='PASS',dw_state_test='PASS',
                coverage_note='Solo simulazione numerica; non verifica DCS, analogica, RF o firmware embedded')
if __name__=='__main__':
    result=run();print(json.dumps(result,indent=2,ensure_ascii=False))
