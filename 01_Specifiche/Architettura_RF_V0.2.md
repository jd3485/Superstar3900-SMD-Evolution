# Architettura RF del Superstar 3900 SMD Evolution - studio V0.2

**Stato:** SCELTA DI STUDIO, non congelata per produzione. **Data:** 2026-11-06.

## 1. Scopo e regole progettuali
Riprogettare il Superstar 3900 come ricevitore supereterodina di alta qualita, prevalentemente SMD, con catena TX CB separata. La robustezza RF (distorsione/intermodulazione, isolamento, filtri, spurie, rumore di fase) prevale sulla miniaturizzazione a ogni costo. L'ingresso e i trasformatori SMD non possono essere scelti guardando il solo footprint: contano Q, tensione, perdite, saturazione e temperatura.

## 2. Architettura ricevente proposta (non equivalente allo schema storico)
SO-239 -> limitatore/protezione ESD a bassa capacita -> relè/routing RX/TX -> attenuatore RF selezionabile 0/10/20 dB -> **sei preselector passabanda commutati**, grosso modo uno per banda A-F (passanti e pendenze DA SIMULARE) -> LNA a basso rumore con bypass/AGC -> mixer bilanciato + LO filtrato -> FI1 **10,695 MHz** -> due percorsi:

- **SSB (USB/LSB):** filtro quarzi circa 2,4 kHz, amplificazione FI, AGC, BFO/PRODOTTO, filtro audio e DSP disattivabile.
- **AM/FM:** filtro FI con larghezza da determinare, secondo mixer a **455 kHz** come ipotesi, demodulatori AM e FM dedicati, AGC, NB/ANL e filtro audio.

Il passaggio fra AM/FM/SSB e gli accoppiamenti FI dovranno essere collaudati per evitare perdita di guadagno, saturazione e reiezione insufficiente. Il filtro a quarzi 10,695 MHz/2,4 kHz non e stato ancora scelto: disponibilita e corrispondenza alla FI sono **rischio aperto**.

## 3. Sintesi LO - proposta ADF4351 (studio, con dati verificabili)
- U1 **ADF4351BCPZ** 3,3 V, sintetizzatore Integer-N/Fractional-N con VCO 2,2..4,4 GHz e divisore uscita /64 (sorgente ADI).
- Riferimento ipotizzato: TCXO 12,800000 MHz; versione/precisione/rumore residuo del TCXO **ancora da selezionare**.
- Contatore di riferimento: R=20, senza raddoppio o divide-by-2 addizionali.
- PFD: 640 kHz; uscita /64; ritorno di anello dal **VCO fondamentale** (Register 4, feedback select=1), non dall'uscita gia divisa.
- Per ogni f_RF: f_LO=f_RF+10.695.000 Hz; f_VCO=64*f_LO; N_INT=f_VCO/640.000=f_LO/10.000. FRAC=0, MOD=2 indicativo.
- 270 canali: f_LO 36,310..39,000 MHz; f_VCO 2323,84..2496,00 MHz; N 3631..3900. Nessun errore di calcolo nominale.
- Registro R4: feedback=fondamentale, divisore di uscita 64, mute-till-lock; banda VCO: clock band-select 640k /8=80kHz (sotto i 125kHz indicati nel datasheet; **valore iniziale, non registro definitivo**).
- Registro R2: impostazione lock detector Integer-N; R3: parametro antibacklash proposto 3 ns secondo indicazione datasheet. Valori esatti di tutti i registri, tempi di lock e loop filter **da progettare**.

**Perche ADF4351 e un candidato e non ancora approvato:** il divisore /64 permette l'uscita di 36-39 MHz, ma lo spettro a breve distanza dalla portante e l'accoppiamento di residui VCO/GHz devono essere provati. Il mixer SMT ADE-1+ richiede ~+7 dBm LO: l'uscita ADF4351 nominale arriva fino a circa +5 dBm, quindi serve potenzialmente un buffer/amplificatore LO, con filtro e isolamento. La perdita di potenza nel filtro rende il buffer ancora piu importante. Nessun nodo LO va collegato direttamente senza verifica dei livelli e adattamento.

**Rischi:** spurie reference 640kHz e armoniche dei divisori; rumore di fase e reciprocal mixing; accoppiamenti a 2,3..2,5GHz; lock transitorio durante cambio canale; EMI verso audio/display; purezza spettrale TX. Valutare alternativa fractional-N a PFD superiore o VCO discreto qualora falliscano le misure.

## 4. Prima conversione e immagine
Con LO alto, `f_IF = f_LO - f_RF = 10,695 MHz`; immagine RF `f_IMG=f_LO+10,695 MHz=f_RF+21,390 MHz`, quindi 47,005..49,695 MHz: si evita con preselettore 25,615..28,305 MHz, la cui reiezione va dimostrata e non stimata dal numero di bande.

## 5. Primo mixer e linearita
Candidato **ADE-1+ (Mini-Circuits)**, SMT, LO +7dBm, IF compatibile con 10,695 MHz, perdita di conversione tipica circa 5dB, IIP3 tipico +15dBm. Sono valori del componente in condizioni del costruttore, non della radio assemblata. LNA +12dB e mixer IIP3+15dBm non garantiscono di per se un ingresso senza intermodulazione: per segnali forti occorrono attenuatore + bypass LNA e misure a due toni.

## 6. Trasmettitore - sola architettura
Microfono -> filtri/modulatore AM/FM/SSB e catena FI -> conversione a 26,965..27,405 MHz sui soli 40 canali ordinari -> filtro immagine -> driver/finale -> filtri armoniche -> sensore direzionale di protezione -> accordatore LC con bypass -> secondo eventuale sensore potenza all'antenna -> uscita RF 50 ohm.

La radio non e ancora in grado di trasmettere: amplificatori, alimentazione finale, filtri TX, interlock hardware, topologia modulazione e ATU sono da dimensionare. La progettazione del TX deve includere blocco fisico in presenza di sintetizzatore unlock, banda illegale, ROS alto, mancanza antenna o sovratemperatura. Nessuna trasmissione sul prototipo fuori da carico fittizio e procedure consentite.

## 7. Metriche RX da congelare con simulazioni e laboratorio
| Parametro | Target di progetto, non risultato | Metodo futuro |
|---|---|---|
| SSB sensibilita | <=0,25 uV RMS / 50 ohm, metrica da definire con riferimento standard | Generatore RF calibrato, livello e (S+N)/N o SINAD dichiarato |
| FI SSB | circa 2,4 kHz (banda effettiva) | Sweep filtro e misura BPF |
| Selettivita adiacente | >=70dB come obiettivo, metrica e offset da specificare | Generatore a due segnali |
| Blocking/intermodulazione | Target non ancora fissato | Due toni e misura IP3/reciprocal mixing |
| Rumore interno | Non mascherare stazioni deboli | Misura NF, MDS e banda audio |
| NB/ANL/DSP | Disinseribili | Confronto prima/dopo, distorsione e intelligibilita |

Per il sistema RF non considerare sufficiente un punteggio di sensibilita senza linearita, variazione con AGC e rumore di fase.

## 8. Compatibilita SMD
Mixer ADE-1+, PLL ADF4351, condensatori e filtri di controllo saranno SMT. Relay RF, trasformatori e accordatore sono ancora da scegliere; anche i componenti SMD avranno limiti di Q, potenza e tensione. La dissipazione del PA e l'eventuale contenitore storico restano vincoli da misurare.

## 9. Fonti consultate (solo link, nessuna copia del datasheet)
1. ADI ADF4351: https://www.analog.com/en/products/ADF4351.html
2. ADI ADF4351 datasheet Rev.A: https://www.analog.com/media/en/technical-documentation/data-sheets/adf4351.pdf
3. Mini-Circuits ADE-1+: https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B
4. ETSI EN300433 V2.1.1: https://www.etsi.org/deliver/etsi_en/300400_300499/300433/02.01.01_60/en_300433v020101p.pdf
5. MIMIT RED: https://www.mimit.gov.it/it/comunicazioni/radio/apparati-radio
