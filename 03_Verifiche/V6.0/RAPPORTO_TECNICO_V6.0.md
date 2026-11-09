# Rapporto tecnico — Superstar 3900 SMD Evolution V6.0

**Data:** 9 novembre 2026  
**Fase:** progettazione incrementale dell'intera radio; nessuna simulazione o esame nativo KiCad richiesto in questa fase.

## Risultato
Il modulo audio/PA è passato da schema funzionale V5.9 a uno **schema a componenti candidato**, con 64 riferimenti, 206 collegamenti pin-rete e 66 reti nominate. Si tratta di una specifica da disegnare in schemi CAD nelle revisioni successive, non di un circuito pronto per la fabbricazione.

### Sezioni progettate
1. Selettore di 5 audio demodulati AM/FM/USB/LSB/CW con TMUX1308 TSSOP16, S5–S7 parcheggiati, EN attivo basso disabilitato per default.
2. Riferimento VMID_AUD nominale 1,65 V con opamp TLV9062, buffer e primo filtro RC candidato. Codec ADC_R dedicato all'RX, ADC_L al microfono.
3. Amplificatore TPA3111D1 13,8 V candidato, 20 dB, PLIMIT ipotetico, shutdown pull-down e uscita BTL.
4. Relè DPDT per speaker radio NC o PA NO, *entrambi* i conduttori commutati; nessuno collegato a GND.
5. Percorso microfono elettrete, PTT e interfaccia 16-pin al pannello / MCU / sicurezza; in PA audio trasmesso esternamente solo con PTT. **RF TX mai abilitata**.

## Consegne progettuali
- `01_Specifiche/V6.0/SCHEMA_ELETTRICO_COMPONENTI_AUDIO_PA_V6.0.md`
- `01_Specifiche/V6.0/CIRCUITO_COMPONENTI_AUDIO_PA_V6.0.json`
- `01_Specifiche/V6.0/NETLIST_PIN_AUDIO_PA_V6.0.csv`
- `01_Specifiche/V6.0/ELENCO_RETI_AUDIO_PA_V6.0.csv`
- `01_Specifiche/V6.0/DIAGRAMMA_CIRCUITO_AUDIO_PA_V6.0.svg`
- `01_Specifiche/V6.0/MATRICE_PA_RX_AUDIO_V6.0.csv`
- `07_Componenti/BOM_AUDIO_PA_V6.0.csv`
- `08_Firmware_Prototipi/V6.0/audio_controller_v60.py`

## Controlli e criticità
35/35 nuovi test statici superati; matrice esaustiva 5.120 condizioni audio per TX sempre spento. **No simulazione SPICE, no KiCad ERC/DRC, no prototipo.** La scheda codec è esterna, i componenti non scelti e gli interblocchi HW restano apertamente da progettare.

## Da sviluppare in V6.1–V6.2
- Mappa STM32 + pannello vintage, ingressi fisici CH9/ALFA/PA/PTT e GPIO per J604.
- Interblocco PA hardware che renda impossibile TX indipendentemente dal firmware, circuito di consenso AMP_SD e alimentazione protetta.
- Finalizzare MPN di ferriti, relè, connettori, verificare EMC e scariche elettrostatiche; le specifiche meccaniche saranno affrontate nell'iterazione dedicata.

## Fonti tecniche
- TI TMUX1308 https://www.ti.com/lit/ds/symlink/tmux1308.pdf
- TI TLV9062 https://www.ti.com/product/TLV9062
- TI TPA3111D1 https://www.ti.com/lit/ds/symlink/tpa3111d1.pdf
- TI TLV320AIC3204 https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf

**Stato complessivo:** avanzamento storico stimato 37%; ZERO hardware validato; nove gate di produzione restano aperti. NO FAB / PCBWAY / TX.
