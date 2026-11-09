# S3900E RX TEST V4.4 — schema candidato / NON PER FABBRICAZIONE

Schema elettrico di studio ricostruito automaticamente dalle 31 associazioni `riferimento.pin → rete` del PCB V3.8; i 15 riferimenti, 8 nomi di rete e valori dei componenti corrispondono anche al PCB di studio V4.3. Il progetto **non è ancora accoppiato a KiCad** tramite UUID/riferimenti di progetto e non è stato sottoposto a ERC, DRC o sincronizzazione grafica.

Genera e verifica: `python3 ../../03_Verifiche/V4.4/sincronizza_schema_rx_v44.py` dalla cartella del progetto. Confronto di CSV, test e launcher nativo: `03_Verifiche/V4.4/`.

**Non usare per realizzare PCB:** la geometria SMA TE, la gestione termica ADL5535, le librerie dei footprint e lo stack-up RF restano senza approvazione. Consultare `03_Verifiche/V4.4/RAPPORTO_TECNICO_V4.4.md`.
