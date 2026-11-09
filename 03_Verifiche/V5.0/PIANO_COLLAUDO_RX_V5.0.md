# Piano di collaudo del solo modulo RX 50 Ω — V5.0 (NON ANCORA ESEGUITO)

**Obiettivo:** isolare gli esperimenti su ADL5535 (J101→J102) e attenuatore passivo (J103→J104). Non è un ricevitore completo e non contiene una catena TX. Nessuna connessione a un'antenna trasmittente.

## Prima di alimentare

1. Dopo fabbricazione **autorizzata** e controllo ottico, verificare polarità, GND, saldature, assenza di corti e continuità 50 Ω nominale degli ingressi/uscite. La sola DRC non sostituisce ispezione o test elettrico.
2. Alimentatore limitato in corrente, inizialmente disattivato, massa comune, collegamento dedicato `+5V_BENCH`; confermare la corrente massima consentita da BOM e strumentazione prima di impostare un limite. ADI riporta 97 mA tipici a 5 V, **non** un criterio automatico di accettazione né la massima corrente.
3. Termina sempre le porte RF inutilizzate a 50 Ω. Evita segnali esterni non controllati. Nessuna prova RF senza misuratore idoneo, schermatura e attenuatori/protezioni adeguati.

## Sequenza consigliata, tutta DA ESEGUIRE

| ID | Misura | Strumenti e metodo | Criterio da fissare PRIMA della prova |
|---|---|---|---|
| RX-B01 | Isolamento e assenza corti | Multimetro, alimentazione disabilitata | Resistenze/prelievi secondo schema approvato |
| RX-B02 | Corrente a 5 V, avvio | Alimentatore limitato + amperometro | Intervallo compatibile con datasheet e BOM approvati |
| RX-B03 | Stabilità e temperatura U101 | Termocoppia o termocamera emissività tarata, regime | Temperatura pad/custodia e stima TJ approvate |
| RX-B04 | Attenuatore J103→J104 | VNA 2 porte 50 Ω, misura S21/S11/S22 | −6,013 dB **ideali** come riferimento; tolleranze da definire |
| RX-B05 | ADL5535 J101→J102 | VNA a basso livello, misura S11/S21/S22 | Limiti derivati da datasheet alle frequenze effettive |
| RX-B06 | Banda CB ricevibile | Sweep 25,615–28,305 MHz e punti di misura ripetibili | Tolleranze guadagno/adattamento definite dopo baseline |
| RX-B07 | Variazione termica | Ripetizione S-parameter a temperatura stabilizzata | Drift massimo approvato dopo prova iniziale |
| RX-B08 | Ripetibilità | Almeno 3 cicli alimentazione e sweep | Valori da fissare su campioni fisici |

**Nota tecnica:** ADL5535 è specificato per 20 MHz–1 GHz; operare attorno a 27 MHz è vicino al limite inferiore e **non** garantisce che le prestazioni tipiche riportate a 190/380 MHz valgano in banda CB. Misurare il circuito reale e non extrapolare automaticamente. Fonte ADI: https://www.analog.com/en/products/adl5535.html.

**Stato al rilascio V5.0:** tutti i test RX-B01…B08 `NOT_RUN`; nessun dato numerico RF/termico reale disponibile. Nessun prototipo assemblato.
