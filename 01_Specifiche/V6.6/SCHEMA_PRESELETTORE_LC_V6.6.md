# V6.6 — Preselettore F501: rete RLC 50Ω candidata, **NO TX / NO FAB**

## Schema elettrico discreto (riferimenti non precedentemente assegnati)

```text
J601 RF_IN_50R → L601 2.0µH → RF_PRE_A → [C601 16pF || C602 1.5pF] → RF_PRE_MID
                                                      |
                            L602 22nH || [C603 1500pF || C604 91pF] → GND_RF
                                                      |
RF_PRE_MID → L603 2.0µH → RF_PRE_B → [C605 16pF || C606 1.5pF] → J602 RF_OUT_50R
```

Tutte le porte sono assunte a **50 Ω reali**. La terminazione 50 Ω si trova nella sorgente e nel mixer/carico: **non installare in aggiunta un resistore 50 Ω in parallelo al segnale**, che caricherebbe impropriamente le porte. I pin di schermatura dei connettori vanno in GND_RF. Lo studio numerico include anche una capacità parassita **C_FEED** dall'ingresso all'uscita che NON va montata: è il modello dell'accoppiamento di PCB/pacchetto, da ridurre.

## Origine dei valori e natura del progetto

Da prototipo passa-basso Butterworth g=[1,2,1] a f1=25MHz, f2=29MHz, Z0=50Ω, f0=sqrt(f1·f2)=26,925824MHz, BW=4MHz. La trasformazione passa-banda fornisce **Lserie=1,98944µH, Cserie=17,5619pF, Lshunt=21,9524nH, Cshunt=1591,55pF**. Quantizzazione candidata: **2.0µH / 17.5pF** per ciascun risonatore serie, **22nH || 1591pF** sul ramo shunt, con capacità realizzate tramite due C0G paralleli.

Non è una scelta di MPN qualificati. In particolare **2µH a ~27 MHz è problematico** per frequenza di autorisonanza (SRF), resistenze serie, dimensione, accoppiamento magnetico. Nessun produttore/part-number di L601/L603 è ancora approvato, né è noto il Q reale o il suo valore all'immagine a 47–50MHz. La topologia resta **CANDIDATO DI STUDIO**, non `PASS_PRODUCTION`.

## Calcolo 50Ω con parassiti e Q ipotizzati

- Q induttori=60 a f0, Q capacitori=400 a f0; **ipotesi**, non misure.
- SRF L601/L603=90MHz e L602=350MHz: **ipotesi**, non caratteristiche acquistabili confermate.
- C_FEED tipica di modello = 0,05pF; stress 0–1pF; **non fisicamente misurata**.
- Rserie inductor 2µH ~5,639Ω ciascuna, Rserie di L602 ~0,062Ω, ESR equivalente capacitativo 17,5pF ~0,844Ω.
- Risultato scenario nominale: perdita RX 3.31–5.59 dB, attenuazione immagine >= 52.83 dB, reiezione immagine relativa >= 47.96 dB, **return loss RX peggiore 6.18 dB**.
- Non raggiunge una soglia di riferimento di RL >= 10dB su tutti i 270 canali; la perdita RX è alta per un front-end sensibile.

**Non confondere le cifre con i 53,46dB del Butterworth ideale V6.5**: quella era una diversa funzione matematica priva di Q/ESR/SRF e feedthrough.

## Requisiti layout/integrazione

1. Disporre L601 e L603 lontani, preferibilmente con assi magnetici disallineati, schermature RF e via GND; senza stima EM non si attribuisce un C_FEED specifico al layout.
2. Separare ingresso/uscita con piano di massa, nessun ritorno condiviso lungo, piccole maglie e connessioni VNA 50Ω; evitare passaggi di RF sotto i risonatori e accoppiamenti ravvicinati.
3. Non assumere Q nominale da un generico SMD: trovare MPN/vendor S-parameters o misurare ciascun L con VNA almeno a 25–60MHz, e preferibilmente fino alla SRF; misurare capacità e loro ESL.
4. Verificare la posizione rispetto al LNA ADL5535 storico: un preselettore **dopo** il LNA non elimina il rischio di sovraccarico del LNA da blocker di immagine.
5. I file CSV sono una **netlist funzionale**, non un schematico KiCad verificato. `ngspice non eseguito`: il file `.cir` è stato generato per il successivo confronto; il simulatore Python a matrice Y/S è stato **effettivamente eseguito**.

**Sicurezza**: nessun enable RF TX; NO TX; NO FAB; interblocco della V6.2 invariato; nessun Gerber rilasciato.
