# Superstar 3900 SMD Evolution - CHANGES V3.7 (2026-11-07)

**Avanzamento stimato 37%, invariato. BLOCCO FABBRICAZIONE.**

- Analizzato il foglio 2/3 del disegno TE/Linx rev D CONSMA002-SMD: la quota Ø2,05 sul land pattern di superficie non comporta una prescrizione di foratura; la V3.7 usa un **pad 1 SMT circolare senza drill** in tutti e quattro i candidati SMA.
- Riorientati in PCB J102 e J104 di 180°: modello meccanico assunto accoppiamento verso destra; J101/J103 verso sinistra. La simmetria di pad consente di conservare tutti i tracciati senza interrompere le reti.
- Creati due moduli modificabili `.kicad_mod` nella libreria `S3900E_Review.pretty` e tabella `fp-lib-table`; **i moduli sono CANDIDATI, non footprint ufficiali**.
- Riscontrata e documentata la differenza residua: quattro piazzole GND quadrate modellate anziché geometrie laterali sagomate del disegno TE. Non è ancora autorizzato l’assemblaggio.
- Confrontato U101 con Analog Devices ADL5535 rev A Fig17: paddle 1,80 x 3,48 mm e pad segnale 0,86 x 1,27 mm, ma stencil/via termici ancora da definire.
- Rigenerati PNG/SVG, due CSV di confronto/orientamento, JSON audit e test automatici comprensivi di mutazioni negative. Nessuna modifica ai 43 segmenti, 64 via e alle quattro zone di massa non riempite.
- Verificati 31 contatti pin–rete, 24 contatti GND→via, sette reti RF/power continue, 0 clash nel modello 2D (limite 0,20 mm, minimo modellato 0,45 mm).
- KiCad CLI assente; tentativo di update del repository Debian fallito per DNS; **nessun DRC/ERC KiCad**, nessun Gerber, nessuna PCB prodotta, nessuna misura RF effettuata.
- Conservate tutte le revisioni precedenti nell'archivio ZIP cumulativo.
