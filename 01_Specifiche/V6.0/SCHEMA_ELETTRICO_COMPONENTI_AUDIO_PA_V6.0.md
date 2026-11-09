# V6.0 — schema a componenti AUDIO / PA — STUDIO NON FABBRICABILE

La revisione aggiunge **64 riferimenti elettronici**, **206 connessioni pin-rete** e **66 reti nominate**. Non è ancora uno schema ERC/DRC KiCad, perché l'utente ha chiesto di completare prima la radio per revisioni. I dati sono disponibili in JSON e CSV per una futura trascrizione verificabile.

## 1. Canale RX analogico (U601 TMUX1308PWR)
- Ingressi analogici (J605): AM/FM/USB/LSB/CW, con R610–R614 1 kΩ e C610–C614 1 µF di accoppiamento; R620–R624 100 kΩ riportano ogni canale al riferimento VMID_AUD nominalmente 1,65 V. Le sorgenti devono essere limitate al range 0–3,3 V **anche ai transitori**, e la loro dinamica massima va definita con i demodulatori nelle revisioni successive.
- S0=AM pin13, S1=FM pin14, S2=USB pin15, S3=LSB pin12, S4=CW pin1; S5/S6/S7 collegati a VMID_AUD (pin5/2/4). D pin3 è la rete AF_SEL_OUT.
- A0/A1/A2 ai pin 11/10/9; EN attivo basso sul pin6, R601 47 kΩ verso 3V3_AF: **mux spento per default**. A0/A1/A2 hanno 100 kΩ verso AGND, configurazione 000. Pullup/pulldown sono candidati, da verificare per le correnti reali e il riavvio MCU.
- R630/R631 e U602A generano VMID_AUD, U602B bufferizza AF_SEL_OUT. R632 2,2 kΩ e C632 10 nF forniscono un primo polo ideale a **7,23 kHz** (non un filtro anti-alias convalidato). C633 1 µF collega l'uscita ad ADC destro del codec, con polarizzazione interna.

## 2. Microfono (fisicamente separato dalla ricezione)
- J601: MIC+, ritorno, PTT_N e schermatura chassis. Per la configurazione elettrete candidata, MICBIAS codec → R640 2,2 kΩ → MIC_SIGNAL; C640 1 µF → IN1_L del codec. R641 1 kΩ e C641 1 nF per filtro RF preliminare. Nessuna tensione di polarizzazione è applicata all'ingresso codec prima dei condensatori.
- **J606 codec remoto TLV320AIC3204:** pin 13 IN1_L (ADC sinistro MIC), pin 14 IN1_R (ADC destro RX), pin 22 LOL (uscita programma), pin 19 MICBIAS; pin 23 LOR non è collegato a nessuna sezione TX su questa scheda.
- Il progetto usa un microfono elettrete come caso base; un microfono dinamico richiede variante senza polarizzazione e diverso gain budget. Non interscambiare i due tipi senza modifica di schema.

## 3. Amplificatore mono e altoparlanti
- U604 TPA3111D1PWP (HTSSOP-28), alimentazione protetta nominale 13,8 V; il chip richiede 8–26 V. Guadagno candidato 20 dB ponendo GAIN0 pin5 e GAIN1 pin6 bassi. Ingresso INP pin12 via C651 1 µF da cursore RV601 10 kΩ log; INN pin11 via C652 1 µF verso AGND. Il percorso sbilanciato richiede valutazione di rumore e reiezione comune.
- Codec LOL pin22 → C650 1 µF → RV601 10 kΩ log; il codec supporta anche volume digitale. R650 100 kΩ tiene SD pin1 basso (**spento**) in assenza di consenso AMP_SD esterno.
- OUTP pin18/20 è un unico segnale OUTP_RAW; OUTN pin23/25 è OUTN_RAW. Quattro condensatori bootstrap C657–C660 220 nF collegano i rispettivi pin BSP/BSN ai pin OUTx. C653 1 µF su GVDD, C654 1 µF su PLIMIT, C655 220 µF e C656 100 nF di disaccoppiamento locale.
- PLIMIT candidato: R652 51 kΩ GVDD→PLIMIT e R653 20 kΩ PLIMIT→AGND. Con GVDD nominale 7 V produce **1,97 V**; è un'ipotesi di limitazione potenza, NON una potenza certificata. Vale il modello TI con filtro/cablaggio da dimensionare.
- FB601/FB602 (bead EMI) tra i nodi PWM e i contatti comuni di K601 **DPDT break-before-make**. K601 non eccitato→due fili altoparlante radio (NC); eccitato→due fili presa PA esterna (NO). Relè solo mentre SD LOW; parametri contatti, ferriti e connettori TBD.
- **USCITE A PONTE:** J602 e J603 hanno ciascuno solo due fili di carico, nessuno dei quali deve mai andare a GND/AGND/PGND/chassis. Non è un'uscita mono single-ended.

## 4. Comando del relè e sicurezza
- Q601 AO3400A candidata, pilotata da PA_RELAY_CMD attraverso R660 100 Ω e con pulldown R661 100 kΩ; D601 di ricircolo protegge la bobina a 12 V. Uscita FAULT pin2 dell'amplificatore ha pullup R651 10 kΩ sul dominio 3.3 V (da verificare con le caratteristiche di fault open-drain).
- PA_MODE_HW **deve andare anche direttamente al blocco di sicurezza fisico RF** della futura V6.2, indipendentemente dal software. Collegarlo esclusivamente alla MCU non soddisfa il requisito PA_NO_RF.
- Il segnale AMP_SD attivo alto deve venire dal blocco di consenso HW/audio futuro (power-good, fault, relè assestato, clock codec, configurazione); oggi la rete è **solo candidata**, perché la porta di consenso non è ancora circuitalmente definita.
- PA microfono su speaker esterno: selezione PA prioritaria, ma **audio udibile solo con PTT premuto** nella nuova specifica V6.0, riducendo il rischio di feedback. Si richiede compatibilità con l'intento V5.9, che instradava MIC in PA senza ancora definire il gate PTT.

## 5. Limitazioni e dipendenze aperte
- Non esistono ancora PCB, simboli KiCad nativi o validazione ERC/DRC di questa nuova scheda; nessuna simulazione o misura audio effettuata.
- MPN finali del relè, bead, connettori, ESD, driver AMP_SD, scheda codec completa e logica HW TX/PA devono essere definiti. La tipologia di microfono è una scelta provvisoria. I pin fisici del codec sono verificati da TI, ma la scheda codec completa e le sue alimentazioni/clock saranno progettate in seguito.
- Il cablaggio della massa analogica, ritorno PGND e schermo chassis richiede piano EMC; non unire tutte le masse in un unico punto di saldatura arbitrario.
- Volume audio PA/RX e limiti SPL dipendono dall'altoparlante e dalle misure. **No progettazione fabbricabile, no Gerber, TX sempre inibita**.

## 6. Documentazione ufficiale
- TMUX1308 (TI, pinout PW16): https://www.ti.com/lit/ds/symlink/tmux1308.pdf
- TLV9062 (TI, dual RRIO): https://www.ti.com/product/TLV9062
- TPA3111D1 (TI, 28 pin, SD e BTL): https://www.ti.com/lit/ds/symlink/tpa3111d1.pdf
- TLV320AIC3204 (TI, pin13/14/19/22): https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf
