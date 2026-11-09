# Esito della revisione V4.0

**V4.0: avanzamento documentale e della specifica firmware, non hardware.**

- Creato supervisore puro Python separato da firmware embedded e DRC; guard tutti False per default.
- Test esaustivo sulle combinazioni di banda, canale, ALFA, modo; prove di priorita' CH9/PA/DW e fault injection.
- Redatto MU-01 illustrato in PDF e Markdown con tabella automatica delle 270 posizioni RX.
- Verificata disponibilita' della pagina ufficiale TE del connettore SMA; file CAD 2D/3D indicati sul sito, non scaricati in questo ambiente e non inseriti nel pacchetto (documentazione proprietaria).
- **Non** eseguiti: KiCad nativo ERC/DRC, refill zone, footprint approval, test termico, VNA/RF, PCBWay ordine o collaudi hardware.
- La matrice di priorita' e' una implementazione di riferimento rivedibile, NON codice di controllo trasmissione reale.

## Bloccanti all'hardware
1. Footprint SMA TE DXF/STEP e confronto quote custom V3.8;
2. pad termico ADL5535, pasta e dissipazione;
3. KiCad 9/10 con refill, DRC e ERC su schematico nativo effettivo;
4. Stack-up controllato per 50 ohm e prove VNA prima di fabbricazione.

Il rilascio rimane NO FAB / NO PCBWAY.
