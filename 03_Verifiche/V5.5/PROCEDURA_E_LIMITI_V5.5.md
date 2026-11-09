# V5.5 — screening del rame e post-verifica dei rapporti KiCad 10

**STUDIO NON PER FABBRICAZIONE.** I file di produzione, gli ordini e la TX restano vietati.

## Novità

1. `audit_rame_v55.py` analizza geometricamente piazzole `F.Cu` comprese le poligonali custom dei connettori SMA, segmenti e vie. Usa Shapely 2 per distanze tra reti differenti. Le zone GND esistono ma **non sono riempite**: l'esito è `STATIC_SCREEN_PASS`, **non DRC**.
2. `validate_native_reports_v55.py` interpreta la struttura di report ERC/DRC KiCad 10: fogli ERC; array DRC `violations`, `unconnected_items`, `schematic_parity`; metadata e versione. Rifiuta report parziali, array mancanti e incongruenze col runner V5.4. La correttezza strutturale **non** dimostra la provenienza autentica del JSON.
3. `run_native_v55.py` esegue prima il runner V5.4, quindi il nuovo post-validatore, salvando report/log nella cartella di output. Se KiCad non esiste, fallisce senza promuovere il progetto.
4. `.github/workflows/kicad_native_v55.yml` predispone il test manuale su Ubuntu 24.04 con KiCad 10, dipendenza Shapely e caricamento dei rapporti anche in caso di errore. **Mai avviato in questa sessione.**

## Sul proprio computer

Da radice progetto estratto:

```bash
python3 -m pip install 'shapely>=2,<3'    # ambiente virtuale consigliato
python3 -B 03_Verifiche/V5.5/test_v55.py
python3 -B 03_Verifiche/V5.5/audit_rame_v55.py --output AUDIT_RAME_FCU_V5.5.json
python3 -B 03_Verifiche/V5.5/run_native_v55.py --output REPORT_NATIVE_V5.5
```

Su un host con KiCad 10 valido, leggere attentamente i report `STATUS_V5.4.json`, `ERC_V5.4.json`, `DRC_PARITY_V5.4.json` e `SUMMARY_V5.5.json`, oltre ai log. Gli stati **`NOT_RUN`**, **`INCOMPLETE_OR_VIOLATIONS`**, e anche **`STRUCTURE_CHECK_PASS_REVIEW_REQUIRED`** non costituiscono approvazione fabbricativa. Il runner lavora su una copia; non esporta Gerber.

## Controllo numerico effettivo (non nativo)

- Strato analizzato: solo `F.Cu` con piazzole, piste e vie non comprensive di rame da riempimento zone.
- Screening con soglia di confronto *analitica* 0,30 mm: nessuna violazione rilevata.
- Distanza minima inter-net geometrica: **0,45 mm**; compare in **cinque** coppie di pad dei componenti C101, C102, R201, R202 e R203.
- 5.267 coppie di geometrie di reti differenti esaminate; 4 zone GND definite, 0 poligoni riempiti.
- Non coperti: DRC di KiCad, zone GND, clearance da fori o bordi, maschera/pasta, rame degli strati interni e inferiore, overlap di courtyards, schemi, stack-up e impedenza RF, via-in-pad termico/stencil e disegno TE ufficiale.

## Gate di produzione

**Tutti e nove i gate V5.0 restano aperti:** ERC/DRC con refill/parità su KiCad reale, CAD ufficiale TE, processo VIPPO, stencil, stack-up, termica, qualità RF e verifica del produttore. Il controllo V5.5 è preliminare e riproducibile, non sostitutivo.

Documentazione di riferimento: https://docs.kicad.org/10.0/en/cli/cli.html ; https://docs.kicad.org/doxygen/structRC__JSON_1_1DRC__REPORT.html ; https://www.kicad.org/download/linux-distros/ .
