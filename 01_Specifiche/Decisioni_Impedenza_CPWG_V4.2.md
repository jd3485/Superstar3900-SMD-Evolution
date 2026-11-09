# Specifica di qualificazione impedenza CPWG (V4.2)

**Stato: aperta, non una geometria di fabbricazione.** Percorsi RF esistenti da 0,28 mm su F.Cu non vanno etichettati 50 Ω fino alla verifica con stack-up PCBWay.

Informazioni necessarie dal produttore: numero e ordine degli strati (F.Cu/In1.Cu/In2.Cu/B.Cu), spessore dielettrico L1-In1, Dk/Er nominale e tolleranza alla frequenza d'interesse, spessore rame dopo galvanica, spessore/specifica maschera, apertura rispetto alle piste, distanze laterali GND, min. piste/spazi, tolleranze registrazione e riempimento piani. Specificare impedenza e tolleranza richieste al fabbricante.

Per verificare la singola tratta: solver CPWG con piani GND e maschera, numero via stitching e loro distanza, transizione SMA, area pad C101/C102/U101, isole causate dai piani; misure di riscontro con VNA/fixture e de-embedding ove appropriato.

La tabella microstrip isolata in `03_Verifiche/V4.2/RAPPORTO_TECNICO_V4.2.md` illustra sensibilità, NON approvazione. Conservare la V3.8 intatta finché il CAD ufficiale e il fabbricante non approvano le alternative.
