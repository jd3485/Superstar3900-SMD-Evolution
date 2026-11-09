# Requisiti V1.5.1 - VOX, Dual Watch, Roger Beep, Echo, CTCSS e DCS

Stato: **ACCETTATI COME REQUISITI; NON IMPLEMENTATI NELL'HARDWARE**.
Revisione requisiti del Superstar 3900 SMD Evolution, 2026-11-07.

## Requisiti funzionali

| ID | Funzione | Comportamento previsto | Esclusioni/priorita' |
|---|---|---|---|
| FR-VOX-01 | VOX | Attivazione RF a voce; soglia e ritardo di rilascio (hang time) regolabili; indicatore VOX; controllo PTT sempre possibile | Non puo' superare protezioni, blocco TX canali, PA, PLL unlock; no auto-TX da altoparlante, anti-rientro acustico |
| FR-DW-01 | Dual Watch | Ascolto alternato A/B con ricevitore singolo, memorizzazione canale secondario, pausa su segnale valido e ripresa a fine traffico | RX non realmente simultanea; in PA/CH9 si sospende; in TX si sospende; la TX resta sul canale primario A (non scatta automaticamente sul B) |
| FR-RB-01 | Roger Beep | Segnale breve e regolabile in abilitazione al rilascio PTT/VOX, prima della disattivazione RF | Disabilitato in PA, CH9 e quando la TX e' bloccata; durata e ampiezza da qualificare |
| FR-ECHO-01 | Echo voce | Effetto audio di ritardo/feedback controllato, con comando ON/OFF e intensita' | Solo catena microfonica TX voce AM/FM/SSB; bypass completo, limiter/modulazione e pulizia audio prioritari; OFF su CH9/PA (PA separata) |
| FR-CTC-01 | CTCSS | FM: 50 toni selezionabili, codifica TX e decodifica RX indipendenti, OFF per default; impostazione per canale/memoria | Non si applica a AM/SSB/CW/PA; CH9 bypass RX subtoni; non e' cifratura/riservatezza |
| FR-DCS-01 | DCS | FM: obiettivo 104 codici normali/invertiti N/I, encode TX e decode RX, OFF di default; selezione per memoria | Alternativo a CTCSS sullo stesso canale; valori/polarita' e framing da verificare con tabelle/strumenti |
| FR-UI-01 | Comandi | Preferenza per comandi fisici dedicati VOX, DW, RB, ECHO; impostazione dettagli toni/code via display encoder o menu di servizio | Configurazione pannello meccanico non finalizzata |

## Catena elettronica preliminare

- **Microfono -> preamplificatore a basso rumore -> filtro anti-aliasing -> codec ADC/DAC o DSP audio -> limitazione/modulatore TX** per VOX, Echo, Roger Beep, codifica subtoni.
- **Discriminatore FM -> ramo subaudio dedicato -> decodifica CTCSS/DCS -> logica di apertura squelch**. Il filtraggio subaudio deve evitare che i toni/code si sentano in altoparlante.
- Bypass analogico della voce e separazione dalla logica digitalizzata dove tecnicamente utile. Il percorso audio non e' ancora dimensionato.
- **Dual Watch**: firmware per commutazione rapida del sintetizzatore e aggancio PLL. Tempi di dwell/ripresa da ricavare da tempo reale di lock, squelch e code detection.
- **VOX**: rilevatore inviluppo/energia con soglia, attacco, hysteresis, hang-time, filtro antirumore e prevenzione feedback microfono-altoparlante.
- Le funzioni TX restano subordinate all'interblocco legale/di sicurezza definito nelle revisioni precedenti; TX sui 270 canali non prevista.

## Comportamenti di precedenza da convalidare

1. Protezione/PLL-unlock/TX-non-consentita impedisce qualsiasi TX anche con PTT, VOX o Roger Beep.
2. PA disabilita RF TX e interrompe Dual Watch. PTT/VOX puo' eventualmente attivare solo audio PA; funzione da sviluppare.
3. CH9 forza 27,065 MHz AM, disattiva Dual Watch, bypass dei subtoni e disabilita Echo/Roger Beep; ripristina le impostazioni precedenti quando disattivato.
4. Dual Watch non comporta trasmissione automatica sul canale secondario; PTT/VOX, ove consentiti, hanno sempre come target il primario.
5. Codifica/decodifica CTCSS e DCS utilizzate solo in FM; NON garantiscono riservatezza.

## Verifiche di accettazione ancora da fare

- VOX: minimi falsi inneschi con AF ricevuto, rumore cabina e feedback acustico; prova a diversi livelli e tempi.
- DW: aggancio PLL, sensibilita', tempo morto di scansione, priorita' audio e ritardo di apertura squelch.
- RB/Echo: deviazione FM, profondita' di modulazione AM, linearita' SSB, clipping, durata e spettro del beep.
- CTCSS: deviazione subaudio, frequenza e tolleranza, detection rate con rumore e interferenze.
- DCS: codici N/I, bit stream, falsa apertura squelch e compatibilita' con apparati di riferimento.
- EMC, alimentazione DSP/codec, interazione clock digitali e ricevitore a basso rumore; prove a TX su carico fittizio.

## Limiti normativi

- Trasmissione solo dove autorizzata e in modalita' ammesse dal profilo paese/conformita'; nessuna estensione TX implicita.
- CW TX resta bloccata salvo specifica verifica e autorizzazione.
- CTCSS/DCS non creano altri canali e non rendono private le comunicazioni.

## Riferimenti tecnici consultati (schede e manuali, non uno schema verificato del progetto)

- Cobra, Dual Watch (ricerca alternata): https://support.cobra.com/support/solutions/articles/47001193576-cb-radio-operation-programming-dual-watch-model-75-wx-st-
- Team Expert 1 CB, RX/TX CTCSS/DCS e DW: https://cbradio.nl/team/downloads/Manual_Team_Expert_1_ENG_DE.pdf
- Alinco DR-138/438, CTCSS/DCS encoder/decoder: https://www.alinco.com/pdffiles/Instruction/Business/DR-138_438_manual.pdf
- Cobra, codici non privati: https://support.cobra.com/support/solutions/articles/47001193822-what-is-ctcss-and-dcs-
- CEPT ECC/DEC/(11)03 banda CB: https://docdb.cept.org/download/1540

**Nessuna nuova parte hardware, KiCad, firmware RF, test in laboratorio o PCB e' stata dichiarata completata in questa revisione.**
