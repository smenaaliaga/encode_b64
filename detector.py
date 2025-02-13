#!/usr/bin/env python3
import csv
import sys

def es_entero(valor):
    """
    Verifica si `valor` puede convertirse en un entero (int).
    """
    try:
        int(valor)
        return True
    except ValueError:
        return False

def es_flotante(valor):
    """
    Verifica si `valor` puede convertirse en un número flotante (float).
    """
    try:
        float(valor)
        # Para diferenciar si realmente es entero (aunque esté en float), 
        # podrías comparar float(valor).is_integer(), pero para este caso 
        # nos basta con saber si se puede convertir o no.
        return True
    except ValueError:
        return False

def inferir_tipo_columna(valores):
    """
    Dada una lista de valores (strings), infiere el tipo de dato SQL apropiado.
    - INT si todos son enteros.
    - FLOAT si no todos son enteros pero todos pueden ser float.
    - VARCHAR si alguno no puede ser numérico.
    Adicionalmente, para VARCHAR se calcula el largo máximo para usarlo como VARCHAR(n).
    """
    # Eliminamos valores vacíos o nulos para evitar errores en inferencia
    valores_filtrados = [v for v in valores if v.strip() != ""]
    
    if not valores_filtrados:
        # Si la columna está completamente vacía, le asignamos un VARCHAR(255) por defecto
        return ("VARCHAR", 255)
    
    todos_entero = all(es_entero(v) for v in valores_filtrados)
    if todos_entero:
        return ("INT", None)
    
    todos_flotantes = all(es_flotante(v) for v in valores_filtrados)
    if todos_flotantes:
        # Podríamos asignar un FLOAT o DECIMAL con cierta precisión
        return ("FLOAT", None)
    
    # Si llega aquí, asumimos tipo texto (VARCHAR).
    # Calculamos el largo máximo
    max_len = max(len(v) for v in valores_filtrados)
    # Para evitar definir un VARCHAR(0) cuando la columna esté vacía en todas sus filas,
    # ponemos un mínimo de 1.
    max_len = max(max_len, 1)
    return ("VARCHAR", max_len)

def generar_template_sql(nombre_tabla, headers, tipos_columnas):
    """
    Genera una plantilla de sentencia SQL para crear una tabla a partir de los nombres
    de columnas (`headers`) y sus tipos (`tipos_columnas`).
    """
    columnas_definiciones = []
    for header, (tipo, longitud) in zip(headers, tipos_columnas):
        # Limpieza básica del nombre de la columna
        header_limpio = header.strip().replace(" ", "_")
        
        if tipo == "VARCHAR":
            columnas_definiciones.append(f"`{header_limpio}` VARCHAR({longitud})")
        elif tipo == "INT":
            columnas_definiciones.append(f"`{header_limpio}` INT")
        elif tipo == "FLOAT":
            columnas_definiciones.append(f"`{header_limpio}` FLOAT")
        else:
            # Caso por si hay otro tipo adicional
            columnas_definiciones.append(f"`{header_limpio}` {tipo}")
            
    columnas_str = ",\n  ".join(columnas_definiciones)
    template = f"CREATE TABLE {nombre_tabla} (\n  {columnas_str}\n);"
    return template

def main():
    if len(sys.argv) < 3:
        print("Uso: python detectar_tipo_csv.py <ruta_csv> <separador>")
        sys.exit(1)
    
    ruta_csv = sys.argv[1]
    separador = sys.argv[2]
    
    # Se lee el CSV
    with open(ruta_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=separador)
        
        # Extraemos la cabecera
        headers = next(reader, None)
        if not headers:
            print("El archivo CSV está vacío o no tiene cabecera.")
            sys.exit(1)
        
        # Inicializamos una lista de listas para almacenar los valores de cada columna
        columnas = [[] for _ in headers]
        
        for fila in reader:
            # Aseguramos que la fila tenga la misma cantidad de columnas que la cabecera
            # (en caso de que haya filas incompletas)
            if len(fila) != len(headers):
                # Aquí puedes decidir cómo manejarlo. 
                # Ejemplo: ignorar filas incompletas o completarlas con valores vacíos
                continue
            
            for i, valor in enumerate(fila):
                columnas[i].append(valor)
    
    # Inferir tipos
    tipos_columnas = [inferir_tipo_columna(col) for col in columnas]
    
    # Generar la plantilla SQL (podrías permitir que el usuario pase el nombre de la tabla por argumento)
    nombre_tabla = "nombre_de_tu_tabla"
    sentencia_sql = generar_template_sql(nombre_tabla, headers, tipos_columnas)
    
    print("== Tipos inferidos por columna ==")
    for header, (tipo, longitud) in zip(headers, tipos_columnas):
        if tipo == "VARCHAR":
            print(f"{header}: {tipo}({longitud})")
        else:
            print(f"{header}: {tipo}")
    
    print("\n== Plantilla SQL generada ==")
    print(sentencia_sql)

if __name__ == "__main__":
    main()