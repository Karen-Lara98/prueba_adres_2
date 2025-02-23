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
    Extrae información del PDF:
       - Nombre del archivo
       - Número de páginas
       - CUFE
       - Peso del archivo en bytes
    """
    # Obtener el nombre del archivo y el tamaño
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    # Inicializar las variables
    try:
        with fitz.open(file_path) as pdf:
            # Obtener el número de páginas del PDF
            num_pages = pdf.page_count
            # Inicializar el CUFE en None o vacío
            cufe = None
            # Buscar el CUFE en cada página del PDF
            for page_num in range(num_pages):
                page = pdf[page_num]
                text = page.get_text("text")
                match = re.search(CUFE_REGEX, text)
                # Si se encuentra el CUFE, se almacena y se sale del bucle
                if match:
                    cufe = match.group(0).replace("\n", "")
                    break
    # Manejar errores al abrir el archivo
    except Exception as e:
        print(f"Error al procesar el archivo {file_name}: {e}")
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