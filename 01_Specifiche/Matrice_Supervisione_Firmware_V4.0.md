# Specifica di supervisione logica V4.0 - DRAFT / no RF

**Scopo:** trasformare requisiti V1.5.1 in comportamento logico ripetibile. File modello: `08_Firmware_Prototipi/radio_supervisor_v40.py`.

## Ordine di precedenza (solo modellazione)
1. Input non valido: `tx_request=False`, indipendentemente da CH9.
2. Configurazione CTCSS/DCS incoerente sul medesimo ramo: blocco TX (policy conservativa provvisoria).
3. PA: solo percorso audio separato; RF e Dual Watch disabilitati.
4. CH9: RX 27,065 MHz AM, no DW, Echo, Roger Beep o subtoni; TX ancora subordinata a tutti i guard.
5. Dual Watch A/B: selezione B solo RX in assenza di richiesta PTT/VOX; TX vincolata alla selezione primaria A.
6. TX logica da PTT o VOX abilitato con `vox_gate` attivo, solo per banda D non-ALFA o CH9, AM/FM/USB/LSB; CW TX vietata.
7. Otto guard indipendenti, tutti `True` per la sola richiesta logica TX: profilo-paese approvato, PLL locked, consenso HW dedicato, alimentazione, temperatura, ROS, relè antenna e ATU libera.

## Importantissimo
`tx_request=True` **non significa trasmissione consentita dalla legge né RF attiva**: è un output di un modello puro. Mancano circuiti, timer, watchdog, logica real-time, autodiagnosi, architettura fail-safe, conformità RED e test di laboratorio. I default false non sono una certificazione. Il porting su MCU deve introdurre interblocchi hardware indipendenti, debounce, lock del PLL, antirimbalzo, gestione fail latch e timeout.

## Assunzioni da confermare
- CW solo RX; profilo TX italiano va ricontrollato e approvato da test di conformità e requisiti normativi applicabili.
- Priorità PA superiore a CH9; riattivando CH9 dopo PA si ripristinano le selezioni fisiche.
- Con DW=ON il flag `dw_slot` è un dato di scheduler esterno; non sono stimati tempi lock PLL / dwell / hang.
- In caso di conflitto CTCSS e DCS il modello blocca la TX (policy conservativa di verifica, non interfaccia utente definitiva).
- Il VOX usa un input `vox_gate` già filtrato; nessun algoritmo audio in questa revisione.

## Accettazione reale ancora aperta
- Codice C embedded, temporizzazioni e feedback hardware;
- simulazione guasti hardwired, test EMC/RED e verifica profilo TX;
- misure e verifiche modulo RX + board footprint native KiCad.

### Matrice sintetica
| Condizione | RX | TX logica | Funzioni sospese |
|---|---|---|---|
| PA attiva | audio PA | sempre OFF | RF, DW, Echo, RB, subtoni |
| CH9 attivo | 27,065 AM | solo se guard e PTT/VOX | DW, Echo, RB, CTCSS/DCS |
| DW su B | B soltanto RX | sempre primario A | scan sospesa durante TX |
| CW | CW in RX | OFF | RB, Echo, subtoni |
| Guard mancante | RX ordinaria | OFF | segnalazione protezione |
| Config CTCSS/DCS in conflitto | frequenza primaria | OFF | subtoni |

Il modello e' solo simulazione, non un circuito pronto alla fabbricazione.
