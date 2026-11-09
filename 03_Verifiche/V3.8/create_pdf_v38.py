#!/usr/bin/env python3
"""ReportLab short dossier of V3.8 static engineering review, no fabrication claims."""
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak, KeepTogether
from reportlab.pdfbase.pdfmetrics import stringWidth
ROOT=Path(__file__).resolve().parents[2]
PDF=ROOT/'Superstar3900_Dossier_Tecnico_V3.8.pdf'
DAT=json.loads((ROOT/'03_Verifiche/V3.8/Audit_Footprint_Termico_V3.8.json').read_text())
PAGE_W,PAGE_H=210*mm,297*mm
TEAL=colors.HexColor('#087f7d');INK=colors.HexColor('#203345');MUTED=colors.HexColor('#5f6e79');PALE=colors.HexColor('#eef5f6');RED=colors.HexColor('#9b3233')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='A_Title',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=18,leading=22,textColor=INK,spaceAfter=8))
styles.add(ParagraphStyle(name='A_Sub',parent=styles['Normal'],fontName='Helvetica',fontSize=9.6,leading=14,textColor=MUTED,spaceAfter=13))
styles.add(ParagraphStyle(name='A_H',parent=styles['Heading2'],fontName='Helvetica-Bold',fontSize=11.5,leading=15,textColor=TEAL,spaceBefore=13,spaceAfter=7))
styles.add(ParagraphStyle(name='A_Body',parent=styles['BodyText'],fontName='Helvetica',fontSize=9,leading=13,textColor=INK,spaceAfter=8))
styles.add(ParagraphStyle(name='A_Small',parent=styles['BodyText'],fontName='Helvetica',fontSize=7.7,leading=11,textColor=INK,spaceAfter=5))
styles.add(ParagraphStyle(name='A_Cell',parent=styles['BodyText'],fontName='Helvetica',fontSize=8.5,leading=11,textColor=INK))
styles.add(ParagraphStyle(name='A_White',parent=styles['BodyText'],fontName='Helvetica-Bold',fontSize=8.5,leading=11,textColor=colors.white))

def P(s,sty='A_Body'):return Paragraph(s,styles[sty])
def T(rows,widths):
    conv=[[P(str(v),'A_White' if i==0 else 'A_Cell') for v in row] for i,row in enumerate(rows)]
    tab=Table(conv,colWidths=widths,hAlign='LEFT',repeatRows=1)
    tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),0.6,TEAL),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]))
    return tab

def footer(c,doc):
    c.saveState();c.setStrokeColor(colors.HexColor('#d2dedf'));c.setLineWidth(.6);c.line(17*mm,17.6*mm,193*mm,17.6*mm)
    c.setFillColor(MUTED);c.setFont('Helvetica',8)
    c.drawString(17*mm,12.2*mm,'S3900E  |  V3.8  |  Studio RF RX 50 ohm  |  NON PRODURRE')
    c.drawRightString(193*mm,12.2*mm,f'Pagina {doc.page}')
    c.restoreState()

doc=SimpleDocTemplate(str(PDF),pagesize=(PAGE_W,PAGE_H),leftMargin=17*mm,rightMargin=17*mm,topMargin=18*mm,bottomMargin=23*mm,title='Superstar 3900 SMD Evolution - Dossier V3.8',author='Progetto S3900E')
w=176*mm
story=[]
story.extend([
 P('Superstar 3900 SMD Evolution | V3.8','A_Title'),
 P('Modulo RX di prova a 50 Ohm · Revisione footprint SMA e termica ADL5535 · 7 novembre 2026','A_Sub'),
 P('<b>Decisione di rilascio:</b> NON APPROVATO PER FABBRICAZIONE. Non generare Gerber, non collegare ad un trasmettitore.','A_Body'),
 P('1. Lavoro effettivamente eseguito','A_H'),
 T([['Parametro','Esito V3.8'],['PCB KiCad','15 componenti, 8 reti; 110 x 62 mm; 4 strati ipotizzati'],['Piste / via','44 segmenti di rame (+1 rispetto alla V3.7), 64 via'],['Connettori SMA','4 footprint candidati con piazzole GND custom sagomate'],['ADL5535','Pad paddle 1,80 x 3,48 mm; pasta ridotta (-0,10 ratio, candidata)'],['Massa termica','Nuova pista GND F.Cu verso via esterno al pad; nessun via nel pad'],['Piani di massa','4 zone definite; <b>0 zone riempite</b>']], [58*mm,118*mm]),
 P('2. Controlli di progetto','A_H'),
 P(f"Verifiche automatiche V3.8: <b>{sum(DAT['checks'].values())}/{len(DAT['checks'])} superate</b>, comprese la compatibilita' tra pin e reti e una prova negativa di cortocircuito. Il modello 2D dei contatti personalizzati restituisce <b>{DAT['audit']['min_2d_inter_net_copper_clearance_mm']:.2f} mm</b> come distanza minima calcolata tra reti diverse; non e' un DRC KiCad.",'A_Body'),
 P('Sono stati rieseguiti anche i test regressivi: V3.7 (17 superati) e V3.6 (18 asserzioni principali e 3 prove negative). Non esistono ancora misure VNA, Gerber o prove termiche alimentate.','A_Body'),
 P('3. Anteprima effettiva della scheda','A_H'),
])
img=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.8/Anteprima_Footprint_Termico_V3.8.png'
story.append(Image(str(img),width=173*mm,height=88*mm))
story.append(P('Figura ricavata dai dati PCB: non e\' un rendering di KiCad, ne\' una verifica 3D.','A_Small'))
story.append(PageBreak())
story.extend([
 P('Geometrie e vincoli meccanici','A_Title'),
 P('4. SMA SMD: confronto con il disegno TE/Linx','A_H'),
 P('Riferimento: CONSMA002-SMD-G, disegno TE Connectivity/Linx Rev. B. L\'impronta consigliata mostra il contatto centrale come land SMD da 2,05 mm e le zone di massa laterali. La nostra V3.8 utilizza quattro pad custom con smussi <b>candidati</b>: costituiscono un miglioramento rispetto a semplici quadrati, ma <b>non dimostrano equivalenza al profilo TE</b>. Verificare anche la corrispondenza del suffisso -G rispetto alla distinta del modulo.','A_Body'),
 T([['Voce','Condizione / cautela'],['Centro RF','Land SMD circolare 2,05 mm; nessun foro introdotto'],['Pad massa','4 pad custom per SMA; geometria da confrontare con CAD certificato'],['Orientamento J101/J103','Porta RF rivolta a sinistra'],['Orientamento J102/J104','Porta RF rivolta a destra (180 gradi)'],['Ingombro longitudinale','Envelope 2D ipotizzato 15,2 mm lato porta; ~7,2 mm di sporgenza su entrambi i bordi'],['F.CrtYd','Esteso nel progetto, ma il montaggio reale resta da verificare']], [59*mm,117*mm]),
 P('5. ADL5535: pad termico e saldatura','A_H'),
 P('Il datasheet Analog Devices Rev. A, Fig. 17, consiglia il collegamento del pad esposto e del pin 2 al piano di massa, con via fra i piani. La V3.8 collega il paddle tramite una breve pista ad un via vicino, <b>fuori dalla zona di pasta</b>. Non e\' stato calcolato il riscaldamento della giunzione.','A_Body'),
 P('La riduzione del solder paste (-0,10) e\' un\'ipotesi che deve essere visualizzata nello stencil esportato da KiCad e validata dall\'assemblatore. I valori di copertura del pad termico suggeriti dalle convenzioni KiCad sono un criterio di screening, non un sostituto del disegno di processo.','A_Body'),
 P('6. Collegamenti e impedenza','A_H'),
 P('Il percorso RF a 50 Ohm dipende dallo stack-up reale di PCBWay, spessore rame, solder mask e discontinuita\' presso gli SMA. I precedenti calcoli di microstrip sono <b>preliminari</b>. La V3.8 non modifica ne\' convalida l\'impedenza controllata.','A_Body'),
 P('Documenti principali: TE CONSMA002-SMD-G, https://www.mouser.com/datasheet/2/418/9/ENG_DS_CONSMA002_SMD_G_B-3238924.pdf ; ADL5535 Rev A, https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf','A_Small'),
])
story.append(PageBreak())
story.extend([
 P('Collaudi aperti e prossima fase','A_Title'),
 P('7. Criteri di accettazione del prototipo','A_H'),
 T([['Blocco da risolvere','Verifica richiesta'],['Footprint SMA','Dimostrare corrispondenza con CAD/land pattern del part number acquistato'],['ADL5535 / termica','Revisione pad, apertura pasta, tenting e massa secondo processo PCBA'],['KiCad nativo','Aprire/salvare PCB in KiCad, riempire zone, eseguire DRC senza violazioni bloccanti'],['Integrita\' fabbricazione','Visualizzare F.Mask/F.Paste, dimensioni, piazzole e assenza di collisioni 3D'],['Stack-up e RF','Accettazione PCBWay della sezione 50 Ohm; eventuale test coupon TDR/VNA'],['Prova a banco','Solo RX, alimentazione limitata, S11/S21, corrente e temperatura']], [62*mm,114*mm]),
 P('8. Riproducibilita\' dei controlli','A_H'),
 P('Dalla radice dello ZIP estratto, eseguire:','A_Body'),
 P('<font face="Courier">python 03_Verifiche/V3.8/build_v38.py</font>','A_Body'),
 P('La verifica nativa, dopo aver installato KiCad 9 o 10, richiede prima un controllo visuale e il refill delle zone; successivamente si puo\' richiamare un comando come:','A_Body'),
 P('<font face="Courier" size="7">kicad-cli pcb drc --severity-all --exit-code-violations -o drc_v38.txt &lt;file.kicad_pcb&gt;</font>','A_Body'),
 P('Questo comando e\' documentato nel progetto come <b>procedura da eseguire</b>, non come test gia\' svolto. Eseguire il DRC sulla PCB, dopo aver controllato la corrispondenza con lo schema e le opzioni di riempimento.','A_Body'),
 P('9. Esito e percentuale','A_H'),
 P('<b>Avanzamento globale stimato: 37%, invariato.</b> Il 63% residuo include il resto della radio, firmware e verifiche hardware. Questa revisione riduce l\'incertezza meccanica e termica, ma non certifica una PCB producibile.','A_Body'),
 P('Prossima revisione V3.9: apertura reale in KiCad, acquisizione di un footprint certificato, controllo dello stencil, refill dei piani e DRC nativo. Solo dopo: prototipo a basso rischio e piano misure VNA.','A_Body'),
 P('Nota di sicurezza: il modulo e\' esclusivamente RX da banco, senza commutazione/protezione TX. Non collegarlo all\'antenna del ricetrasmettitore durante la trasmissione.','A_Small')
])
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(PDF,PDF.stat().st_size)
