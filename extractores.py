"""
Módulo principal para extracción de datos de facturas en formato PDF y CSV.
Este módulo coordina las funciones de los módulos especializados.
"""

import re

# Importar funciones de los módulos especializados
from extractores_patrones import (
    PATRONES_CONCEPTO, 
    PATRONES_PARAMETROS_ESPECIFICOS
)
from extractores_pdf import (
    convertir_pdf_a_csv,
    procesar_texto,
    extraer_datos_estructurados,
    analizar_estructura_columnas
)
from extractores_componentes import (
    extraer_tabla_componentes,
    leer_archivo
)


def extraer_valores_hes(content):
    """
    Extrae los valores HES del contenido, asegurando que solo se extraigan valores numéricos.
    
    Args:
        content (str): Contenido del archivo CSV
        
    Returns:
        dict: Diccionario con los valores HES extraídos (solo números)
    """
    # Inicializar diccionario con valores vacíos para todas las autorizaciones
    results = {
        'hes1': "0", 'hes2': "0", 'hes3': "0", 'hes4': "0", 'hes5': "0",
        'hes6': "0", 'hes7': "0", 'hes8': "0", 'hes9': "0", 'hes10': "0"
    }
    
    # Patrones para cada HES (1-10)
    for i in range(1, 11):
        # Crear varios patrones para cada HES
        patrones = [
            rf'HES{i}:[\t\s]*(\d+)',             # Formato básico: HES1: 12345
            rf'HES{i}[\t\s]*:[\t\s]*(\d+)',      # Variante con espacios
            rf'HES[\t\s,]+{i}[\t\s,]*:[\t\s]*(\d+)'  # Formato con separación: HES, 10, : 12345
        ]
        
        # Intentar los patrones para este HES
        for patron in patrones:
            match = re.search(patron, content)
            if match:
                # Extraer solo el valor numérico
                value = match.group(1).strip()
                # Verificar que sea numérico
                if value.isdigit():
                    results[f'hes{i}'] = value
                    break  # Si encontramos un valor numérico, podemos parar
    
    return results


def extraer_parametros_especificos(content):
    """
    Extrae los parámetros específicos como IR, Grupo, DIU INT, etc.
    
    Args:
        content (str): Contenido del archivo CSV
        
    Returns:
        dict: Diccionario con los parámetros específicos extraídos
    """
    # Inicializar diccionario con valores por defecto (todos numéricos)
    parametros = {
        'ir': "0",
        'grupo': "0",
        'diu_int': "0",
        'dium_int': "0",
        'fiu_int': "0",
        'fium_int': "0",
        'fiug': "0",
        'diug': "0"
    }
    
    # Buscar los patrones completos primero para FIUG y DIUG que son los más confiables
    patron_fiug_diug = r'FIUG:\s*([\d.]+),\s*DIUG:\s*([\d.]+)'
    match = re.search(patron_fiug_diug, content)
    if match:
        parametros['fiug'] = match.group(1)
        parametros['diug'] = match.group(2)
    
    # Buscar el grupo
    patron_grupo = r'Grupo:\s*(\d+)'
    match = re.search(patron_grupo, content)
    if match:
        parametros['grupo'] = match.group(1)
    
    # Buscar los valores INT que son numéricos - sólo buscar dígitos
    for key in ['diu_int', 'dium_int', 'fiu_int', 'fium_int']:
        for patron in PATRONES_PARAMETROS_ESPECIFICOS[key]:
            match = re.search(patron, content)
            if match and match.group(1).isdigit():
                parametros[key] = match.group(1)
                break
    
    # IR es un caso especial - debe ser un número
    patron_ir_especifico = r'IR:\s*(\d+)'
    match = re.search(patron_ir_especifico, content)
    if match and match.group(1).isdigit():
        parametros['ir'] = match.group(1)
    
    return parametros


def extraer_datos_factura(file_path):
    """
    Extrae los datos generales de la factura desde un archivo CSV.
    
    Args:
        file_path (str): Ruta al archivo CSV de la factura
        
    Returns:
        dict: Diccionario con los datos extraídos de la factura
    """
    content = leer_archivo(file_path)
    
    # Extraer información principal
    fecha_vencimiento_match = re.search(r'Fecha\s+vencimiento:\s+(\d{4}-\d{2}-\d{2})', content)
    fecha_vencimiento = fecha_vencimiento_match.group(1) if fecha_vencimiento_match else "No encontrado"
    
    periodo_facturacion_match = re.search(r'Período\s+Facturación:\s+(\d{4}-\d{2}-\d{2}).*?(\d{4}-\d{2}-\d{2})', content)
    if periodo_facturacion_match:
        periodo_facturacion = f"{periodo_facturacion_match.group(1)} a {periodo_facturacion_match.group(2)}"
    else:
        # Try alternative format
        alt_match = re.search(r'Período\s+Facturación:\s+(\d{4}-\d{2}-\d{2})', content)
        periodo_facturacion = alt_match.group(1) if alt_match else "No encontrado"
    
    factor_m_match = re.search(r'Factor\s+M:\s+(\d+)', content)
    factor_m = factor_m_match.group(1) if factor_m_match else "No encontrado"
    
    # Extraer código SIC
    codigo_sic_match = re.search(r'Código\s+SIC:.*?([A-Za-z]+)[,\s]*(\d+)', content)
    if codigo_sic_match:
        # Concatenar el prefijo de letras y los números
        prefijo = codigo_sic_match.group(1)
        numeros = codigo_sic_match.group(2)
        codigo_sic = f"{prefijo}{numeros}"
    else:
        codigo_sic = "No encontrado"
    
    # Extraer número de factura
    numero_factura_patrones = [
        r'FACTURA\s+ELECTR[ÓO]NICA\s+DE\s+VENTA\s+SERVICIO\s+P[ÚU]BLICO:.*?No\.\s+([A-Za-z0-9]+)',
        r'FACTURA\s+ELECTR[ÓO]NICA\s+DE\s+VENTA\s+SERVICIO\s+P[ÚU]BLICO:,No\.\s+([A-Za-z0-9]+)',
        r'No\.\s+([A-Za-z0-9]+)'
    ]
    
    numero_factura = "No encontrado"
    for patron in numero_factura_patrones:
        match = re.search(patron, content, re.IGNORECASE)
        if match:
            numero_factura = match.group(1)
            break
    
    # Initialize results dictionary with the main variables
    results = {
        "fecha_vencimiento": fecha_vencimiento,
        "periodo_facturacion": periodo_facturacion,
        "factor_m": factor_m,
        "codigo_sic": codigo_sic,
        "numero_factura": numero_factura,
    }
    
    # Extract all the financial variables
    for var_name, patterns in PATRONES_CONCEPTO.items():
        # Skip subtotal_energia_contribucion_pesos since it will be calculated later
        if var_name == "subtotal_energia_contribucion_pesos":
            continue
        
        value = "No encontrado"
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                # Clean the captured value
                captured_value = match.group(1)
                # Remove commas at the beginning of the value
                if captured_value.startswith(','):
                    captured_value = captured_value[1:]
                value = captured_value
                break
        results[var_name] = value
    
    # Calcular subtotal_energia_contribucion_pesos como la suma de subtotal_base_energia y contribucion
    try:
        # Convertir valores a números, eliminando las comas
        subtotal_base = int(results["subtotal_base_energia"].replace(',', '')) if results["subtotal_base_energia"] != "No encontrado" else 0
        contribucion = int(results["contribucion"].replace(',', '')) if results["contribucion"] != "No encontrado" else 0
        
        # Calcular la suma
        subtotal_energia_contribucion_pesos = subtotal_base + contribucion
        
        # Formatear el resultado con comas para miles
        results["subtotal_energia_contribucion_pesos"] = f"{subtotal_energia_contribucion_pesos:,}"
    except (ValueError, KeyError):
        # En caso de error, establecer un valor por defecto
        results["subtotal_energia_contribucion_pesos"] = "No encontrado"
    
    # Extraer valores HES (autorizaciones)
    hes_values = extraer_valores_hes(content)
    results.update(hes_values)
    
    # Extraer parámetros específicos (IR, Grupo, DIU INT, etc.)
    parametros_especificos = extraer_parametros_especificos(content)
    results.update(parametros_especificos)
    
    return results


def extraer_todos_datos_factura(file_path):
    """
    Extrae todos los datos de la factura, combinando datos generales y tabla de componentes.
    
    Args:
        file_path (str): Ruta al archivo CSV de la factura
        
    Returns:
        tuple: Tupla con (datos_generales, datos_componentes)
    """
    datos_generales = extraer_datos_factura(file_path)
    datos_componentes = extraer_tabla_componentes(file_path)
    
    return datos_generales, datos_componentes


# Re-exportar las funciones que antes estaban en este archivo
# para mantener compatibilidad con el resto del código
__all__ = [
    'convertir_pdf_a_csv',
    'procesar_texto',
    'extraer_datos_estructurados',
    'analizar_estructura_columnas',
    'leer_archivo',
    'extraer_valores_hes',
    'extraer_parametros_especificos',
    'extraer_datos_factura',
    'extraer_tabla_componentes',
    'extraer_todos_datos_factura'
]