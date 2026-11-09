# Fonti tecniche e limiti V2.9

- Coilcraft 0805CS datasheet: https://www.coilcraft.com/en-us/files/datasheet/0805CS
- Coilcraft SPICE model Document 158 (Rev. 2025-01-16): https://www.coilcraft.com/getmedia/c86a99da-e310-4932-bb03-09af08346f8a/spice_0805cs.pdf
- Murata C0G GRM188, catalogo: https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/static-model/component-list-s-mlcc-2506.ashx
- KEMET C0G MLCC: https://content.kemet.com/datasheets/KEM_C1003_C0G_SMD.pdf

Il modello Coilcraft e' ottenuto da misura tipica de-embedded, non garantisce Q minimo a 27 MHz, non include pad, piste, piano di massa, accoppiamenti tra bobine, box, connettori, schermature e degradazioni reali. La perdita del condensatore C0G e' rappresentata da tan(delta)=0.001 IPOTETICO, non certificato per un prodotto specifico. 

Il circuito sperimentale esclude ESD, protezione TX/RX, limitatori RF e uno switch reale; non collegarlo direttamente a un finale TX o all'antenna di trasmissione. Il filtro HP3 compare esclusivamente nello studio numerico, non nel foglio sperimentale a 9 componenti.
