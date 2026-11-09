# Superstar 3900 SMD Evolution - V4.2 cumulativa (2026-11-08)

**Stato: 37% progettuale stimato, invariato. ZERO hardware collaudato. NO FAB / NO PCBWAY / NO TX.**

## Novità V4.2

- Audit geometrico 2D F.Cu con pads SMA custom reali e rotazioni; controllo inter-reti, continuità 7 segnali e percorso verso via locale per 24 pad GND.
- Risultato: minimo 0,450 mm tra reti distinte, zero interferenze sotto una soglia analitica di 0,20 mm, **19 test passati**. **Non** è un DRC nativo.
- Analisi courtyard/ingombro SMA: sporgenza modello 7,2 mm su bordo sinistro/destro. Footprint TE ancora da approvare (GND 7,40 contro 7,76 mm nel disegno TE); NO modifica al PCB V3.8.
- Studio parametricamente semplificato di impedenza microstrip: mostra dipendenza da h L1-L2; **non** definisce impedenza CPWG reale.
- Documenti aggiornati su analisi termica ADL5535, stack-up e criteri di signoff. Nessuna misura termica o RF.

## Avvio nuova chat

1. Leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, poi `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. Leggere `03_Verifiche/V4.2/RAPPORTO_TECNICO_V4.2.md` e `01_Specifiche/Decisioni_Impedenza_CPWG_V4.2.md`.
3. Rieseguire `python3 03_Verifiche/V4.2/test_geometria_rf_v42.py` (Shapely 2.x) e `python3 03_Verifiche/V4.1/test_audit_rf_v41.py`.
4. Manuale illustrato completo alla bozza V4.0: `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`, 11 pagine.
5. Ripartire dai cancelli aperti TE/ADI/DRC/stack-up; `03_Verifiche/V4.1/RUN_KICAD_NATIVE_V4.1.sh` per KiCad 10+ su una macchina che lo dispone. La sua esistenza non significa che KiCad sia stato eseguito.

**Le revisioni cumulano integralmente sorgenti e documenti; gli aggiornamenti attivi sono accompagnati da snapshot delle versioni precedenti e manifest SHA-256.**
