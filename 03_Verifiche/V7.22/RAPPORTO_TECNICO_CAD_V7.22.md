# V7.22 — ECO effettiva U6202 exposed pad EP33, NO FAB / NO TX

**11 novembre 2026, base tecnica V7.21 (main PR #22 documentale `ac244c8f`).**

## Fonte e difetto corretto

[TlV320AIC3204 TI SLOS602E Rev E](https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf), §6 pp.5–7: pin 1–32; package RHB0032E p.52: pad termico centrale **33** nominale 3.45±0.1 mm; §12.1: obbligo di collegare al ground plane e saldare, non internamente connesso. Lo schema originale includeva solo 1–32.

## Nuovo CAD

- `04_KiCad/Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB/`: copia versionata del foglio MCU, simbolo embedded del codec con nuovo pin **33 EP_GND_THERMAL_PAD** tipo passive (48.26,−30.48); istanza U6202 a (400,160) quindi endpoint a (448.26,190.48), con etichetta **GND locale**. Già presenti U6202 IOVSS:7 AVSS:17 DVSS:28 sulla medesima rete locale. Nessuna unione con masse RX/AUX, GND_MAIN o EFUSE_RTN. Nessun PWR_FLAG.
- `04_KiCad/Assemblaggio_RX_Power_V7.22_EP33_NOT_FOR_FAB/`: nuovo root 7 fogli che include lo schema MCU V7.22; progetto e tabelle librerie locali mantenuti.

## Verifica CI

Workflow `v722_codec_ep33_native.yml` esegue KiCad9 CLI ERC/netlist originali e revised, richiede stessa topologia tranne **un solo ref-pin-net U6202/33 sulla GND locale**, 100 reti, 132 componenti, pin 1–32 conservati e conformi ai nomi TI, nessun ERC nuovo critico. 10 nuovi test V7.22 + 308 regressioni storiche (attesi 318 complessivi). Non segnare PASS senza conferma CI.

## HOLD

**Nessun footprint assegnato al codec**: il VQFN-32-1EP 5×5 KiCad è candidato, non validato per land/paste/stencil/assemblaggio; U6201 e U6203–U6206 e altri 42 componenti ancora senza impronta, 48 totali non assegnati, F200/Y1 non validati. Root ERC baseline 36 errori/340 warning; PCB unica inesistente, 15 interfacce OPEN/HOLD, SG48 HOLD. Progresso layout ~10% stimato invariato.

**NO FAB / NO GERBER / NO PCBWAY / NO TX.** Next V7.23: verificare MPN, pin/pad ST LQFP64 e TI DBV e il footprint, quindi altre 42 impronte.

## Qualifica statica aggiuntiva dei pin elettrici ST e TI (sorgenti produttore)

Confronto completo del simbolo nativo U6201 con [ST DS12288 Rev.6, Figura 7, pagina 50, LQFP64](https://www.st.com/resource/en/datasheet/stm32g474vb.pdf): **64/64 pin-numeri e nomi elettrici coincidono** con STM32G474RE_LQFP64_DRAFT. Controllo attento a pin 7 PG10-NRST, 27 VSSA, 28 VREF+, 29 VDDA, 61 PB8-BOOT0 e ripetizioni VSS/VDD. Nessuna assegnazione del footprint e nessuna approvazione MPN/land pattern.

Confronto del simbolo condiviso U6203, U6204, U6205, U6206 con [TI SBVS338H Rev.H, Figura 4-4 e Pin Functions, pagina 4, DBV 5-pin SOT23](https://www.ti.com/lit/ds/symlink/tps7a20.pdf): **5/5 mapping** 1 IN, 2 GND, 3 EN, 4 N/C, 5 OUT; pad 4 esplicitamente senza collegamento elettrico. I quattro valori TPS7A2033PDBVR e i footprint vuoti sono controllati. **Non** significa validazione termica a 300mA, geometria DBV produttore, paste/mask o footprint pronto. I 2 nuovi test statici rendono eseguibile il controllo non appena Actions riparte; esecuzione CI ancora NON comprovata.
