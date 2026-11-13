# Audit e riduzione costi GitHub Actions — 13 novembre 2026

Repository: `jd3485/Superstar3900-SMD-Evolution`. **L'utente autorizza l'ottimizzazione dei workflow, NON la modifica delle impostazioni di fatturazione GitHub.** Nessuna modifica al CAD, alle netlist, ai risultati dei test tecnici o ai vincoli NO FAB/NO TX. Stato tecnico di partenza V7.44 integrata su main (PR #47), V7.45 in handoff.

## Inventario reale

La directory `.github/workflows/` di `main` contiene **49 file YAML**, non i 34 indicati nel vecchio protocollo. La presenza di un workflow **non significa** che esso sia sempre eseguito né che sia fatturato. I workflow rilevati usano trigger mirati `pull_request.paths` + `workflow_dispatch`, tranne i quattro vecchi test KiCad V5.4–5.7 che già erano manual-only. Non abbiamo consultato i dati di billing/account, perciò **non forniamo un risparmio in euro misurato**.

## Duplicazione eliminata

Nella vecchia V7.12 risultavano contemporaneamente attivabili:

| Workflow | Trigger automatici sovrapposti prima della ECO | Ruolo |
|---|---|---|
| `v712_kicad_native_annotation.yml` | `04_KiCad/Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB/**` e `03_Verifiche/V7.12/**` | Suite integrale KiCad: export gerarchico, netlist, ERC, RX parser, DRC del coupon, regressioni Python |
| `v712_rx_schematic_native_probe.yml` | Gli stessi due pattern | Diagnostica sperimentale supplementare per confrontare la schematica RX V5.2 e la candidata V7.12, con una **seconda installazione di KiCad** |

**Intervento:** `v712_rx_schematic_native_probe.yml` diventa `workflow_dispatch` **soltanto manuale**. Nessuno dei suoi step è eliminato; la diagnostica si può eseguire manualmente quando utile. La suite **`v712_kicad_native_annotation.yml` rimane automatica su quei percorsi**, conservando l'ERC, le verifiche della schematica RX standalone, il DRC e i test storici. Quando una PR modifica uno dei due percorsi comuni, non parte più automaticamente la seconda pipeline KiCad di sola esplorazione. L'eventuale risparmio è **un run sperimentale evitato per PR interessata**, non una percentuale generale del conto GitHub.

## Controllo anti-duplicazione permanente

`ci/workflow_policy/audit_workflow_costs.py` ora:
1. Richiede che i cinque workflow deliberatamente **manual-only** restino tali (V5.4–V5.7 + sonda RX V7.12).
2. Rileva i pattern PR **identici** rivendicati da più workflow, e ne impedisce l'aggiunta involontaria nelle revisioni future.
3. Mantiene una **eccezione intenzionale** per `v722_codec_ep33_native.yml` e `v723_kicad9_footprint_native.yml` sui tre pattern di librerie `Librerie_Footprint_V7.22_...`: il primo verifica netlist/EP33 e regressioni elettriche, il secondo usa le API native PCBNEW per leggere e verificare le vere impronte. Non si elimina un controllo fisico importante per un solo risparmio di run.
4. Mantiene tutte le altre regole preesistenti: no push, no trigger globali `04_KiCad/**`, no self-trigger, `workflow_dispatch` come recupero, permessi minimi, concurrency cancella **solo** run PR obsoleti, non verifiche manuali, conservazione gate originali V7.0.
5. Nel workflow di policy `actions_policy_quick.yml`, tenta di **riusare PyYAML già disponibile sul runner** e installa la versione fissata `6.0.3` solo in assenza del modulo. Il controllo YAML non viene eliminato e non si presume che il package sia sempre già installato.

Questa guardia blocca **duplicazioni di pattern esatti**. Non è un solver generale per l'intersezione di wildcard parzialmente sovrapposte, e non è una prova che tutti i 49 workflow siano privi di altro lavoro simile. Le revisioni future devono continuare a riusare test e report esistenti quando possibile anziché introdurre workflow ripetitivi. Nei lavori CAD/elettrici resta obbligatoria la netlist/ERC nativa prima/dopo e DRC se è presente una PCB reale.

## Verifica finale e condizioni

La modifica ai workflow e al file di policy deve superare il run **`actions_policy_quick.yml`** sulla Pull Request. Non dichiarare PASS o merge in assenza di evidenza del run specifico. Non viene avviata KiCad9 perché nessun CAD o test tecnico è modificato; non si tocca alcun settaggio di billing o repository. Lo storico di fallimenti non va cancellato e i run antichi non vengono rieseguiti.

**Sicurezza:** nessuna modifica di fabbricazione, nessun Gerber o TX, SG48 e 15 interfacce cross-module ancora HOLD. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**
