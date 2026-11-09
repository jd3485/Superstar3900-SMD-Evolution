# V6.7 — Circuito RX front end, 50 Ω (STUDIO, NO FAB, RX ONLY)

**Flusso previsto:** ingresso J701 **isolato da ogni trasmettitore** → D701 TVS ESD candidato in parallelo al segnale/terra (DNI fino alla qualificazione) → filtro schermato F501 SXBP-27R5+ → C701 DC-block 100 nF → U101 ADL5535 pin1 → pin3 RFOUT/VCC → C702 DC-block 100 nF → attenuatore PI selezionabile con assemblaggio R701/R702/R703 → J702 → U501 ADE-1+ pin3 RF. **J701 non è il connettore dell'antenna condivisa con la TX**: l'eventuale commutatore d'antenna con isolamento TX è DA PROGETTARE e l'ingresso va collegato SOLO a generatore RF attenuato da banco durante prove future.

## Riferimenti reali e netlist

- D701: Semtech RClamp2271ZC, protezione ESD 1 linea ±22V, **capacitance 0.2pF max**, 2 terminali, possibile per RF antenna. Il suo modello lineare nello script è soltanto la capacità; **non dimostra immunità ai transienti, ai segnali forti né isolamento TX**. Le connessioni fisiche alle pad e la variante di layout vanno confrontate col datasheet. DNI nella build nominale.
- F501: Mini-Circuits SXBP-27R5+, pin1 RF_IN, pin8 RF_OUT, 2…7 GND. 50 Ω, 24–31MHz; IL max2.5dB e stopband >=20dB a 39–900MHz, a 25°C. La reiezione 20dB è il solo valore *minimo* da cui partire, non una specifica sufficiente per tutte le interferenze.
- U101: ADL5535 SOT-89, **pin1 RFIN, pin2 e paddle GND, pin3 RFOUT + alimentazione 5 V**. L701 470nH fra 5V_RF_RX_DECOUPLED e pin3. C701/C702 100nF blocco DC, C703 68pF + C704 1.2nF + C705 1uF a massa dal ramo 5V. Componenti riportati dalla fig.16/tab.5 datasheet ADI. Un circuito precedente di U101 esiste nella V5.x: questa è una **ECO candidata**, NON un nuovo U101 fisico duplicato o un aggiornamento automatico del PCB.
- R701/R702/R703 configurazioni **mutuamente esclusive**: `BYPASS` = R701 0Ω, R702/R703 DNI; `PAD6` = R701 37.4Ω, R702/R703 150Ω, Pi 50 Ω circa 6dB. Il pad POST-LNA protegge la dinamica del mixer ma **NON il LNA contro i blocker**.
- J703: 5V_RF_RX_DECOUPLED è richiesta condizionata da RX_ENABLE_HW. Il commutatore di potenza hardware sul ramo **NON è ancora sviluppato** e viene indicato come *CONNESSIONE APERTA*; niente autorizzazione TX, interblocco PA indipendente da confermare.
- Interfaccia LO resta V6.4 → V6.5: **+7dBm al mixer richiesti ma non verificati**. IF 10.695MHz viene indirizzata alla futura catena FI V6.8.

## Vincoli progettuali espliciti

1. Qualificare rating ESD/antenna, isolamento antenna RX/TX, potenza RF residua sul RX durante TX, gestione PTT; non collegare a trasmettitore.
2. A 20–70MHz il datasheet ADL5535 riporta gain tip 16.7/16.5dB, NF tip 3.0dB, P1dB uscita 17.7/18.9dBm, OIP3 41.5/43.5dBm. **Non trattare interpolazioni o valori tipici come minimi garantiti**; +20dBm RF in assoluto (non regime operativo).
3. Il datasheet ADL5535 richiede saldatura pad alla massa a bassa impedenza. Layout termico, return RF, stackup e SMAs storici non ancora qualificati.
4. Il filtro F501 può lasciare >= -20dB della potenza immagine in un caso limite di datasheet: questa revisione NON dichiara raggiunto un target di image rejection 40dB. Un secondo stadio filtrante o altra architettura potrà servire.
5. Il mixer ADE-1+ ha perdita di conversione tip circa 5dB e IIP3 tip +15dBm su specifiche vendor globali; **NF=perdita di conversione è solo una proxy ideale** e non una NF SSB caratterizzata.
6. Eventuali interferenze vicino al canale (es. ±10kHz) passano un filtro così largo. Selettività FI, AGC e DSP rimangono da completare.
7. Per uno scenario antenna input blocker 0dBm, modello con filtro 1.3dB e U101 +16.5dB → +15.2dBm al mixer senza pad, +9.2dBm con pad 6dB; lo stesso blocker resta +15.2dBm all'uscita U101 in entrambi i casi. Non è approvazione di sopravvivenza né prova di linearità.

**Fonti primarie:** https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf ; https://www.minicircuits.com/pdfs/SXBP-27R5%2B.pdf ; https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B ; https://www.semtech.com/products/circuit-protection/antenna/rclamp2271zc

**Stato:** COMPONENT CANDIDATE / NO NATIVE KICAD ERC/DRC / NO VNA / NO FAB / NO TX.
