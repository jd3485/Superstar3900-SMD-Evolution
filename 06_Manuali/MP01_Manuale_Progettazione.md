# MP-01 — Manuale di progettazione

**Stato: struttura, da compilare con dati tecnici verificabili.**

1. Requisiti, priorità, criteri pass/fail e vincoli legali.
2. Analisi radio Superstar 3900 storica, versioni e ipotesi adottate.
3. Architetture alternative considerate e motivi della selezione.
4. Budget di rumore, sensibilità, dinamica, IP3, selettività, blocking e spurie.
5. Analisi sintetizzatore PLL, VCO, stabilità e rumore di fase.
6. Filtri RF/FI e adattamento: simulazioni S-parametri e tolleranze.
7. Catena TX: linearità, modulazioni, potenza, termica e filtri armoniche.
8. Microcontrollore, tabelle canali, firmware, protezioni e interfaccia.
9. Wattmetro, accoppiatore direzionale, SWR, modulometro e taratura.
10. Accordatore LC: topologia, componenti, gestione carico e sicurezza.
11. Alimentazione e EMC/EMI, stackup e layout con ritorni di corrente.
12. Modelli e simulazioni: versioni software, parametri, grafici, risultati.
13. Tolleranze, corner analysis, FMEA essenziale e modifiche progettuali.
14. Lista limitazioni e prove di accettazione da eseguire sul prototipo.


---

# Capitolo effettivo aggiunto in V0.2: strategia di sintesi e ricezione

**Le specifiche sono ancora modificabili.** La scelta di una FI a 10,695MHz consentirebbe di conservare lo spirito della supereterodina storica, senza copiarne ciecamente ogni componente. Con iniezione alta del primo LO, il filtro immagine vede segnali fuori di oltre 21MHz dalla banda utile (47,005..49,695MHz). L'intero intervallo utile di 2,69MHz puo essere diviso in sei preselettori commutati secondo banda selezionata. Restano da determinare guadagno, Q, inserzione e reiezione effettiva.

La formula della sintesi LO, con `IF=10.695.000`, e `LO = RF+IF`. Un ADF4351 con un TCXO da 12,8MHz diviso per R20 produce fPFD=640kHz. Il VCO fondamentale viene confrontato nella PLL (feedback fondamentale), e l'uscita viene divisa per 64. Si ottiene `LO = (N * 640000) / 64 = 10000*N`. Dato che il piano canali richiede frequenze LO sulla griglia 10kHz, con N intero da 3631 a 3900 si rappresentano tutte le 270 posizioni senza FRAC.

La ricerca di sensibilita non significa amplificare indiscriminatamente: si potra usare un attenuatore in ingresso e bypassare l'LNA in zone con forte campo RF; un mixer ADE-1+ SMT richiede +7dBm LO, quindi occorre prevedere la catena di buffering. Per il progetto reale conteranno anche il rumore di fase, il filtro a quarzi della FI, la linearita e la schermatura.

Calcoli, fonti, risultati e limitazioni si trovano in `01_Specifiche/Architettura_RF_V0.2.md` e `03_Verifiche/Calcoli_Fase_1_V0.2.md`. La prima ipotesi Friis fornisce NF circa 4,85dB, ma e solo una stima termica con parametri ipotizzati. In assenza di circuito e misure nessun numero di prestazione e garantito.

## V0.4 - Capitolo 2b: filtro d'anello e buffer LO
Consulta `01_Specifiche/PLL_Loop_Filter_V0.4.md` per lo schema nodale, formula Z_vtune e modello L(s); `01_Specifiche/Buffer_LO_V0.4.md` per le scelte del buffer. Sono candidati non ancora ingegnerizzati nel CAD; per numeri verificati apri `03_Verifiche/Report_PLL_Loop_V0.4.json`. Nessuna affermazione di fase noise dBc/Hz assoluta.

## Revisione V0.5 - selezione PLL (preliminare)

È disponibile lo studio `01_Specifiche/Confronto_Sintetizzatori_V0.5.md`. Il LMX2572 diventa candidato privilegiato in virtu' del confronto del rumore bianco normalizzato in banda (15,01 dB teorici sulla sola componente, non risultato globale). Fase successiva: modello di rumore completo, scelta filtro d'anello LMX, verifica TCXO e schema CAD.

## Calcoli e dimensionamento LMX2572 - V0.6
Vedere `01_Specifiche/Filtro_Anello_LMX2572_V0.6.md` per legge Y(s), modello open-loop e 4.000 prove di sensibilita ipotetiche. Verifica dati Kvco TI/PLL timing e fase noise con strumento TI prima di consolidare i componenti. Confine VCO3/VCO4 a circa 4.650GHz.


## Capitolo V0.8 - Alimentazioni locali LMX2572
6 ingressi Vcc separati, ciascuno con resistor link 0R per misure e 1uF verso GND.
7 nodi bias/regolatore ciascuno con capacita ripresa da TI EVM. NON portare alimentazione
esterna ai nodi Vref/Vbias. Differenziare alimentazione 3.3 V non ancora realizzata e
lo stadio di bypass. Schemi generati ma ERC e distinte non qualificati.

## V0.9 - isolamento dell'alimentazione riferimento
Due LDO 3.3V separati sul +5V protetto (da creare) rendono indipendenti a bassa frequenza il PLL e il TCXO. Questa scelta non garantisce da sola alcun miglioramento del rumore di fase; serve misurare lo spettro LO. TPS7A20 ha PSRR e noise specificati dal produttore, da valutare alle frequenze effettive e al carico.


## Aggiornamento V1.1 - calcolo UVLO/OVP e limiti
Per tre resistori in cascata R1,R2,R3 da IN a RTN, OVP al nodo R3 e UVLO al nodo R2+R3, Vuv = 1.19*(R1+R2+R3)/(R2+R3), Vov = 1.19*(R1+R2+R3)/R3. R1=365k, R2=16.2k, R3=30.1k sono candidati. Non sostituire un calcolo statico con una simulazione di transitorio reale.


## V1.2 - selezione cautelativa protezioni
F200 1.5A Nano2 451 candidato. Package reale circa 6.10x2.69mm; precedente footprint 1206 non idoneo, corretto con segnaposto non validato. D200 SMBJ18CA bidirezionale solo candidato DNP, non confondere tensione di standoff 18 V con soglia OVP. Verificare IEC surge, inrush, SCCR e coordinamento prima del montaggio.

## V1.4 - Decisione gerarchia e tracciabilita
E stato inserito sul foglio root un simbolo a due pin J100 per documentare la rete ausiliaria a 13,8 V. Il footprint e intenzionalmente vuoto: la scelta del dispositivo fisico richiede specifica di corrente e vincoli meccanici, evitando una fabbricazione prematura. L'analisi geometrica indipendente conta 4 schemi, 3 fogli figli e 6 separazioni di wire nel PLL; non effettua regole elettriche KiCad, calcolo della dissipazione o verifica transitoria. Conservare l'ERC nativo e il controllo datasheet TCXO fra i gate della prossima revisione.


## Aggiornamento V1.5
Protocollo SPI LMX2572 §7.5 TI: implementazione test 24 bit MSB-first, da espandere con profilo validato e mappa registri.


## V1.5.1 - Piano progettuale audio e controllo
Sottoblocchi futuri: front-end microfono anti-rientro, ADC/DAC e DSP opzionale, detector VOX, memoria Echo, generatore Roger Beep, filtri separati subaudio e decoder CTCSS/DCS FM, scheduler Dual Watch sincronizzato con lock PLL. Specifiche e verifiche in `01_Specifiche/Funzioni_Aggiunte_V1.5.1.md`. Nessun circuito dimensionato in questa revisione.

## V1.6 - Trattamento digitale AF

Base 48 ksps, 16 bit; 10 ms = 480 campioni stereo. Doppio buffer DMA RX+TX: 7680 byte. Echo a 250 ms/mono/16 bit: 24 KB. Riconoscimento dimostrativo 50 CTCSS su 800 ms di dati sintetici a 8 ksps, separato dalla catena analogica e dal DCS. Vedere report V1.6 e test software.


## Aggiornamento V2.3 - Analisi NF e linearita' dei primi stadi
Sono confrontate sette catene RF modello. Perdite davanti all'LNA aumentano direttamente la figura di rumore; separarle puo' migliorare NF ma espone l'amplificatore a bloccanti/immmagini che sarebbero stati soppressi dal filtro precedente. Il pad dopo l'amplificatore migliora IIP3 riferita all'antenna limitando il mixer, ma non evita l'overload dell'LNA. I dati numerici sono riproducibili con `03_Verifiche/V2.3/rx_cascade_v23.py`. Si richiedono S11/S21, NF, IIP3, P1dB, purezza LO e misure reali.

## Nota tecnica V2.4 - Preselettore di studio
Descrizione e risultati: `01_Specifiche/Preselettore_Bassa_Perdita_V2.4.md`. Nessun filtro approvato e nessuno schema elettrico definitivo.
