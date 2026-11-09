"""Deterministic *ideal digital* candidate V6.2 hardware model, not firmware release.
The model represents the AND/NOT gate netlist and refuses any TX when jumper absent.
"""
import json
from pathlib import Path

def load_contract(root):
    return json.loads((Path(root)/'01_Specifiche/V6.2/CIRCUITO_INTERBLOCCHI_V6.2.json').read_text(encoding='utf8'))

def evaluate(data, inputs):
    s={str(k):bool(v) for k,v in inputs.items()}
    allowed_input={'SUP_3V3_OK','BAT_UV_OK','BAT_OV_OK','RX_SAFE_NC','PA_MODE_HW',
                   'FAULT_LOOP_OK','TX_ARM_REQUEST','PTT_N','TX_BENCH_KEY','AMP_SD_REQUEST',
                   'CODEC_READY','AMP_FAULT_N','PA_RELAY_CMD'}
    if not set(s).issubset(allowed_input):
        raise ValueError('Unrecognized inputs: '+repr(set(s)-allowed_input))
    # All active-high inputs are LOW until asserted; active-low PTT defaults HIGH (not pressed)
    states={k:(k=='PTT_N') for k in allowed_input}
    states.update(s)
    # enforce physical double-throw transition: simultaneously RX and PA high cannot grant TX;
    # gate NOT_PA also physically denies TX independently.
    for item in data['gates']:
        assert item['a'] in states, 'missing driver '+item['a']
        if item['type']=='NOT': states[item['y']]=not states[item['a']]
        else:
            assert item['b'] in states, 'missing driver '+item['b']
            states[item['y']]=states[item['a']] and states[item['b']]
    return states

def tx_permitted(data,inputs):
    return evaluate(data,inputs)['TX_ENABLE_HARD']
