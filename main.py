# Description: Este script permite extraer información de archivos PDF y almacenarla en una base de datos SQLite.

#####################################################################################################################
# Importar módulos necesarios
import os
#####################################################################################################################

#####################################################################################################################
# Importar funciones y variables del archivo functions.py
from functions import CUFE_REGEX, pdf_directory, create_connection, create_table, upsert_factura, extract_pdf_info
#####################################################################################################################

#####################################################################################################################
# Función principal
def main():
    # Crear una conexión a la base de datos
    conn = create_connection("facturas.db")
    # Verificar si se pudo establecer la conexión
    if conn is None:
        # Mostrar un mensaje si no se pudo establecer la conexión
        print("No se pudo establecer conexión con la base de datos.")
        return

    # Crear la tabla facturas si no existe
    create_table(conn)

    # Obtener la lista de archivos PDF en la carpeta
    pdf_files = [file for file in os.listdir(pdf_directory) if file.lower().endswith('.pdf')]
    num_files = len(pdf_files)
    # Mostrar un mensaje con la cantidad de archivos PDF encontrados
    print(f"Se encontraron {num_files} archivos PDF en la carpeta.\n")

    # Iterar sobre los archivos PDF
    for file_name in pdf_files:
        # Obtener la ruta completa del archivo
        pdf_path = os.path.join(pdf_directory, file_name)
        # Extraer información del archivo
        file_name, num_pages, cufe, file_size = extract_pdf_info(pdf_path)

        # Verificar si los datos ya existen
        c = conn.cursor()
        # Buscar los datos en la base de datos
        c.execute("SELECT * FROM facturas WHERE nombre_archivo = ?", (file_name,))
        # Obtener los datos existentes
        existing_data = c.fetchone()

        # Preguntar al usuario si desea sobrescribir los datos
        if existing_data:
            # Mostrar un mensaje si los datos ya existen
            confirm = input(f"Los datos para '{file_name}' ya existen. ¿Deseas sobrescribirlos? (s/n): ")
            # Continuar con el siguiente archivo si el usuario no confirma
            if confirm.lower() != 's':
                # Mostrar un mensaje si no se modificará la entrada
                print(f"No se modificará la entrada para {file_name}.\n")
                # Continuar con el siguiente archivo
                continue
            
        # Insertar o actualizar los datos en la base de datos
        if cufe is not None:
            # Mostrar los datos extraídos del archivo
            print(f"Nombre del archivo: {file_name}")
            print(f"Número de páginas: {num_pages}")
            print(f"CUFE encontrado: {cufe}")
            print(f"Peso del archivo: {file_size} bytes\n")
            # Insertar o actualizar los datos en la base de datos
            upsert_factura(conn, (file_name, num_pages, cufe, file_size))
            # Confirmar los cambios
            conn.commit()
            # Mostrar un mensaje si los datos se insertaron correctamente
            print(f"Datos insertados/actualizados correctamente en la base de datos.")
        else:
            # Mostrar un mensaje si no se encontró un CUFE
            print(f"No se encontró un CUFE en el archivo: {file_name}")
            
    # Cerrar la conexión a la base de datos
    conn.close()
    
    # Mostrar un mensaje al finalizar el proceso
    print("Proceso completado. Los datos han sido almacenados en la base de datos SQLite.")
#####################################################################################################################

#####################################################################################################################
# Ejecutar la función principal si se ejecuta este script
if __name__ == '__main__':
    main()
#####################################################################################################################