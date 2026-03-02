import pandas as pd
import unittest
import os
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# ==========================================
# 1. LOGICA DEL PROGRAMA
# ==========================================

def dibujar_encabezado(canvas, doc):
    """Dibuja el encabezado (Asignatura, Tema, Semana) en la parte superior."""
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 10)
    
    alto_pag = A4[1]
    margen_izq = 1.5 * cm
    
    # Posicion inicial Y
    y = alto_pag - 1.5 * cm
    
    # Linea 1
    canvas.drawString(margen_izq, y, "Asignatura: _______________________________________")
    canvas.drawString(margen_izq + 11*cm, y, "Semana: _________")
    
    # Linea 2
    y -= 0.8 * cm
    canvas.drawString(margen_izq, y, "Tema: _________________________________________________")
    
    canvas.restoreState()

def procesar_datos(ruta_csv):
    """Lee el CSV, limpia espacios y ordena alfabeticamente por Nombre."""
    try:
        df = pd.read_csv(ruta_csv, sep=';', skipinitialspace=True)
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        if 'Nombre' in df.columns:
            df = df.sort_values(by='Nombre').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"Error al leer el CSV: {e}")
        return pd.DataFrame() # Retorna DF vacio en caso de error

def generar_pdf_una_pagina(df, nombre_salida="Hoja_Firmas.pdf"):
    """Genera el PDF final con diseno de doble columna."""
    if df.empty:
        print("No hay datos para generar el PDF.")
        return

    doc = BaseDocTemplate(nombre_salida, pagesize=A4)
    
    # Margenes optimizados
    margen_lateral = 1 * cm
    margen_inferior = 1 * cm
    margen_superior_contenido = 3.5 * cm 
    
    ancho_pag, alto_pag = A4
    ancho_frame = (ancho_pag - 2*margen_lateral - 0.5*cm) / 2 
    alto_frame = alto_pag - margen_inferior - margen_superior_contenido
    
    # Definir columnas
    frame1 = Frame(margen_lateral, margen_inferior, ancho_frame, alto_frame, id='col1')
    frame2 = Frame(margen_lateral + ancho_frame + 0.5*cm, margen_inferior, ancho_frame, alto_frame, id='col2')
    
    template = PageTemplate(id='CompactHeader', frames=[frame1, frame2], onPage=dibujar_encabezado)
    doc.addPageTemplates([template])
    
    elementos = []
    estilos = getSampleStyleSheet()
    estilo_grupo = ParagraphStyle('GTitle', parent=estilos['Normal'], fontSize=9, spaceAfter=2, fontName='Helvetica-Bold')
    
    # Dividir en grupos de 8
    grupos = [df[i:i+8] for i in range(0, len(df), 8)]
    
    for i, grupo in enumerate(grupos):
        elementos.append(Paragraph(f"Grupo {i+1}", estilo_grupo))
        
        datos_tabla = [["Nombre", "Apellidos", "Dia 1", "Dia 2"]]
        for _, fila in grupo.iterrows():
            # Convertimos a string por seguridad
            n = (str(fila['Nombre'])[:18] + '.') if len(str(fila['Nombre'])) > 18 else str(fila['Nombre'])
            a = (str(fila['Apellido(s)'])[:18] + '.') if len(str(fila['Apellido(s)'])) > 18 else str(fila['Apellido(s)'])
            datos_tabla.append([n, a, "", ""])
            
        anchos = [ancho_frame * 0.33, ancho_frame * 0.33, ancho_frame * 0.17, ancho_frame * 0.17]
        t = Table(datos_tabla, colWidths=anchos, rowHeights=13)
        t.setStyle(TableStyle([
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elementos.append(t)
        elementos.append(Spacer(1, 6))

    doc.build(elementos)

# ==========================================
# 2. CLASE DE TESTS UNITARIOS
# ==========================================

class TestGeneradorFirmas(unittest.TestCase):
    
    def setUp(self):
        """Se ejecuta ANTES de cada test: Crea un entorno de prueba."""
        self.test_csv = "test_data_unit.csv"
        self.test_pdf = "test_output_unit.pdf"
        
        # Crear un CSV falso con algunos nombres desordenados
        with open(self.test_csv, "w", encoding='utf-8') as f:
            f.write("Nombre; Apellido(s)\n")
            f.write("Zacarias; Flores\n")
            f.write("Ana; Gomez\n")
            f.write("Bernardo; Silva\n")
            
    def tearDown(self):
        """Se ejecuta DESPUES de cada test: Limpia los archivos creados."""
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        if os.path.exists(self.test_pdf):
            try:
                os.remove(self.test_pdf)
            except PermissionError:
                pass # A veces el archivo sigue abierto por el sistema

    def test_ordenamiento_alfabetico(self):
        """Verifica que procesar_datos ordena por Nombre."""
        df = procesar_datos(self.test_csv)
        nombres = df['Nombre'].tolist()
        
        # 'Ana' debe ser la primera, 'Zacarias' el ultimo
        self.assertEqual(nombres[0], "Ana")
        self.assertEqual(nombres[-1], "Zacarias")
        
    def test_generacion_archivo_pdf(self):
        """Verifica que la funcion crea fisicamente un archivo PDF valido."""
        df = procesar_datos(self.test_csv)
        generar_pdf_una_pagina(df, self.test_pdf)
        
        # Comprobar existencia
        self.assertTrue(os.path.exists(self.test_pdf))
        # Comprobar que no es un archivo vacio
        self.assertGreater(os.path.getsize(self.test_pdf), 0)

# ==========================================
# 3. EJECUCION
# ==========================================

if __name__ == '__main__':
    # 1. Ejecutar los tests
    print("Iniciando Tests Unitarios...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\nTests finalizados.")
    
    # 2. Ejecucion real (Asegurate que el nombre del CSV es correcto)
    archivo_real = "pokemons_participantes_curso.csv" # <--- REVISA QUE ESTE NOMBRE SEA EL DE TU ARCHIVO
    if os.path.exists(archivo_real):
        print(f"\nGenerando PDF real desde {archivo_real}...")
        df = procesar_datos(archivo_real)
        generar_pdf_una_pagina(df, "Hoja_Firmas_Final.pdf")
        print("PDF generado!")
    else:
        print(f"\nNo se encontro el archivo '{archivo_real}' para generar el PDF final.")