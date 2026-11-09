# Piano di collaudo V3.1 (banco RF esclusivamente ricezione)

**Stato:** PROPOSTA DI PROVA, NON ESEGUITA.

## Collegamenti

- Sezione LNA: J101 (RFIN) -> C101 -> U101 pin1 -> U101 pin3 (RFOUT e bias) -> C102 -> J102 (RFOUT).
- Bias: 5,0 V stabilizzati e limitati in corrente su J105; choke 470 nH da 5 V a U101 pin3; bypass 68 pF, 1,2 nF, 1 uF a massa. Il pad termico e il pin2 U101 sono massa.
- Attenuatore: J103 -> 150 Ω a GND -> 37,4 Ω serie -> 150 Ω a GND -> J104. Esso **non** è automaticamente commutato.
- Confronti da effettuare con brevi cavi SMA 50 Ω: preselettore V2.9 isolato; LNA J101-J102 isolato; pad J103-J104 isolato; preselettore -> LNA -> pad. Per bypass usare il cavo direttamente tra le porte esterne (non ponticellare la scheda alimentata).

## Sicurezza

- NON collegare il modulo all'antenna di una radio che possa trasmettere e NON collegarlo al finale TX. E' una scheda di studio RX senza circuito di isolamento TX e senza protezione d'ingresso approvata.
- Prima dell'alimentazione verificare la continuità GND e l'assenza di cortocircuito tra +5 V e GND. Alimentare prima con sorgente limitata in corrente, partendo con 0 V e salendo a 5,0 V.
- U101 assorbe circa 97 mA tipici secondo Analog Devices; impostare un limite adatto al prototipo e verificare assorbimento, temperatura e dissipazione.
- Segnali del generatore RF inizialmente deboli (es. -50 dBm, poi variare), in 50 Ω. Mai applicare potenza TX.

## Procedura VNA

1. Calibrazione SOLT sulle estremità dei cavi di test, 50 Ω. Annotare data, strumento e versione calibrazione.
2. Misurare J103/J104 pad: S11 e S21 da 1 a 100 MHz, particolarmente a 25,615 / 27,205 / 28,305 MHz. Risultato analitico ideale nominale S21=-6.013 dB; ritorno S11=-67.04 dB. Il PCB reale avrà parassiti non modellati.
3. Misurare preselettore V2.9, da 1 a 80 MHz, per individuare interferenze HF sotto 25 MHz e la reiezione tra 47,005 e 49,695 MHz.
4. Misurare LNA con alimentatore e bias protetti; S21/S11/S22 20-60 MHz. Non applicare segnale eccessivo.
5. Misurare cascata filtrata con e senza pad, normalizzando le perdite di cavi/connettori.
6. Misurare rumore con analizzatore di figura di rumore o sorgente ENR calibrata; il solo VNA non misura NF.
7. Due toni di basso livello (es. 26,985 MHz e 27,005 MHz), analizzatore di spettro e attenuatori di sicurezza; calcolare IM3/IIP3 senza superare compressione.
8. Test di interferenza con ingresso HF da 1-25 MHz, con attenzione al sovraccarico anche se il filtro immagine rispetta la specifica.

## Accettazione (soglie preliminari, non verifiche superate)

- Pad: 6,0 dB ± 0,3 dB a 27 MHz, ritorno ingresso > 20 dB.
- LNA: controllare allineamento a dati ADI (20 MHz/70 MHz); niente valori garantiti a 27 MHz senza misura.
- Corrente / temperatura: entro limiti dei datasheet e dei componenti scelti.
- Preselettore: rivalutare l'obiettivo ≤ 1,5 dB di perdita RX e ≥ 60 dB di reiezione immagine, attualmente non raggiunti insieme dalla V2.9.

## Bloccanti produzione

- Scelta e verifica footprint SMA e J105, maschera fori/ingombri meccanici, footprint U101 e induttore L101.
- ERC, DRC e netlist nativi KiCad; verifica trasmission-line su stack-up PCBWay reale.
- Isolamento TX/RX, protezione ESD/sovratensione e controllo alimentazioni: NON progettati qui.
- File Gerber, posizionamento e distinta PCBWay **non approvati**.
