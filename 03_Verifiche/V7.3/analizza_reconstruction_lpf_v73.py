"""Candidate 7-pole 50-ohm Butterworth LPF: ABCD network, no DAC I/V.

This is a NUMERICAL design study, not vendor S-parameters, SPICE, EM or PCB.
The output of DAC900 is current-mode; it must NEVER be treated as a 50-ohm
voltage source without a qualified separate transimpedance/interface circuit.
"""
import json
import math
import random

Z0_OHM = 50.0
FC_HZ = 850_000.0
IF2_HZ = 455_000.0
FS_HZ = 3_840_000.0
ORDER = 7


def nominal_elements():
    omega = 2*math.pi*FC_HZ
    elements=[]
    for index in range(1,ORDER+1):
        g=2*math.sin((2*index-1)*math.pi/(2*ORDER))
        if index % 2:
            elements.append(("L",g*Z0_OHM/omega))
        else:
            elements.append(("C",g/(Z0_OHM*omega)))
    return tuple(elements)


def abcd_s21(freq_hz, elements=None, q_inductor=float("inf"),
             q_capacitor=float("inf")):
    """Matched 2-port S21/S11 of a ladder with optional simplified Q loss."""
    if not (math.isfinite(freq_hz) and freq_hz>0):
        raise ValueError("frequency must be positive and finite")
    elements=nominal_elements() if elements is None else elements
    if len(elements)!=ORDER or any(t not in ("L","C") or not v>0 for t,v in elements):
        raise ValueError("invalid ladder")
    if q_inductor<=0 or q_capacitor<=0:
        raise ValueError("positive Q required")
    a,d=1+0j,1+0j
    b,c=0j,0j
    omega=2*math.pi*freq_hz
    for kind,value in elements:
        if kind=="L":
            z=complex(omega*value/q_inductor if math.isfinite(q_inductor) else 0,
                      omega*value)
            a,b,c,d=a, a*z+b, c, c*z+d
        else:
            z_c=complex(1/(omega*value*q_capacitor) if math.isfinite(q_capacitor) else 0,
                        -1/(omega*value))
            y=1/z_c
            a,b,c,d=a+b*y,b,c+d*y,d
    denominator=a+b/Z0_OHM+c*Z0_OHM+d
    s21=2/denominator
    s11=(a+b/Z0_OHM-c*Z0_OHM-d)/denominator
    return s21,s11


def insertion_loss_db(freq_hz, **kwargs):
    s21,_=abcd_s21(freq_hz, **kwargs)
    return -20*math.log10(max(abs(s21),1e-200))


def return_loss_db(freq_hz, **kwargs):
    _,s11=abcd_s21(freq_hz, **kwargs)
    return -20*math.log10(max(abs(s11),1e-200))


def evaluate(n_scenarios=400, seed=73):
    if not 1<=n_scenarios<=2000:
        raise ValueError("bounded Monte Carlo only")
    nominal=nominal_elements()
    wanted=[IF2_HZ-2700,IF2_HZ,IF2_HZ+2700]
    images=[FS_HZ-IF2_HZ,FS_HZ+IF2_HZ]
    nominal_loss=max(insertion_loss_db(f) for f in wanted)
    nominal_rel_img=min(insertion_loss_db(f)-insertion_loss_db(IF2_HZ) for f in images)
    q_example_loss=max(insertion_loss_db(f,q_inductor=80,q_capacitor=500) for f in wanted)
    rng=random.Random(seed)
    worst_wanted=0.0
    worst_relative_image=float("inf")
    min_return_loss=float("inf")
    for _ in range(n_scenarios):
        vals=tuple((t,v*(1+rng.uniform(-0.05 if t=="L" else -0.02,
                                          0.05 if t=="L" else 0.02))) for t,v in nominal)
        opts=dict(elements=vals,q_inductor=rng.uniform(40,120),
                  q_capacitor=rng.uniform(200,1000))
        wanted_loss=max(insertion_loss_db(f,**opts) for f in wanted)
        relative_image=min(insertion_loss_db(f,**opts)-insertion_loss_db(IF2_HZ,**opts)
                           for f in images)
        worst_wanted=max(worst_wanted,wanted_loss)
        worst_relative_image=min(worst_relative_image,relative_image)
        min_return_loss=min(min_return_loss,return_loss_db(IF2_HZ,**opts))
    return {
        "label":"7th order 50-ohm mathematical LC LPF, not physical hardware",
        "cutoff_hz":FC_HZ,
        "carrier_hz":IF2_HZ,
        "sample_rate_hz":FS_HZ,
        "image_frequencies_hz":images,
        "elements":[{"kind":k,"value_si":round(v,13)} for k,v in nominal],
        "nominal_max_wanted_loss_db":round(nominal_loss,3),
        "nominal_min_image_relative_attenuation_db":round(nominal_rel_img,3),
        "q80_500_max_wanted_loss_db":round(q_example_loss,3),
        "monte_carlo_scenarios":n_scenarios,
        "mc_max_wanted_loss_db":round(worst_wanted,3),
        "mc_min_relative_image_attenuation_db":round(worst_relative_image,3),
        "mc_min_return_loss_db":round(min_return_loss,3),
        "dac_current_output_interface": "NOT DESIGNED",
        "hardware_verified":False,
        "tx_permitted":False,
    }


if __name__=="__main__":
    print(json.dumps(evaluate(),sort_keys=True,indent=2))
