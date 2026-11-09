# V3.1 - registro decisioni

- **Decisione**: prova separata a 50 Ω della sezione LNA ADL5535 e attenuatore π. Preselettore resta nella versione V2.9, con collegamento SMA esterno per confronti.
- **Dati controllati**: datasheet ADL5535 Rev A, figura 16 e 25, pagina 11 e 14; pin1 RF IN, pin2 e pad GND, pin3 RFOUT/VCC; choke 470 nH, C1=C2 100 nF, bypass 68 pF, 1,2 nF, 1 µF.
- **Pad**: π 50 Ω, 6 dB nominali, resistenze commerciali 150 Ω / 37,4 Ω / 150 Ω; calcolo ABCD e stress ±1% in `03_Verifiche/V3.1`.
- **Alternativa di studio**: bypass LNA tramite collegamento SMA esterno, NON attraverso un relè sulla PCB V3.1. In una futura revisione aggiungere commutazione dopo prove di perdita/isolamento.
- **Sicurezza**: esclusivamente misura RX e a bassa potenza. Non collegare apparato TX e nessuna alimentazione a 13,8 V.
- **Stato del progetto totale**: avanzamento stimato 36% per sviluppo documentale e prototipo testabile **solo come bozza**. Non confondere con percentuale di hardware validato.
- **Vietato dichiarare approvato**: ERC, DRC, SPICE nativo, fabbricazione, misure RF, sicurezza TX/RX, filtraggio antenna/duplex, EMI/EMC.
- **Fonte ufficiale**: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf ; https://www.minicircuits.com/WebStore/dashboardPdf?model=ADE-1%2B
