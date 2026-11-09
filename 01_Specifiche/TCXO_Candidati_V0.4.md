# Referenza 12,8MHz: candidati SMD

- **T200F-012.8M** (Connor-Winfield): TCXO 12,8MHz, 3,3V, LVCMOS, SMD 10 pin, stabilita pubblicata ±200ppb, Imax 6,5mA. Verificare datasheet, pinout, phase noise, gestione EN, disponibilita e prezzo PRIMA della BOM definitiva. Fonte: https://www.digikey.it/en/products/detail/connor-winfield/T200F-012-8M/10130302
- Alternativa **TVJ6F-012.8M** (Connor-Winfield), 3.3V, 4-pad SMD, ±1ppm, Imax 6mA, meno stabile, da confrontare su rumore di fase, non solo ppm: https://www.digikey.it/en/products/detail/connor-winfield/TVJ6F-012-8M/3524588

A 39MHz LO, la sola accuratezza di 200ppb corrisponde a ±7,8Hz di scostamento di frequenza LO (fLO * 0.2e-6), senza includere l'oscillatore seconda FI, deriva, aging e errori di calibrazione. **Stabilita in frequenza non equivale a basso rumore di fase.** Nessuno dei due candidati e' approvato per acquisto.
