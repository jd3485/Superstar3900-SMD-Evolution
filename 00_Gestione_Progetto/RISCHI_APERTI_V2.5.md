# Rischi aperti - V2.5

- R1: sei filtri paralleli più commutatori potrebbero aggiungere perdita e accoppiamento non modellati: NO-GO.
- R2: i modelli indicano Q=90 nominale per ciascuna bobina, ma a 27 MHz serve scelta part number e Q/SRF certificati.
- R3: relè G6K-2F-RF perdita dichiarata a 1 GHz; non applicare il valore come specifica garantita a 27 MHz.
- R4: PE42462 può essere usato da 10 MHz, ma la perdita indicativa 0,7 dB non è stata verificata nei nostri circuiti a 27 MHz; 2 switch serie riducono il budget.
- R5: sommare in dB le attenuazioni di BPF pre-LNA e LP7 post-LNA ipotizza isolamento e matching. Il leakage può limitare la reiezione effettiva.
- R6: sicurezza dei filtri RX durante la trasmissione: percorso TX separato e controlli interbloccati non ancora disegnati.
- R7: non ci sono schema RF KiCad, ERC/DRC, PCB, VNA, NF e IM3 di prototipo: nessuna dichiarazione prestazionale.
