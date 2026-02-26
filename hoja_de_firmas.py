import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def process_data(csv_path):
    # Load and clean
    df = pd.read_csv(csv_path, sep=';', skipinitialspace=True)
    df.columns = df.columns.str.strip()
    
    # Sort alphabetically by Nombre
    df = df.sort_values(by='Nombre').reset_index(drop=True)
    return df

def chunk_data(df, chunk_size=8):
    return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

def create_pdf(chunks, output_filename="hoja_de_firmas.pdf"):
    doc = SimpleDocTemplate(output_filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    for i, chunk in enumerate(chunks):
        # Header
        elements.append(Paragraph(f"<b>Hoja de Firmas - Grupo {i+1}</b>", styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Table Data
        data = [["Nombre", "Apellidos", "D’a 1", "D’a 2"]]
        for _, row in chunk.iterrows():
            data.append([row['Nombre'], row['Apellido(s)'], "", ""])
            
        # Table
        t = Table(data, colWidths=[120, 150, 100, 100], rowHeights=40)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t)
        elements.append(PageBreak())
        
    doc.build(elements)

# Execute
df = process_data("pokemons_participantes_curso.csv")
chunks = chunk_data(df, 8)
create_pdf(chunks)
print("PDF created successfully!")