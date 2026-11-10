"""V7.9 7-pole 50-ohm idealized filter with inductor SRF sensitivity.

This is a WHAT-IF calculation, NOT a vendor SPICE model or an electrically
connected current-output DAC interface. Candidate power inductors selected
for *screening* only: actual Q at 455kHz, mounting parasitics and bias
are not supplied by these vendor webpages. All TX parts remain DNP.
"""
import math
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.3"))
from analizza_reconstruction_lpf_v73 import nominal_elements, insertion_loss_db, FC_HZ, IF2_HZ, FS_HZ

Z0=50.0
# Coilcraft part-specific vendor web page nominal values:
# MSS1260T-472MLD: 4.7uH, 20% tolerance, SRF 38MHz *typical*
# MS590PNB183MSZ: 18uH, 20% tolerance, SRF 11.2MHz *minimum*
# Actual values and model are illustrative. Coilcraft does NOT publish a
# validated 455kHz Q model for our candidate DAC reconstruction filter.
INDUCTORS=(
    ("MSS1260T-472MLD",4.7e-6,38e6,"SRF_TYP"),
    ("MS590PNB183MSZ",18e-6,11.2e6,"SRF_MIN")
)
RF_PERMISSION=False

def tx_permission(**_):
    return False

def _srf_shunt_capacitance(l_h,srf_hz):
    return 1/((2*math.pi*srf_hz)**2*l_h)

def proposed_elements():
    old=nominal_elements()
    output=[]
    for i,(kind,value) in enumerate(old):
        if kind=="L":
            l=INDUCTORS[0][1] if i in (0,6) else INDUCTORS[1][1]
            output.append((kind,l))
        else: output.append((kind,value))
    return tuple(output)

def approximate_abcd(freq_hz, elements, q_l=60, q_c=500,
                     srf_edge=38e6, srf_middle=11.2e6):
    """A simplified lossy ABCD two-port with L parallel C derived from SRF."""
    if not math.isfinite(freq_hz) or freq_hz<=0:
        raise ValueError("positive finite frequency")
    if len(elements)!=7 or not 0<q_l<=10000 or not 0<q_c<=10000:
        raise ValueError("invalid elements or assumptions")
    omega=2*math.pi*freq_hz
    a,d=1+0j,1+0j
    b,c=0j,0j
    for i,(kind,value) in enumerate(elements):
        if kind=="L":
            srf=srf_edge if i in (0,6) else srf_middle
            if not math.isfinite(srf) or srf<=freq_hz:
                raise ValueError("SRF too low to use a sub-resonant L model")
            cp=_srf_shunt_capacitance(value,srf)
            z=complex(omega*value/q_l,omega*value)
            z=1/(1/z+1j*omega*cp)
            a,b,c,d=a,a*z+b,c,c*z+d
        elif kind=="C":
            z=complex(1/(omega*value*q_c),-1/(omega*value))
            y=1/z
            a,b,c,d=a+b*y,b,c+d*y,d
        else:
            raise ValueError("bad component type")
    den=a+b/Z0+c*Z0+d
    s21=2/den
    s11=(a+b/Z0-c*Z0-d)/den
    return s21,s11

def loss_db(freq_hz,**kw):
    s21,_=approximate_abcd(freq_hz,proposed_elements(),**kw)
    return -20*math.log10(max(abs(s21),1e-150))

def evaluate():
    wanted=[IF2_HZ-2700,IF2_HZ,IF2_HZ+2700]
    images=[FS_HZ-IF2_HZ,FS_HZ+IF2_HZ]
    nominal=nominal_elements()
    candidate=proposed_elements()
    base_wanted=max(insertion_loss_db(f,elements=nominal) for f in wanted)
    ideal_sub_wanted=max(insertion_loss_db(f,elements=candidate) for f in wanted)
    srf_wanted=max(loss_db(f) for f in wanted)
    srf_rel_img=min(loss_db(f)-loss_db(IF2_HZ) for f in images)
    differences=[]
    for i,((kind,base),(kind2,proposed)) in enumerate(zip(nominal,candidate)):
        if kind=="L":
            differences.append({"index_1based":i+1,
                "vendor_mpn":INDUCTORS[0][0] if i in (0,6) else INDUCTORS[1][0],
                "nominal_design_uh":base*1e6,
                "catalog_value_uh":proposed*1e6,
                "deviation_percent":100*(proposed/base-1)})
    return {
      "label":"Screening ONLY of mismatched catalog inductors / simplified SRF",
      "assumed_50ohm_source_and_load":True,
      "vendor_q_at_455khz_known":False,
      "vendor_srf_typ_vs_min_mixed":True,
      "srf_middle_min_hz":11.2e6,
      "srf_edge_typ_hz":38e6,
      "assumed_q_l":60,
      "assumed_q_c":500,
      "design_ideal_wanted_loss_db":base_wanted,
      "catalog_nominal_ideal_wanted_loss_db":ideal_sub_wanted,
      "catalog_srf_approx_wanted_loss_db":srf_wanted,
      "catalog_srf_approx_min_image_rel_atten_db":srf_rel_img,
      "catalog_inductor_values":differences,
      "physical_dac_iv_interface_validated":False,
      "vendor_component_model_validated":False,
      "rf_permission":False
    }

if __name__=="__main__":
    print(json.dumps(evaluate(),indent=2,sort_keys=True))
