# Superstar 3900 SMD Evolution — ripresa da V3.9 (2026-11-08)

Archivio cumulativo da usare: `Superstar3900_SMD_Evolution_V3.9.zip`.

Stato: **37% di avanzamento progettuale stimato, NON fabbricabile**. V3.9 è una revisione documentale: ultimo PCB è il coupon RX V3.8, 110×62 mm, 15 footprint, 8 reti, 44 segmenti, 64 via GND e 4 zone di massa non riempite. Restano da validare schematico, stack-up, termica, RF e compliance.

Requisiti invariati: 270 posizioni RX = 6×(40+5 ALFA), tasto ALFA fisico, CH9 27,065 MHz AM prioritario; AM/FM/USB/LSB/CW/PA, VOX, dual watch, roger beep, echo, 50 CTCSS, 104 DCS, display frequenza, ATU, SWR/potenza/modulazione e estetica vintage. TX limitato alle frequenze, potenze e modalità legali italiane con interlock fail-closed hardware e firmware da collaudare. Proposte principali: STM32G474RE, TLV320AIC3204 a 48 kHz, LMX2572 con TCXO 12,8 MHz e IF 10,695 MHz; candidature non tutte approvate.

V3.9: integrazione fonti TE ufficiali per `CONSMA002-SMD-G`. Il disegno cliente rev D copre il connettore standard e quello dorato; center land Ø2,05 mm in V3.8 corrisponde nominalmente, ma pad GND custom si estendono 7,40 mm verticali a fronte di 7,76 mm del footprint raccomandato: **non approvato**. Audit statico e protocollo CAD aggiornati; regressioni V3.8 44/44 e V3.7 17/17 e hash storico verificati. Non è stata svolta alcuna verifica nativa KiCad: `kicad-cli` non disponibile.

**Prossimo obiettivo**: CAD TE 2D/3D ufficiale e correzione footprint su COPIA, conferma ADL5535/paste, KiCad nativo apertura schema+PCB/ERC/DRC dopo riempimento zone, approvazione stack-up PCBWay 50 Ω. Poi soltanto prototipo RX e VNA con TX fisicamente scollegata. Niente Gerber né ordine produttivo finché restano bloccanti.

Vedi `01_Specifiche/Protocollo_Accettazione_CAD_V3.9.md` e `03_Verifiche/V3.9/RAPPORTO_VERIFICA_V3.9.md`.
