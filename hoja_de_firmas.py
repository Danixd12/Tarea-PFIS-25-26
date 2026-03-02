import pandas as pd
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# ==========================================
# 1. FUNCIÓN DE DIBUJADO (ENCABEZADO)
# ==========================================
def dibujar_encabezado(canvas, doc):
    """Dibuja el encabezado aprovechando el espacio superior."""
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 10)
    
    # Coordenadas desde esquina inferior izquierda (0,0)
    alto_pag = A4[1]
    margen_izq = 1.5 * cm
    
    # Posición inicial Y (cerca del borde superior)
    y = alto_pag - 1.5 * cm
    
    # Línea 1: Asignatura y Semana en la misma altura para ahorrar espacio
    canvas.drawString(margen_izq, y, "Asignatura: _______________________________________")
    canvas.drawString(margen_izq + 11*cm, y, "Semana: _________")
    
    # Línea 2: Tema debajo
    y -= 0.8 * cm
    canvas.drawString(margen_izq, y, "Tema: _________________________________________________")
    
    canvas.restoreState()

# ==========================================
# 2. PROCESAMIENTO Y GENERACIÓN
# ==========================================
def procesar_datos(ruta_csv):
    """Lee y ordena alfabéticamente el CSV."""
    df = pd.read_csv(ruta_csv, sep=';', skipinitialspace=True)
    df.columns = df.columns.str.strip()
    if 'Nombre' in df.columns:
        df = df.sort_values(by='Nombre').reset_index(drop=True)
    return df

def generar_pdf_una_pagina(df, nombre_salida="Hoja_Firmas_1Pagina_Final.pdf"):
    doc = BaseDocTemplate(nombre_salida, pagesize=A4)
    
    # Márgenes ajustados para maximizar el área útil
    margen_lateral = 1 * cm
    margen_inferior = 1 * cm
    # Reservamos solo 3.5cm arriba para el encabezado
    margen_superior_contenido = 3.5 * cm 
    
    ancho_pag, alto_pag = A4
    # Calculamos ancho de columna
    ancho_frame = (ancho_pag - 2*margen_lateral - 0.5*cm) / 2 # 0.5cm de hueco entre columnas
    alto_frame = alto_pag - margen_inferior - margen_superior_contenido
    
    # Definimos las 2 columnas (Frames)
    frame1 = Frame(margen_lateral, margen_inferior, ancho_frame, alto_frame, id='col1')
    frame2 = Frame(margen_lateral + ancho_frame + 0.5*cm, margen_inferior, ancho_frame, alto_frame, id='col2')
    
    # Asignamos la plantilla con el encabezado personalizado
    template = PageTemplate(id='CompactHeader', frames=[frame1, frame2], onPage=dibujar_encabezado)
    doc.addPageTemplates([template])
    
    elementos = []
    estilos = getSampleStyleSheet()
    # Estilo de título de grupo minimalista
    estilo_grupo = ParagraphStyle('GTitle', parent=estilos['Normal'], fontSize=9, spaceAfter=2, fontName='Helvetica-Bold')
    
    # Dividir en grupos de 8
    grupos = [df[i:i+8] for i in range(0, len(df), 8)]
    
    for i, grupo in enumerate(grupos):
        elementos.append(Paragraph(f"Grupo {i+1}", estilo_grupo))
        
        datos_tabla = [["Nombre", "Apellidos", "Día 1", "Día 2"]]
        for _, fila in grupo.iterrows():
            # Truncamos texto largo para evitar saltos de línea
            n = (fila['Nombre'][:18] + '.') if len(fila['Nombre']) > 18 else fila['Nombre']
            a = (fila['Apellido(s)'][:18] + '.') if len(fila['Apellido(s)']) > 18 else fila['Apellido(s)']
            datos_tabla.append([n, a, "", ""])
            
        # Anchos de columna optimizados
        anchos = [ancho_frame * 0.33, ancho_frame * 0.33, ancho_frame * 0.17, ancho_frame * 0.17]
        
        # Tabla compacta: altura de fila 13pt (aprox 4.5mm)
        t = Table(datos_tabla, colWidths=anchos, rowHeights=13)
        t.setStyle(TableStyle([
            ('FONTSIZE', (0,0), (-1,-1), 7),      # Fuente 7pt
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('LEFTPADDING', (0,0), (-1,-1), 1),   # Padding mínimo
            ('RIGHTPADDING', (0,0), (-1,-1), 1),
        ]))
        elementos.append(t)
        elementos.append(Spacer(1, 6)) # Separación entre tablas

    doc.build(elementos)

if __name__ == "__main__":
    df = procesar_datos("pokemons_participantes_curso(1).csv")
    generar_pdf_una_pagina(df)
    print("¡PDF generado en una sola página!")