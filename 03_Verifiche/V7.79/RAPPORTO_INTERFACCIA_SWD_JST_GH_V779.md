# V7.79 — reale interfaccia di servizio SWD su MCU STM32G474RE

**Modifica elettrica progettata:** connettore SMD **J6201 JST GH 5 vie**, MPN [BM05B-GHS-TBT(LF)(SN)](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf), passo 1,25 mm, con footprint KiCad9 `Connector_JST:JST_GH_BM05B-GHS-TBT_1x05-1MP_P1.25mm_Vertical` e involucro accoppiato `GHR-05V-S`. Lo schema **MCU** versionato contiene un nuovo simbolo 5 pin, coordinato alla nuova libreria S3900E; il master 7 fogli V7.79 punta solo al nuovo MCU, conservando l'**AUX V7.78** e tutti gli altri moduli.

| J6201 pin | Rete MCU esistente | Destinazione/funzione |
|---|---|---|
| 1 | `3V3_MCU` | riferimento di tensione **VTREF, sola lettura** dall'adattatore SWD; **vietata iniezione di potenza** |
| 2 | `MCU_SWDIO` | STM32 SWDIO, programmazione/debug RX-only sulla radio |
| 3 | `MCU_SWCLK` | STM32 SWCLK |
| 4 | `MCU_NRST` | reset STM32 (non reset eFuse) |
| 5 | `GND` | esclusivamente massa **MCU**, senza unirla ad `AUX GND_MAIN` o `EFUSE_RTN` |

Questo **non è** un connettore ARM-Cortex 10-pin standard: è un JST-GH cinque vie con cablaggio personalizzato obbligatorio. **Mating housing, pin1, crimps, cablaggio, isolamento, ESD, accessibilità e carico target sotto debugger sono HOLD**. Non collegare ST-LINK, USB, veicolo, alimentatori o debugger fisici senza validazione del cablaggio e dei domini. Nessun collegamento TX o PTT è stato introdotto. Il VTREF **non è** una seconda sorgente di alimentazione e il connettore non qualifica la fonte originale 3,3 V.

## Prove automatiche da CI KiCad9

`03_Verifiche/V7.79/test_native_mcu_swd_jst_gh_v779.py` esamina netlist/ERC **prima e dopo** l'intero master nativo. Deve dimostrare **140→141 componenti**, nessun componente preesistente modificato, nessuna perdita/creazione impropria di reti, **soli cinque nuovi pin J6201** su reti MCU nominate, ESD/circuitazione HW non proclamate. L'ERC può ridurre errori `label_dangling` **solo** relativi a `MCU_NRST`, `MCU_SWDIO`, `MCU_SWCLK` (una vera interfaccia fisica), senza sopprimere errori power o altri problemi. Il test confronta anche il footprint JST GH *reale* via pcbnew e la numerazione dei cinque pad. Esiti da confermare dal run CI prima del merge.

**Limitazioni permanenti:** RX/PLL/MCU/AUX interfacce ancora HOLD, sei `power_pin_not_driven` fonte/ritorno non qualificati, eFuse recupero/F200, SWD GPIO tolerance, power budget 3,3V e loop 5V, TCXO pin10, PCB unica/DRC non eseguiti. No waiver, PWR_FLAG, rete 3V3 esterna o ponte fra masse. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
