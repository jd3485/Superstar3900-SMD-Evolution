# Fonti primarie e note di interpretazione (V2.7)

- Coilcraft 0805CS, documento tecnico 100-1 / 100-2: https://www.coilcraft.com/getmedia/dd5f20e4-1ff7-43df-8317-b693eb2dce3e/0805cs.pdf
- Murata, serie alta Q C0G/NP0, famiglia da ricontrollare per ogni MPN: https://www.murata.com/en-us/products/capacitor/ceramiccapacitor/overview/lineup/low-esl
- Esempio verificato per dielettrico RF (NON valore utilizzato dal filtro): GJM1555C1H220GB01D, 22pF 0402 ±2%, fonte distributore: https://www.digikey.com/en/products/detail/murata-electronics/GJM1555C1H220GB01D/7363125

**Attenzione:** il Q minimo Coilcraft di 560 nH e' 23 misurato a 50 MHz; il dato non determina Q a 27 MHz.
I condensatori C0G/NP0 82/91/150/160/180/270/300 pF NON hanno ancora un MPN specifico selezionato, pertanto non si puo' usarli come BOM di acquisto.
Stato dei parametri di simulazione: Q e tan_delta ipotetici, non estratti da S-parameters misurati.
