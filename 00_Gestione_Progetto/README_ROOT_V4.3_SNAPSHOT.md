# Superstar 3900 SMD Evolution — V4.3 cumulativa (2026-11-08)

**37% avanzamento progettuale stimato, ZERO hardware validato. NO FAB / NO PCBWAY / NO TX.**

## Novità V4.3

- Variante *solamente di studio* del PCB V3.8 per SMA: 16 piazzole GND spostate di 0,18 mm verso l'esterno, inviluppo nominale 7,76 mm. Non derivata da CAD ufficiale, non approvata TE.
- Rispetto a V3.8 invariati numero componenti, reti, piste, via e tutte le geometrie tranne i 16 centri pad GND SMA. 21 test V4.3 statici superati; 19 test V4.2 e 12 V4.1 ripetuti, più 2.400 casi supervisore V4.0 rieseguiti.
- Preservato PCB V3.8 byte-identico; termica ADL5535 e rientro 50 Ω aperti. KiCad nativo non installato; non è stato eseguito alcun DRC/ERC.
- Rapporto: `03_Verifiche/V4.3/RAPPORTO_TECNICO_V4.3.md`; JSON/PNG/test nello stesso percorso.
- Manuale d'uso illustrato bozza: `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf` (invariato).

## Ripresa in nuova chat

1. Leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, il registro decisioni e `00_Gestione_Progetto/CHANGELOG_V4.3.md`.
2. Rivedere `03_Verifiche/V4.3/RAPPORTO_TECNICO_V4.3.md`, `01_Specifiche/Checklist_SMA_ADL5535_V4.3.md`.
3. Rigenerare/verificare: `python3 03_Verifiche/V4.3/crea_e_verifica_candidato_sma_v43.py` e `python3 03_Verifiche/V4.3/test_candidato_sma_v43.py` (Shapely 2.x); non usare questi output come DRC.
4. Prima di produrre: CAD ufficiale TE, studio termico ADI, schema RX aggiornato, KiCad DRC/ERC reali, zone riempite e stack-up approvato.

Ogni ZIP contiene tutte le versioni precedenti, snapshot dei documenti modificati e manifest SHA-256.
