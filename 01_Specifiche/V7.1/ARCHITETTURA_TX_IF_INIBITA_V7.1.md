# Superstar 3900 SMD Evolution — V7.1 TX modulatore / IF candidate (SOLO STUDIO)

**10 novembre 2026 — NON FABBRICABILE; RF TX NON ABILITATA.** Overlay aggiuntivo alla V7.0. Non modifica gli originali V6.x/V7.0. Questa revisione definisce la conversione di frequenza e un modello *offline* mono-tono, **non** un modulatore audio multitonale completo e **non** una catena di trasmissione operativa.

## Contratto di segnale e inversioni

Il piano RX V6.4 contiene 270 posizioni, incluse 30 ALFA, fRF=25.615..28.305 MHz, LO1=fRF+10.695 MHz (36.310..39.000 MHz). **Riutilizzo solo MATEMATICO**, nessuna programmazione LMX2572 TX autorizzata. Per un TX *candidato*: sorgente IF2 a 455 kHz (DA PROGETTARE), mixer U7201 con LO2=10.240 MHz e IF sulla porta 2 -> RF differenza/somma alle frequenze 9.785/10.695 MHz; un filtro IF1 stretto F7201 (MPN, matching, Q e misura assenti) dovrebbe mantenere 10.695 MHz; mixer U7202 con LO1 sulla porta 6, IF1 sulla porta 2 -> RF differenza nel canale e immagine a LO1+10.695 MHz.

**Inversione importante per USB/LSB.** Con LO1 alto, fRF_out = LO1 − (LO2 + fIF2): per USB fIF2=455kHz−f_audio, per LSB fIF2=455kHz+f_audio; AM/FM centrano la portante a 455kHz; CW candidato a +700Hz sul canale usa 454.3kHz in IF2. Questo *non* prova filtraggio sideband né linearità. Per FM, la deviazione ha segno opposto in IF2: Δf_RF=−Δf_IF2. Frequenza IF2 digitale ad alta velocità, generazione I/Q, DAC/DUC, antialias e filtri analogici **non selezionati**.

| Nodo teorico | AM portante, primo canale A1 | AM portante, ultimo F40 |
|---|---:|---:|
| RF nominale | 25.615 MHz | 28.305 MHz |
| LO1 storico (sola aritmetica) | 36.310 MHz | 39.000 MHz |
| IF2 | 0.455 MHz | 0.455 MHz |
| LO2 | 10.240 MHz | 10.240 MHz |
| IF1 desiderata | 10.695 MHz | 10.695 MHz |
| IF1 indesiderata | 9.785 MHz | 9.785 MHz |
| RF differenza | 25.615 MHz | 28.305 MHz |
| RF immagine | 47.005 MHz | 49.695 MHz |

## Overlay componenti e netlist

- U7201 e U7202: **Mini-Circuits ADE-1+**, CD636, 6 pin: 1/4/5 massa, 2 IF, 3 RF, 6 LO; conversion loss tipico ~5 dB solo nelle condizioni del datasheet, LO nominale +7 dBm. Portata RF/LO 0.5–500 MHz, IF DC–500 MHz. In U7201 il segnale 455 kHz entra sulla **porta IF2**, non sulla porta RF3 (455kHz è sotto 0.5MHz). Dati: https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B e https://www.minicircuits.com/pdfs/ADE-1%2B.pdf
- F7201 (roofing 10.695 MHz), F7202 (filtro RF 25.615–28.305 MHz) sono **segnaposto senza MPN/pinout**, DNP. Nessuna prestazione di immagine/spur validata. Un filtro RF per l'intero intervallo non garantisce da solo la selettività richiesta.
- R7201..R7205 sono *interruzioni 0Ω*, **tutte DNP**. I due mixer sono **DNP**. Nessun connettore RF, antenna, finale o PA TX realizzato. Il blocco U7202.RF3 resta un nome teorico, senza percorso fisico verso un'uscita. **Non collegare F501 RX come filtro TX.**
- Nessun collegamento fisico da U971 LO2 / U7121 driver V7.0 o LMX2572 LO1 ai mixer TX. Le porte LO richiederebbero due budget +7 dBm indipendenti da misurare: **non** inferire il livello da modelli LO RX.
- Nessun rail TX o enable aggiunto; TX_ENABLE_HARD V6.2 resta una logica sperimentale il cui bench jumper J801 è DNI. Il collegamento al PA è assente anche se tutti gli stati logici fossero TRUE.

## Modello di modulazione (non firmware)

`08_Firmware_Prototipi/V7.1/tx_if_offline_v71.py` produce solo vettori numerici AM, FM, USB, LSB e CW mono-tono a frequenza di campionamento di riferimento 3.64 Msps; **non** effettua streaming DAC, GPIO, SPI, abilitazione PA o trasmissioni. I 48ksps codec esistenti non possono essere trattati direttamente come campioni reali a 455kHz: serve un'architettura DUC/DAC/anti-alias qualificata. Il sistema radio TX audio reale, filtro pre-mod, limiter, CTCSS/DCS, selettività e tolleranze restano incompleti.

## Gate e fallimenti possibili

1. DUC/IQ/DAC e filtro 455kHz SSB/CW NON SELEZIONATI. Un singolo tono SSB non dimostra reiezione banda laterale.
2. BPF 10.695MHz, isolamento dal prodotto 9.785MHz e stadio di guadagno IF1 NON VALIDATI.
3. BPF RF, reiezione della somma ~47..50MHz, isolamento RX/TX, commutazione d'antenna, EMI/spurie e feedthrough LO NON VALIDATI.
4. Mixer ADE-1+ pinout candidato, matching, attenuazioni e livelli RF **non misurati**; LO1/LO2 TX assenti e filtri DNP.
5. Qualifica alimentazioni, dissipazione, TX watchdog/fault loop indipendente e approvazione normativa mancanti.
6. Schematico KiCad nativo / ERC / DRC / SPICE / EM / misure su hardware: **NON ESEGUITI**. Nessun ordine PCB. Nessuna TX.

Il prossimo stadio potrà specificare un generatore IF2/DUC e un filtro di trasmissione con prova di isolamento e gate fisico; **non** montare jumper/mixer né riutilizzare un collegamento PA esistente prima dell'intero processo di verifica.
