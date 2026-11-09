# Registro verifiche V2.3

ESEGUITO CON ESITO POSITIVO (software locale):
- 13 test unitari del modello di rumore, guadagni e IIP3: `python 03_Verifiche/V2.3/test_rx_cascade_v23.py`.
- 6 suite storiche: `python 03_Verifiche/run_all_tests.py`.
- CSV e JSON confronti nominali e perturbazioni illustrate: `python 03_Verifiche/V2.3/rx_cascade_v23.py`.
- Archivio ZIP verificato con test integrità, manifest esterno SHA256.

LIMITI DELLA VERIFICA:
- Non eseguite simulazioni SPICE dei filtri e del mixer, né modelli elettromagnetici di layout.
- Nessun S11, S21, NF, IIP3 o P1dB misurato su hardware; nessuna validazione RF a 27 MHz.
- Nessun ERC/DRC KiCad nativo; installazione software non disponibile in questo ambiente.
- I parametri 1,5 dB prefilter / 3,0 dB postfilter sono obiettivi ipotetici, non risultati validati.
- La reiezione di immagine V2.2 (69 dB nel precedente modello) NON è applicabile alla topologia divisa.
- Lo script di Monte Carlo è studio di sensitività ai parametri ipotizzati, NON rendimento industriale.

BLOCCANTI PRODUZIONE: completamento schema e PCB, librerie componenti, filtro RF reale, alimentazione completa, SPI e firmware, modelli RF e collaudi, percorso trasmittente, accordatore, strumenti, normativa.
