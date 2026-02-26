import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import unittest
import os

# ==========================================
# 1. LÓGICA PRINCIPAL DEL PROGRAMA
# ==========================================

def procesar_csv(ruta_csv):
    """Lee el CSV, limpia espacios y ordena alfabéticamente por 'Nombre'."""
    # Leemos el archivo considerando el separador ';'
    df = pd.read_csv(ruta_csv, sep=';', skipinitialspace=True)
    # Limpiamos los nombres de las columnas por si tienen espacios extras
    df.columns = df.columns.str.strip()
    
    # Ordenamos alfabéticamente por la columna 'Nombre'
    df = df.sort_values(by='Nombre').reset_index(drop=True)
    return df

def agrupar_alumnos(df, tamaño_grupo=8):
    """Divide el DataFrame en listas de tamaño 'tamaño_grupo'."""
    return [df.iloc[i:i + tamaño_grupo] for i in range(0, len(df), tamaño_grupo)]

def generar_pdf(grupos, nombre_salida="hoja_de_firmas.pdf"):
    """Genera el PDF con encabezado y tablas con los grupos formados."""
    doc = SimpleDocTemplate(nombre_salida, pagesize=A4)
    elementos = []
    estilos = getSampleStyleSheet()
    
    for i, grupo in enumerate(grupos):
        # 1. Encabezado
        titulo = Paragraph(f"<b>Hoja de Firmas - Grupo {i+1}</b>", estilos['Title'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 20))
        
        # 2. Datos de la tabla (Cabecera + Alumnos)
        datos_tabla = [["Nombre", "Apellidos", "Día 1", "Día 2"]]
        for _, fila in grupo.iterrows():
            datos_tabla.append([fila['Nombre'], fila['Apellido(s)'], "", ""])
            
        # 3. Creación y estilos de la tabla
        # Configuramos anchos de columnas (Nombres y Apellidos más anchos) y altura de las filas (espacio para firmar)
        tabla = Table(datos_tabla, colWidths=[120, 150, 100, 100], rowHeights=40)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ]))
        
        elementos.append(tabla)
        elementos.append(PageBreak()) # Salto de página para el siguiente grupo
        
    doc.build(elementos)


# ==========================================
# 2. TESTS UNITARIOS
# ==========================================

class TestHojaFirmas(unittest.TestCase):
    
    def setUp(self):
        """Prepara un archivo CSV de prueba antes de cada test."""
        self.csv_prueba = "test_data.csv"
        with open(self.csv_prueba, "w", encoding="utf-8") as f:
            f.write("Nombre; Apellido(s)\n")
            f.write("Zubat; Garcia\n")
            f.write("Abra; Perez\n")
            # Añadimos 10 alumnos más
            for i in range(10):
                f.write(f"Pokemon{i}; Apellido{i}\n")
                
    def tearDown(self):
        """Limpia los archivos creados después de cada test."""
        if os.path.exists(self.csv_prueba):
            os.remove(self.csv_prueba)
        if os.path.exists("test_output.pdf"):
            os.remove("test_output.pdf")

    def test_orden_alfabetico(self):
        """Comprueba que los alumnos se ordenan por Nombre alfabéticamente."""
        df = procesar_csv(self.csv_prueba)
        # Abra debería ser el primero y Zubat el último
        self.assertEqual(df.iloc[0]['Nombre'], "Abra")
        self.assertEqual(df.iloc[-1]['Nombre'], "Zubat")
        
    def test_agrupamiento_en_8(self):
        """Comprueba que la lista de alumnos se divide correctamente de 8 en 8."""
        df = procesar_csv(self.csv_prueba)
        grupos = agrupar_alumnos(df, tamaño_grupo=8)
        
        # Hay 12 alumnos en total en el test (Zubat, Abra + 10 extras)
        # Debería haber 2 grupos: uno de 8 y otro de 4.
        self.assertEqual(len(grupos), 2) 
        self.assertEqual(len(grupos[0]), 8)
        self.assertEqual(len(grupos[1]), 4)
        
    def test_generacion_pdf(self):
        """Comprueba que el archivo PDF se genera físicamente en el disco."""
        df = procesar_csv(self.csv_prueba)
        grupos = agrupar_alumnos(df, tamaño_grupo=8)
        generar_pdf(grupos, "test_output.pdf")
        
        self.assertTrue(os.path.exists("test_output.pdf"))


# ==========================================
# 3. EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("Ejecutando tests unitarios...")
    # Ejecutamos los tests (exit=False permite continuar con el script tras los tests)
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\nGenerando hoja de firmas real...")
    # Generación para el CSV real aportado
    try:
        df_real = procesar_csv("pokemons_participantes_curso.csv")
        grupos_reales = agrupar_alumnos(df_real, 8)
        generar_pdf(grupos_reales, "hoja_de_firmas.pdf")
        print("¡El archivo 'hoja_de_firmas.pdf' se ha generado correctamente!")
    except FileNotFoundError:
        print("El archivo 'pokemons_participantes_curso.csv' no se encuentra en el directorio actual.")