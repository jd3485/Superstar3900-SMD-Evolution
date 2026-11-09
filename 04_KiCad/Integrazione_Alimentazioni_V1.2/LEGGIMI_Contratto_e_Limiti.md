# Contratto di integrazione alimentazioni V1.2

**Non e' ancora un progetto KiCad gerarchico collegato.** I tre fogli `INTEGRATION_DRAFT` sono copie con etichette locali uniformate; la loro presenza in una cartella non ne realizza la connessione elettrica. Va ancora costruito un top-level con hierarchical pins/power flags, quindi ERC nativo, prova di netlist e revisione dei footprint.

- `EFUSE` esce su `BUCK_VIN_PROTECTED`, che diventa ingresso `BUCK`.
- `BUCK` esce su `5V_RF_PREREGULATED`, che alimenta i due LDO dello schema `PLL`.
- Nella bozza V1.0 buck chiamava il ritorno `GND_RF_SUPPLY`; nella V0.9 PLL era `GND`. Per il contratto di integrazione sono stati uniformati a `GND_MAIN` (rete di riferimento elettrico proposta; la distribuzione fisica delle masse deve ancora essere progettata).
- **`EFUSE_RTN` deve restare isolato da `GND_MAIN`**: vincolo essenziale; accoppiamenti parassiti/filtri dovranno essere analizzati prima di connettere ritorni reali.
- Pin10 TCXO resta ambiguo e non valido per la fabbricazione.
- F200 ha package 451: il footprint 1206 dell'originale era scorretto ed e' stato sostituito con un identificatore di footprint inesistente volutamente marcato NON VALIDATO.

I controlli sui nomi delle reti verificano SOLO la consistenza delle etichette presenti nei file; non equivalgono a netlist elettrica estratta da KiCad o a simulazione.
