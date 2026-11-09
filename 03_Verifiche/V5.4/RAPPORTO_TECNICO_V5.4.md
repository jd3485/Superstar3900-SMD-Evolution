# Superstar 3900 SMD Evolution — rapporto tecnico V5.4

**8 novembre 2026 · Revisione di automazione per verifica nativa · NON PER FABBRICAZIONE / NO TX**

## Nuova consegna

La V5.4 aggiunge un percorso concretamente ripetibile per la validazione di KiCad 10 **su una macchina esterna con KiCad disponibile**, inclusa una procedura facoltativa tramite GitHub Actions. Il progetto elettrico e meccanico candidato **non è stato modificato** rispetto alla V5.3. L'archivio conserva integralmente il manuale d'uso e gli elaborati precedenti.

Materiali nuovi: `03_Verifiche/V5.4/run_native_v54.py`, `test_native_runner_v54.py`, `run_regressioni_v54.py`, `PROCEDURA_NATIVA_E_CI_V5.4.md`, `.github/workflows/kicad_native_v54.yml`, report e log. Il candidato sottoposto a KiCad rimane la coppia `.kicad_sch/.kicad_pcb` V5.2 con librerie portabili locali.

## Controlli realmente eseguiti qui

| Attività | Esito |
|---|---|
| Verifica integrità in ingresso ZIP V5.3 | ZIP senza errori CRC |
| Comando `kicad-cli` | Non installato |
| Tentativo `apt-get update` | DNS repository Debian non disponibile |
| `run_native_v54.py` effettivo | Exit 3; ERC, DRC, zone refill e parità **NOT_RUN**; sorgenti immutati |
| Test V5.4 con CLI **simulate** | 8/8 superati, **non sono test KiCad** |
| Suite software V4.0–V5.4 | 15/15 superate, comprese le combinazioni del supervisore software |
| KiCad nativo e confronto TE STEP/DXF | **NON ESEGUITI** |
| Risposte scritte da PCBWay/assemblatore | **Non ricevute** |

La procedura testata rifiuta un eseguibile che dichiara KiCad 9, segnala report JSON invalidi, intercetta i codici di errore e registra la versione del tool, il riepilogo degli hash e i risultati. Non abilita Gerber o fabbricazione anche con report apparentemente puliti.

## Impatto progettuale

Nessun miglioramento RF o termico può essere dichiarato. Non ci sono nuovi moduli collaudati. L'impronta `CONSMA002-SMD-G` resta da confrontare integralmente con il CAD TE; sei vie termiche sotto U101 della variante V4.8 restano un'ipotesi che richiede il processo VIPPO e lo stencil concordati con il montatore. Restano aperte tutte le nove condizioni `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json`.

**Avanzamento storico stimato**: 37%, invariato. **0 prototipi validati. NO FAB / NO PCBWay / NO TX**.

## Passaggio decisivo successivo

Usare il workflow facoltativo o una macchina con KiCad 10 e recuperare i report ERC/DRC effettivi, poi correggere esclusivamente una nuova copia candidata in funzione degli errori documentati. La revisione V5.4 riduce la dipendenza dal sistema di lavoro locale; **non risolve per decreto** alcuna violazione eventualmente presente.

Fonti ufficiali: KiCad CLI 10 https://docs.kicad.org/10.0/en/cli/cli.html ; installazione Ubuntu https://www.kicad.org/download/details/ubuntu/ ; TE SMA https://www.te.com/en/product-CONSMA002-SMD-G.html ; ADL5535 https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf .
