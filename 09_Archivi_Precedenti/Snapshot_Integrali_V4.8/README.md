# Superstar 3900 SMD Evolution — V4.8 (cumulativa)

**Stato**: progetto sperimentale. Nessun hardware collaudato, 37% avanzamento progettuale stimato. **NO FAB / NO PCBWAY / NO TX.**

## Novità V4.8

- `03_Verifiche/V4.8/RAPPORTO_TECNICO_V4.8.md`: relazione e limiti delle verifiche.
- `04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/`: progetto candidato *separato*, con sei via-in-pad GND 0,55/0,25 mm sotto U101. Non fabbricabile senza via fill/cap, stencil e qualifica RF/termica.
- `03_Verifiche/V4.8/test_variante_termica_v48.py`: controllo reversibilità e geometria.
- `03_Verifiche/V4.8/RUN_KICAD_CANDIDATO_V48.sh`: ERC/DRC su copia, senza Gerber; non eseguito per KiCad assente.
- `MANIFEST_SHA256_V4.8.csv`: hash dei file correnti escluso sé stesso.
- `09_Archivi_Precedenti/Snapshot_Integrali_V4.7/`: copie byte-identiche dei documenti attivi aggiornati.

**Ripresa:** leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, registro decisioni e rapporto V4.8. Manuale illustrato V4.0 ancora presente nella cartella `06_Manuali`.

---
## Testo storico (V4.7 e precedenti)

# Superstar 3900 SMD Evolution — V4.7 cumulativa (8 novembre 2026)

**Stato:** ricerca/progettazione 37% stimato, **zero hardware collaudato**, **NO FAB / NO PCBWay / NO TX**.

## Novità verificata V4.7

- Recuperato il **disegno ufficiale TE rev. D** del `CONSMA002-SMD-G`. Nel candidato SMA V4.3/V4.5 coincidono staticamente soltanto Ø2,05 mm del disco centrale e 7,76 mm dell'inviluppo verticale GND. Non è una validazione completa del footprint. DXF/STEP disponibili sul sito TE ma **non acquisiti**.
- I pad GND custom degli SMA dispongono di F.Mask/F.Paste senza riduzione esplicita, da approvare con l'assemblatore. Per U101 ADL5535 la formula nominale dell'apertura paste con ratio -0,100 dà circa 81% dell'area pad: **non** una misura termica o verifica stencil.
- **28/28 test V4.7 superati**; regressioni V4.0–V4.6 rieseguite. KiCad CLI assente: **ERC/DRC, refill e parità NON ESEGUITI**. Schemi, PCB e librerie candidati rimangono inalterati.
- `03_Verifiche/V4.7/RAPPORTO_TECNICO_V4.7.md`, `AUDIT_SMA_TE_V4.7.json`, `GEOMETRIA_SMA_STUDIO_V4.7.png` e `CHECKLIST_ACCETTAZIONE_V4.7.csv`.
- Tutte le versioni precedenti e il manuale illustrato V4.0 sono inclusi; documenti sostituiti salvati byte-per-byte in `00_Gestione_Progetto/V4.7_SNAPSHOT_V4.6/`.

**Per proseguire:** aprire `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, poi il rapporto V4.7; acquisire CAD TE esatto e validare in KiCad 10 prima di un prototipo.

---

## README precedente V4.6 conservato

# Superstar 3900 SMD Evolution — V4.6 cumulativa (8 novembre 2026)

**Stato ufficiale:** ricerca/progettazione in corso, **37% stimato**, **0 moduli hardware validati**. **NO FAB / NO PCBWay / NO TX**.

## Novità V4.6

- Audit dimensionale dei collegamenti di massa dell'ADL5535 U101: pad esposto 1,80×3,48 mm, via GND più vicino separato da 0,50 mm di rame; assenza di via-in-pad. Il layout è invariato e la termica rimane NON APPROVATA.
- Analisi dei quattro SMA J101–J104 nel candidato portabile: CAD TE DXF/STEP elencati dal produttore ma non acquisiti. Footprint e ingombro restano NON APPROVATI.
- Nuovo lanciatore KiCad che verifica `--refill-zones` e `--schematic-parity`, usa una copia temporanea e non salva il PCB: **KiCad non disponibile qui, native checks NON ESEGUITI**. Procedura KiCad 10 pronta per verifica esterna.
- 24/24 nuovi test statici e di blocco fail-closed superati, più suite V4.0–V4.5 rieseguite. Il manuale d'uso illustrato V4.0 e tutte le revisioni storiche restano nell'archivio.
- Corretta la guida interna di ripresa che era rimasta a V4.4; gli originali V4.5 sono salvati in `00_Gestione_Progetto/V4.6_SNAPSHOT_V4.5/`.

## Per riprendere rapidamente

1. Leggi `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. Leggi `03_Verifiche/V4.6/RAPPORTO_TECNICO_V4.6.md`, `AUDIT_TERMICA_SMA_V4.6.json` e il disegno `DETTAGLIO_PAD_TERMICO_U101_V4.6.png`.
3. Per i test: `python3 03_Verifiche/V4.6/test_rischi_v46.py`; per KiCad **reale**, su macchina con KiCad 10, `bash 03_Verifiche/V4.6/RUN_KICAD_RX_V46.sh ./risultati_kicad`.
4. Non produrre o ordinare nulla fino ad approvazione del CAD TE, termica ADL5535, impedenza e controlli nativi KiCad, seguiti da collaudi RF.

---

## README storico V4.5 (conservato per orientamento)

# Superstar 3900 SMD Evolution — V4.5 cumulativa (2026-11-08)

**Stato: progettazione/documentazione 37% stimato, zero prototipi convalidati; NO FAB / NO PCBWAY / NO TX.**

## Novità V4.5

Il modulo RX sperimentale dispone ora di **librerie KiCad locali**, generate dai footprint incorporati nella copia V4.3 del PCB e dai simboli dello schema candidato V4.4.

- **3 librerie footprint `.pretty` con 9 componenti tipo**, una libreria simboli con 9 simboli e tabelle riferite a `${KIPRJMOD}`. Layout 15 componenti riprodotto; non modificato il rame del candidato né l'originale V3.8.
- **26 test statici V4.5 superati**; eseguite di nuovo suite V4.0–V4.4. Non eseguiti ERC, DRC/refill o verifica di parità con KiCad, perché `kicad-cli` non disponibile.
- **Rischi aperti**: confronto CAD ufficiale TE CONSMA002-SMD-G, dissipazione ADL5535, approvazione stack-up 50 Ω, validazione PCB KiCad e misure RF.
- **Manuale illustrato V4.0** incluso: `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. È ancora una bozza, non un manuale di un apparato collaudato.

## File di accesso

1. `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. `03_Verifiche/V4.5/RAPPORTO_TECNICO_V4.5.md`, `INVENTARIO_LIBRERIE_V4.5.json`, `TEST_V4.5.txt`.
3. `04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB/README.md`.
4. `03_Verifiche/V4.5/crea_librerie_v45.py` (rigenerazione), `test_librerie_v45.py` (suite) e `RUN_KICAD_RX_V45.sh` (richiede KiCad installato).
5. `00_Gestione_Progetto/CHANGELOG_V4.5.md` e tutti gli snapshot e manifest precedenti.

L'archivio V4.5 è **cumulativo**. I documenti attivi V4.4 aggiornati hanno copie byte-identiche denominate SNAPSHOT; tutte le revisioni e il manuale restano nell'archivio. Il progetto V4.5 non è utilizzabile per fabbricazione senza una revisione ingegneristica e verifiche hardware.
