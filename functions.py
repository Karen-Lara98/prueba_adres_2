# Description: Funciones para extraer información de archivos PDF y almacenarla en una base de datos SQLite

# Importar módulos necesarios
import os
import re
import sqlite3
import fitz  # PyMuPDF para leer PDFs
from sqlite3 import Error

############################################################################################
# Expresión regular para el CUFE (Esta me la dieron en la prueba)
CUFE_REGEX = r"\b([0-9a-fA-F]\n*){95,100}\b"
############################################################################################

############################################################################################
"""
Ruta al directorio que contiene los archivos PDF
"""
# Variable base para obtener la ruta absoluta del directorio actual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ruta al directorio que contiene los archivos PDF
pdf_directory = os.path.join(BASE_DIR, "pdf_sample")
############################################################################################

############################################################################################
# Función para crear una conexión a la base de datos SQLite
def create_connection(db_file):
    """
    Crea una conexión a la base de datos SQLite.
    """
    # Si el archivo de la base de datos no existe, se creará automáticamente
    try:
        # Crear la conexión a la base de datos
        conn = sqlite3.connect(db_file)
        return conn
    # Manejar errores al crear la conexión
    except Error as e:
        print(e)
        
    # Retornar None si no se pudo crear la conexión
    return None
############################################################################################

############################################################################################
# Función para crear la tabla facturas si no existe
def create_table(conn):
    """
    Crea la tabla facturas si no existe.
    """
    
    # Sentencia SQL para crear la tabla facturas
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS facturas (
        nombre_archivo TEXT PRIMARY KEY,
        numero_paginas INTEGER,
        cufe TEXT,
        peso INTEGER
    );
    """
    
    # Crear la tabla facturas
    try:
        # Crear un cursor y ejecutar la sentencia SQL
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    # Manejar errores al crear la tabla
    except Error as e:
        print(e)
############################################################################################

############################################################################################
# Función para extraer información de un archivo PDF
def extract_pdf_info(file_path):
    """
    Documentación de la función extract_pdf_info
    Extrae información del PDF:
       - Nombre del archivo
       - Número de páginas
       - CUFE
       - Peso del archivo en bytes

    Validaciones añadidas:
    1. Verifica que el archivo tenga la extensión .pdf
    2. Verifica que el archivo contenga la firma PDF (%PDF-)
    """

    # Obtener el nombre del archivo y el tamaño
    file_name = os.path.basename(file_path) # Nombre del archivo
    file_size = os.path.getsize(file_path) # Tamaño del archivo en bytes

    # Validar que el archivo tenga extensión .pdf
    if not file_path.lower().endswith('.pdf'):
        # Mostrar un mensaje si el archivo no es un PDF
        print(f"El archivo {file_name} no tiene extensión PDF.")
        # Retornar información vacía
        return file_name, 0, None, file_size

    # Validar la firma del archivo (cabecera PDF)
    try:
        # Leer los primeros 5 bytes del archivo
        with open(file_path, 'rb') as f:
            # 5 bytes del archivo
            header = f.read(5)
            
        # Verificar si el archivo tiene la firma PDF correcta
        if header != b'%PDF-':
            # Mostrar un mensaje si el archivo no tiene la firma PDF correcta
            print(f"El archivo {file_name} no tiene la firma PDF correcta. No es un PDF válido.")
            # Retornar información vacía
            return file_name, 0, None, file_size
    # Manejar errores al leer el archivo
    except Exception as e:
        # Mostrar un mensaje si hay un error al leer el archivo
        print(f"Error al leer el archivo {file_name}: {e}")
        # Retornar información vacía
        return file_name, 0, None, file_size

    # Inicializar las variables
    try:
        # Abrir el archivo PDF con PyMuPDF
        with fitz.open(file_path) as pdf:
            # Obtener el número de páginas del PDF
            num_pages = pdf.page_count
            # Inicializar el CUFE en None o vacío
            cufe = None
            # Buscar el CUFE en cada página del PDF
            for page_num in range(num_pages):
                # Obtener el texto de la página
                page = pdf[page_num]
                # Extraer el texto de la página
                text = page.get_text("text")
                # Buscar el CUFE en el texto de la página
                match = re.search(CUFE_REGEX, text)
                # Si se encuentra el CUFE, se almacena y se sale del bucle
                if match:
                    # Almacenar el CUFE encontrado
                    cufe = match.group(0).replace("\n", "")
                    # Sale del bucle
                    break
                
    # Manejar errores al abrir o procesar el archivo
    except Exception as e:
        # Mostrar un mensaje si hay un error al procesar el archivo
        print(f"Error al procesar el archivo {file_name}: {e}")
        # Retornar información vacía
        return file_name, 0, None, file_size

    # Retornar la información extraída
    return file_name, num_pages, cufe, file_size
############################################################################################

############################################################################################
# Función para insertar o actualizar los datos de una factura en la base de datos
def upsert_factura(conn, factura_data):
    """
    Inserta o actualiza los datos de una factura en la base de datos.
    """
    
    # Sentencia SQL para insertar o actualizar los datos de la factura
    sql = """
    INSERT OR REPLACE INTO facturas (nombre_archivo, numero_paginas, cufe, peso)
    VALUES (?, ?, ?, ?)
    """
    # Se intenta insertar o actualizar los datos de la factura
    try:
        # Crear un cursor y ejecutar la sentencia SQL
        c = conn.cursor()
        c.execute(sql, factura_data)
    
    # Manejar errores al insertar o actualizar los datos
    except Error as e:
        print(f"Error al insertar/actualizar {factura_data[0]}: {e}")
############################################################################################