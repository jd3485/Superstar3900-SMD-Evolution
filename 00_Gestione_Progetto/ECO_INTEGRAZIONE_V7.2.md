# ECO V7.2 — sorgente IF2 offline inibita

1. V7.2 aggiunge `duc_if2_offline_v72.py`: AM, FM, USB, LSB e CW su audio 48kHz, DUC 80× a IF2 455kHz (3.84Msps). Non modifica sorgenti V7.1; nessun firmware STM32 o DAC viene scritto/programmaticamente utilizzato.
2. V7.1 propone U7201/U7202 e F7201/F7202 **DNP**, ponti R7201–R7205 **DNP**. V7.2 aggiunge DAC U7301, IF2 F7301 e connettori/ponticelli tutti **DNP**: non collegare IF2 al mixer U7201 e non collegare RF ad alcun PA/antenna.
3. Contratto Hilbert di quadratura solo blocchi periodici, **NON** pronto per streaming audio: sideband USB RF corrisponde a IF2 inferiore, LSB RF alla superiore; FM deviazione IF2 negativa.
4. Modello filtri F7201/F7202 esclusivamente **Butterworth matematico**: livelli di reiezione non costituiscono prestazioni fisiche o criteri di fabbricazione. F7301 richiesto per eliminare immagini DAC, **non ancora selezionato**.
5. Estendere verifica V7.2 includendo regression suite V7.1, mappatura 270 canali, 128 combinazioni logiche fail-closed, risultati spettrali multi-tono e BOM/netlist DNP. Riportare gli esiti reali della CI solo dopo verifica del log.
6. Vincoli precedenti immutati: IF analogica 455k e LO2 RX V7.0 non qualificati, interblocchi V6.2 incompleti, no catena PA, nessun KiCad nativo, ERC/DRC, EMC/hardware. **NO FAB / NO TX.**
