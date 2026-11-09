# Superstar 3900 SMD Evolution — V4.4 cumulativa (2026-11-08)

**Stato: 37% stimato di documentazione/progettazione; zero moduli hardware collaudati. NO FAB / NO PCBWAY / NO TX.**

## Novità V4.4

- Generato **schema sperimentale RX V4.4** con 15 simboli, 31 pin, 8 reti, i valori e i footprint di PCB V3.8; la netlist PCB V4.3 è identica. La mappa pin-per-pin è in CSV e lo schema è un file `.kicad_sch` candidato, non approvato.
- Corrette solo nella copia di studio due vecchie etichette (`RF_LNA_IN`, `RFOUT_BIAS`) che non corrispondevano al PCB; allineati i campi footprint e J105. **Non** modificati né schema storico V3.1, né PCB V3.8, né PCB di studio V4.3.
- Generatore riproducibile, test 20/20; regressioni V4.3 21/21, V4.2 19/19, V4.1 12/12 e 2.400 stati supervisore V4.0.
- Nuova procedura ERC/DRC su COPIE; qui `kicad-cli` assente, quindi **non eseguiti**. Ancora aperti confronto DXF/STEP TE, termica ADL5535, librerie footprint, parità schematico-PCB, stack-up, misure.
- **Manuale d'uso PDF illustrato V4.0** preservato: `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf` (11 pagine, BOZZA).

## File da aprire per primi

1. `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. `03_Verifiche/V4.4/RAPPORTO_TECNICO_V4.4.md` e `03_Verifiche/V4.4/VERIFICA_SCHEMA_PCB_V4.4.json`.
3. `04_KiCad/Modulo_RX_Test_50ohm_V4.4_SCHEMA_MATCH/S3900E_RX_TEST_50R_V4_4_MATCH_NETS_NOT_FOR_FAB.kicad_sch`.
4. `03_Verifiche/V4.4/NETMAP_RX_PCB_V4.4.csv`, generator/test e report regressioni.
5. Storico V4.3 per studio SMA, V4.2 per geometria, V4.1 per RF statico, V4.0 per supervisor/manuale.

**L'archivio e cumulativo**: tutti i file della V4.3 sono conservati; i documenti principali modificati hanno snapshot byte-identici V4.3. `MANIFEST_SHA256_V4.4.csv` permette controlli di integrità.
