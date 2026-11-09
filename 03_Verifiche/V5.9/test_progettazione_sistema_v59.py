#!/usr/bin/env python3
import sys, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'08_Firmware_Prototipi'/'V5.9'))
from audio_route_v59 import *

class AudioDesign(unittest.TestCase):
    def test_modes(self):
        for mode in RxMode:
            r=route_audio(RouteInputs(mode))
            self.assertEqual(r.selected_demod,mode.value)
            self.assertEqual(r.codec_adc_l,'MIC')
            self.assertEqual(r.codec_adc_r,'RX_DEMOD')
            self.assertEqual(r.codec_dac_l,'RX_AUDIO')
            self.assertEqual(r.codec_dac_r,'MUTE')
            self.assertFalse(r.rf_tx_permission)
    def test_ch9_override(self):
        for mode in RxMode:
            self.assertEqual(route_audio(RouteInputs(mode,ch9_override=True)).selected_demod,'AM')
    def test_pa_priority(self):
        for tx in [False,True]:
            r=route_audio(RouteInputs(RxMode.USB,pa_mode=True,tx_request=tx))
            self.assertEqual(r.speaker,Speaker.PA)
            self.assertEqual(r.codec_dac_l,'MIC_MONITOR')
            self.assertEqual(r.codec_dac_r,'MUTE')
            self.assertFalse(r.rf_tx_permission)
    def test_tx_fail_closed(self):
        for mode in RxMode:
            r=route_audio(RouteInputs(mode,tx_request=True))
            self.assertTrue(r.tx_modulator_muted)
            self.assertEqual(r.codec_dac_r,'MUTE')
            self.assertFalse(r.rf_tx_permission)
    def test_power_loss(self):
        for pa in [False,True]:
            r=route_audio(RouteInputs(RxMode.FM,pa_mode=pa,power_good=False))
            self.assertEqual(r.speaker,Speaker.MUTED)
    def test_transition_mute(self):
        for mode in RxMode:
            r=route_audio(RouteInputs(mode,transition_mute=True))
            self.assertEqual(r.codec_dac_l,'MUTE')
    def test_bad_mode_rejected(self):
        with self.assertRaises(ValueError): route_audio(RouteInputs('SSB'))
    def test_no_hardware_control(self):
        src=(ROOT/'08_Firmware_Prototipi'/'V5.9'/'audio_route_v59.py').read_text()
        self.assertNotIn('HAL_GPIO_WritePin',src)
        self.assertNotIn('rf_tx_permission=True',src)

class ContractDesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/'01_Specifiche'/'V5.9'/'CONTRATTO_MODULI_V5.9.json').read_text())
    def test_module_count(self): self.assertEqual(len(self.d['modules']),26)
    def test_unique_connection_ids(self):
        ids=[e['id'] for e in self.d['connections']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertGreaterEqual(len(ids),50)
    def test_ports_exist_and_types_match(self):
        for e in self.d['connections']:
            fm,fp=e['from'].split('.',1);tm,tp=e['to'].split('.',1)
            self.assertIn(fm,self.d['modules']);self.assertIn(tm,self.d['modules'])
            so=self.d['modules'][fm]['ports'][fp];ti=self.d['modules'][tm]['ports'][tp]
            self.assertEqual(so['direction'],'out');self.assertEqual(ti['direction'],'in')
            self.assertEqual(e['signal_type'],so['signal_type'])
            self.assertEqual(e['signal_type'],ti['signal_type'])
    def test_single_driver_per_input(self):
        inputs=[e['to'] for e in self.d['connections']]
        self.assertEqual(len(inputs),len(set(inputs)))
    def test_five_audio_modes_to_mux(self):
        srcs={e['from'] for e in self.d['connections'] if e['to'].startswith('AF_MUX.') and e['signal_type']=='AF_ANALOG'}
        self.assertEqual(srcs,{f'RX_DEMOD.{m}_af' for m in ('am','fm','usb','lsb','cw')})
    def test_adc_separation(self):
        conns={e['to']:e['from'] for e in self.d['connections']}
        self.assertEqual(conns['CODEC.adc_l'],'MIC_PRE.mic_af')
        self.assertEqual(conns['CODEC.adc_r'],'AF_MUX.rx_selected')
    def test_clock_consistency(self):
        k=self.d['clock_audio']
        self.assertEqual(k['sampling_hz']*k['slots']*k['bits_per_slot'],k['bit_clock_hz'])
        self.assertEqual(k['mclk_hz']//k['sampling_hz'],256)
        self.assertEqual(k['master'],'CODEC')
    def test_hw_rf_inhibit_bypass_absent(self):
        drives=[e['from'] for e in self.d['connections'] if e['to']=='TX_PA.enable_hw']
        self.assertEqual(drives,['SAFETY.tx_rf_enable'])
        self.assertEqual(self.d['tx_default'],'HW_INHIBITED')
    def test_rx_path_complete(self):
        needed=['ANT.rf','TR_SWITCH.rx','RX_BPF.out','RX_LNA.out','RX_MIX.if1','RX_IF.if_demod']
        self.assertTrue(all(x in {e['from'] for e in self.d['connections']} for x in needed))
    def test_tx_chain_has_hardware_gate(self):
        links={(e['from'].split('.')[0],e['to'].split('.')[0]) for e in self.d['connections']}
        for link in [('TX_IF_MOD','TX_MIX'),('TX_MIX','TX_DRIVER'),('TX_DRIVER','TX_PA'),('TX_PA','TX_LPF'),('TX_LPF','ATU_METER'),('ATU_METER','TR_SWITCH'),('SAFETY','TX_PA')]:
            self.assertIn(link,links)
    def test_amp_has_distinct_speakers(self):
        e={(c['from'],c['to']) for c in self.d['connections']}
        self.assertIn(('AUDIO_OUT.radio_speaker','RADIO_SPK.in'),e)
        self.assertIn(('AUDIO_OUT.pa_speaker','PA_SPK.in'),e)
    def test_status_blocks_fabrication(self):
        self.assertIn('NOT_FAB',self.d['status'])
        self.assertTrue(all(e['status']=='CONTRATTO_LOGICO_CANDIDATO' for e in self.d['connections']))

if __name__=='__main__': unittest.main(verbosity=2)
