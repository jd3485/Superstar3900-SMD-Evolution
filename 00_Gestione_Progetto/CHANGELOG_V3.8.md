# CHANGELOG — Superstar 3900 SMD Evolution V3.8
Data: 2026-11-07
Avanzamento complessivo **37%**, invariato da V3.7. Coupon RX **NON FABBRICABILE**.

## Modifiche reali

- Generata la PCB KiCad da 110 × 62 mm **V3.8**, 15 componenti, 8 reti, 44 segmenti di rame, 64 via e 4 zone massa non riempite.
- Sostituite le quattro piazzole GND rettangolari di ciascun SMA con forme KiCad `smd custom` sagomate **candidate**. Il land centrale diametro 2,05 mm resta SMD senza foro. Non si dichiara la copia esatta della footprint TE ufficiale.
- Esteso il contorno meccanico sul livello `F.CrtYd` del modello SMA; stimata sporgenza oltre il bordo di circa 7,2 mm sui due lati in base alle quote assunte. Non eseguita verifica 3D.
- Esplicitata pista F.Cu verso un via GND esterno al paddle di U101 ADL5535, senza via aperti nell'area di saldatura; rapporto pasta del paddle impostato a -0.10 **candidato**; connessione piena ai piani richiesta ma zone ancora non riempite.
- Generata libreria KiCad locale sperimentale dei due footprint, anteprima del layout e nuovo audit che usa i contorni **reali** dei pad custom invece della loro sola scatola d'ingombro.
- 36 nuovi controlli automatici positivi, inclusa prova negativa di corto geometrico introdotto intenzionalmente; regressione V3.7 17/17 e V3.6 superata.
- Nuovo dossier PDF in tre pagine, guida di test KiCad nativo, registro problemi aperti e archivio cumulativo con hash.

## Vincoli rimasti aperti
- La quota esatta dei contatti laterali di massa dipende dal CAD certificato del part number ordinato; verifica suffisso `-G`.
- KiCad CLI non disponibile: nessun ERC/DRC nativo né riempimento dei piani.
- Nessuna verifica dei Gerber, solder mask, 3D, termica FEM, VNA o RF alimentata.
- Stack-up PCBWay e impedenza RF da confermare.
- Coupon solo RX bench, mai collegare a TX attivo.

## Decisione
**NO FAB / NO PCBWAY**. Prossimo rilascio V3.9 dedicato all'approvazione footprint, all'esecuzione nativa KiCad e al controllo termico.
