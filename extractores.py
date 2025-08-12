"""
Módulo para extracción de datos de facturas en formato PDF y CSV.
Este módulo contiene funciones para convertir archivos PDF a CSV y
extraer información estructurada de las facturas.
"""

import os
import re
import csv
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser

# Patrones regex centralizados para extracción de datos
PATRONES_CONCEPTO = {
    'subtotal_base_energia': [
        r'Subtotal base energía.*?"([-\d,]+)"', 
        r'Subtotal\tbase\tenergía.*?"([-\d,]+)"',
        r'Subtotal base energía.*?(?<!")(\d+)(?!")',
        r'Subtotal\tbase\tenergía.*?(?<!")(\d+)(?!")'
    ],
    'contribucion': [
        r'Contribución.*?"([-\d,]+)"',
        r'Contribución.*?(?<!")(\d+)(?!")'
    ],
    'contribucion_otros_meses': [
        r'Contribución de otros meses.*?([-\d,]+)', 
        r'Contribución\tde\totros\tmeses.*?([-\d,]+)',
        r'Contribución de otros meses.*?(?<!")(\d+)(?!")',
        r'Contribución\tde\totros\tmeses.*?(?<!")(\d+)(?!")'
    ],
    'subtotal_energia_contribucion_kwh': [
        r'\$\/kWh,\$\s*Subtotal\s*energia\s*\+\s*contribución,\s*([-\d.,]+)', 
        r'\$\/kWh,\$\s*Subtotal\tenerg[ií]a\t\+\tcontribución,\s*([-\d.,]+)'
    ],
    'subtotal_energia_contribucion_pesos': [
        r'\$\/kWh,\$\s*Subtotal\s*energia\s*\+\s*contribución,\s*[-\d.,]+,\s*"([-\d,]+)"', 
        r'\$\/kWh,\$\s*Subtotal\tenerg[ií]a\t\+\tcontribución,\s*[-\d.,]+,\s*"([-\d,]+)"',
        r'\$\/kWh,\$\s*Subtotal\s*energia\s*\+\s*contribución,\s*[-\d.,]+,\s*(?<!")(\d+)(?!")',
        r'\$\/kWh,\$\s*Subtotal\tenerg[ií]a\t\+\tcontribución,\s*[-\d.,]+,\s*(?<!")(\d+)(?!")'
    ],
    'otros_cobros': [
        r'Otros cobros.*?"([-\d,]+)"', 
        r'Otros\tcobros.*?"([-\d,]+)"',
        r'Otros cobros.*?(?<!")(\d+)(?!")', 
        r'Otros\tcobros.*?(?<!")(\d+)(?!")'
    ],
    'sobretasa': [
       r'Sobretasa.*?([-\d,]+)',
        r'Sobretasa.*?(?<!")(\d+)(?!")' 
    ],
    'ajustes_cargos_regulados': [
        r'Ajustes cargos regulados.*?"([-\d,]+)"', 
        r'Ajustes\tcargos\tregulados.*?"([-\d,]+)"',
        r'Ajustes cargos regulados.*?(?<!")(\d+)(?!")',
        r'Ajustes\tcargos\tregulados.*?(?<!")(\d+)(?!")'
    ],
    'compensaciones': [
        r'Compensaciones.*?"([-\d,]+)"',
        r'Compensaciones.*?(?<!")(\d+)(?!")'
    ],
    'saldo_cartera': [
        r'Saldo cartera.*?"([-\d,]+)"', 
        r'Saldo\tcartera.*?([-\d,]+)',
        r'Saldo cartera.*?(?<!")(\d+)(?!")',
        r'Saldo\tcartera.*?(?<!")(\d+)(?!")'
    ],
    'interes_mora': [
        r'Interés por Mora.*?"([-\d,]+)"', 
        r'Interés\tpor\tMora.*?"([-\d,]+)"',
        r'Interés por Mora.*?(?<!")(\d+)(?!")',
        r'Interés\tpor\tMora.*?(?<!")(\d+)(?!")'
    ],
    'recobros': [
        r'Recobros.*?([-\d,]+)',
        r'Recobros.*?(?<!")(\d+)(?!")' 
    ],
    'alumbrado_publico': [
        r'Alumbrado público.*?([-\d,]+)', 
        r'Alumbrado\tpúblico.*?"([-\d,]+)"',
        r'Alumbrado público.*?(?<!")(\d+)(?!")', 
        r'Alumbrado\tpúblico.*?(?<!")(\d+)(?!")'
    ],
    'impuesto_alumbrado_publico': [
        r'Impuesto alumbrado público.*?([-\d,]+)', 
        r'Impuesto\talumbrado\tpúblico.*?"([-\d,]+)"',
        r'Impuesto alumbrado público.*?(?<!")(\d+)(?!")',
        r'Impuesto\talumbrado\tpúblico.*?(?<!")(\d+)(?!")'
    ],
    'ajuste_iap_otros_meses': [
        r'Ajuste IAP otros meses.*?([-\d,]+)', 
        r'Ajuste\tIAP\totros\tmeses.*?"([-\d,]+)"',
        r'Ajuste IAP otros meses.*?(?<!")(\d+)(?!")',
        r'Ajuste\tIAP\totros\tmeses.*?(?<!")(\d+)(?!")'
    ],
    'convivencia_ciudadana': [
        r'Convivencia ciudadana.*?"([-\d,]+)"', 
        r'Convivencia\tciudadana.*?"([-\d,]+)"',
        r'Convivencia ciudadana.*?(?<!")(\d+)(?!")',
        r'Convivencia\tciudadana.*?(?<!")(\d+)(?!")'
    ],
    'tasa_especial_convivencia': [
        r'Tasa especial convivencia ciudadana.*?"([-\d,]+)"', 
        r'Tasa\tespecial\tconvivencia\tciudadana.*?"([-\d,]+)"',
        r'Tasa especial convivencia ciudadana.*?(?<!")(\d+)(?!")',
        r'Tasa\tespecial\tconvivencia\tciudadana.*?(?<!")(\d+)(?!")'
    ],
    'ajuste_tasa_convivencia': [
        r'Ajuste tasa convivencia otros meses.*?"([-\d,]+)"', 
        r'Ajuste\ttasa\tconvivencia\totros\tmeses.*?"([-\d,]+)"',
        r'Ajuste tasa convivencia otros meses.*?(?<!")(\d+)(?!")',
        r'Ajuste\ttasa\tconvivencia\totros\tmeses.*?(?<!")(\d+)(?!")'
    ],
    'total_servicio_energia_impuestos': [
        r'Total servicio energía \+ impuestos.*?"([-\d,]+)"', 
        r'Total\tservicio\tenergía\t\+\timpuestos.*?"([-\d,]+)"', 
        r'Total\tservicio\tenergía\t\\\+\timpuestos.*?"([-\d,]+)"',
        r'Total servicio energía \+ impuestos.*?(?<!")(\d+)(?!")',
        r'Total\tservicio\tenergía\t\+\timpuestos.*?(?<!")(\d+)(?!")',
        r'Total\tservicio\tenergía\t\\\+\timpuestos.*?(?<!")(\d+)(?!")'
    ],
    'ajuste_decena': [
        r'Ajuste a la decena.*?([-\d,]+)', 
        r'Ajuste\ta\tla\tdecena.*?([-\d,]+)',
        r'Ajuste a la decena.*?(?<!")(\d+)(?!")',
        r'Ajuste\ta\tla\tdecena.*?(?<!")(\d+)(?!")'
    ],
    'neto_pagar': [
        r'Neto a pagar.*?"([-\d,]+)"', 
        r'Neto\ta\tpagar.*?"([-\d,]+)"',
        r'Neto a pagar.*?(?<!")(\d+)(?!")',
        r'Neto\ta\tpagar.*?(?<!")(\d+)(?!")'
    ],
    'energia_reactiva_inductiva': [
        r'Energía\s*reactiva\s*inductiva,\s*([-\d,]+)', 
        r'Energía\treactiva\tinductiva,\s*"([-\d,]+)"',
        r'Energía\s*reactiva\s*inductiva,\s*(?<!")(\d+)(?!")',
        r'Energía\treactiva\tinductiva,\s*(?<!")(\d+)(?!")'
    ],
    'energia_reactiva_capacitiva': [
        r'Energía\s*reactiva\s*capacitiva,\s*([-\d,]+)', 
        r'Energía\treactiva\tcapacitiva,\s*"([-\d,]+)"',
        r'Energía\s*reactiva\s*capacitiva,\s*(?<!")(\d+)(?!")',
        r'Energía\treactiva\tcapacitiva,\s*(?<!")(\d+)(?!")'
    ],
    'total_energia_reactiva': [
        r'Total\s*energía\s*reactiva,\s*([-\d,]+)', 
        r'Total\tenergía\treactiva,\s*"([-\d,]+)"',
        r'Total\s*energía\s*reactiva,\s*(?<!")(\d+)(?!")',
        r'Total\tenergía\treactiva,\s*(?<!")(\d+)(?!")'
    ]
}

# patrón que reconoce valores con y sin comillas
COMPONENTES_ENERGIA = [
    {
        "name": "Generación",
        "pattern": r'1\.\s+Generación,"?([-\d,]+)"?,([-\d\.]+),"?([-\d,]+)"?,"?([-\d,]+)"?,"?([-\d,]+)"?'
    },
    {
        "name": "Comercialización",
        "pattern": r'2\.\s+Comercialización,([-\d\.]+),"?([-\d,]+)"?,"?([-\d,]+)"?,"?([-\d,]+)"?'
    },
    {
        "name": "Transmisión",
        "pattern": r'3\.\s+Transmisión,([-\d\.]+),"?([-\d,]+)"?,"?([-\d,]+)"?,"?([-\d,]+)"?'
    },
    {
        "name": "Distribución",
        "pattern": r'4\.\s+Distribución,([-\d\.]+),"?([-\d,]+)"?,"?([-\d,]+)"?,"?([-\d,]+)"?'
    },
    {
        "name": "Pérdidas",
        "pattern": r'5\.\s+Perdidas\s+\(\*\),([-\d\.]+),"?([-\d,]+)"?,"?([-\d,]+)"?,"?([-\d,]+)"?'
    },
    {
        "name": "Restricciones",
        "pattern": r'6\.\s+Restricciones,([-\d\.]+),"?([-\d,]+)"?,"?([-\d,]+)"?,"?([-\d,]+)"?'
    },
    {
        "name": "Otros cargos",
        "pattern": r'7\.\s+Otros\s+cargos,([-\d\.]+),"?([-\d,]+)"?,"?([-\d,]+)"?,"?([-\d,]+)"?'
    },
    {
        "name": "Energía inductiva + capacitiva",
        "pattern": r'8\.\s+Energ[ií]a\s+inductiva\s+\+\s+capacitiva\s+facturada,\s*([-\d,.]*),\s*([-\d,.]+),\s*"?([-\d,.]*)"?,\s*"?([-\d,.]+)"?,\s*"?([-\d,.]+)"?'
    }
]
# patrones para extraer los parámetros específicos datos OR
PATRONES_PARAMETROS_ESPECIFICOS = {
    'ir': [r'IR:\s*(?:,|\s+)([^,\s]+)', r'IR:,([^,]+)'],
    'grupo': [r'Grupo:\s*(?:,|\s+)(\d+)', r'Grupo:,(\d+)', r'Grupo: (\d+)'],
    'diu_int': [r'DIU INT:\s*(?:,|\s+)([^,\s]+)', r'DIU INT:,([^,]+)'],
    'dium_int': [r'DIUM INT:\s*(?:,|\s+)([^,\s]+)', r'DIUM INT:,([^,]+)'],
    'fiu_int': [r'FIU INT:\s*(?:,|\s+)([^,\s]+)', r'FIU INT:,([^,]+)'],
    'fium_int': [r'FIUM INT:\s*(?:,|\s+)([^,\s]+)', r'FIUM INT:,([^,]+)'],
    'fiug': [r'FIUG:\s*(?:,|\s+)([\d.]+)', r'FIUG: ([\d.]+)'],
    'diug': [r'DIUG:\s*(?:,|\s+)([\d.]+)', r'DIUG: ([\d.]+)']
}


def convertir_pdf_a_csv(ruta_pdf, ruta_salida=None):
    """
    Convierte un archivo PDF a formato CSV, preservando la estructura de columnas.
    
    Args:
        ruta_pdf (str): Ruta al archivo PDF
        ruta_salida (str, optional): Ruta donde se guardará el archivo CSV.
                                     Si es None, se usará el nombre del PDF con .csv.
    
    Returns:
        str: Ruta del archivo CSV creado
    """
    if ruta_salida is None:
        nombre_base = os.path.splitext(os.path.basename(ruta_pdf))[0]
        directorio = os.path.dirname(os.path.abspath(ruta_pdf))
        ruta_salida = os.path.join(directorio, f"{nombre_base}.csv")
    
    # Extraer datos organizados por filas y columnas
    datos_estructurados = extraer_datos_estructurados(ruta_pdf)
    
    # Guardar en archivo CSV
    with open(ruta_salida, 'w', encoding='utf-8', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        
        # Escribir datos
        for pagina, filas in datos_estructurados.items():
            # Escribir encabezado de página
            writer.writerow([f"PÁGINA {pagina}"])
            writer.writerow([])  # Línea vacía para separar
            
            # Escribir filas de datos
            for fila in filas:
                writer.writerow(fila)
            
            # Separador entre páginas
            writer.writerow([])
            writer.writerow([])
    
    return ruta_salida


def procesar_texto(texto):
    """
    Procesa el texto para separar números y valores que podrían estar juntos.
    
    Args:
        texto (str): Texto a procesar
        
    Returns:
        list: Lista de elementos separados
    """
    # Patrones para buscar en el texto
    patrones = [
        # Patrón para separar números con comas seguidos de otros números
        r'(\d[\d,.]+)\s+(\d[\d,.]+)',
        # separa texto de números
        r'([a-zA-Z]+[a-zA-Z\s]+)(\d[\d,.]+)'
    ]
    
    elementos = [texto]
    
    # Aplicar cada patrón
    for patron in patrones:
        nuevos_elementos = []
        for elem in elementos:
            # Verificar si el patrón coincide
            coincidencia = re.search(patron, elem)
            if coincidencia:
                # Separar el elemento según el patrón
                partes = re.split(patron, elem)
                # Filtrar elementos vacíos y agregar a la lista
                nuevos_elementos.extend([p.strip() for p in partes if p and p.strip()])
            else:
                nuevos_elementos.append(elem)
        elementos = nuevos_elementos
    
    # Eliminar duplicados y elementos vacíos
    return [e for e in elementos if e and e.strip()]


def extraer_datos_estructurados(ruta_pdf):
    """
    Extrae datos del PDF y los organiza en una estructura adecuada para CSV
    
    Args:
        ruta_pdf (str): Ruta al archivo PDF
    
    Returns:
        dict: Diccionario con páginas como claves y listas de filas como valores
    """
    datos_por_pagina = {}
    
    with open(ruta_pdf, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        
        device = PDFPageAggregator(rsrcmgr, laparams=LAParams(
            line_margin=0.5,
            word_margin=0.1,
            boxes_flow=-1.0,  
            detect_vertical=True
        ))
        
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        page_num = 0
        for page in PDFPage.create_pages(doc):
            page_num += 1
            
            interpreter.process_page(page)
            layout = device.get_result()
            
            # Organizar elementos por posición Y para preservar filas
            elementos_por_y = {}
            
            for element in layout:
                if hasattr(element, 'get_text'):
                    # Redondeadp para agrupar líneas cercanas (en grupos de 10 unidades)
                    y = int(element.y0 / 10) * 10
                    if y not in elementos_por_y:
                        elementos_por_y[y] = []
                    elementos_por_y[y].append(element)
            filas_pagina = []
            
            # Ordenar por y descendente (de arriba pa abajo)
            for y in sorted(elementos_por_y.keys(), reverse=True):
                # Ordenar elementos de izquierda a derecha en cada fila
                elementos = sorted(elementos_por_y[y], key=lambda e: e.x0)
                
                # Lista para almacenar todos los elementos procesados de la fila
                elementos_procesados = []
                
                for element in elementos:
                    texto = element.get_text().strip()
                    if texto:
                        # Procesar el texto para separar posibles números juntos
                        sub_elementos = procesar_texto(texto)
                        elementos_procesados.extend(sub_elementos)
                
                # Añadir fila si no está pelá
                if elementos_procesados:
                    filas_pagina.append(elementos_procesados)
            datos_por_pagina[page_num] = filas_pagina
    
    return datos_por_pagina


def analizar_estructura_columnas(datos_por_pagina):
    """
    Analiza la estructura de las columnas para intentar normalizar el número de columnas.
    Útil para determinar un encabezado si es necesario.
    
    Args:
        datos_por_pagina (dict): Datos estructurados por página
        
    Returns:
        int: Número máximo de columnas encontrado
    """
    max_columnas = 0
    
    for pagina, filas in datos_por_pagina.items():
        for fila in filas:
            max_columnas = max(max_columnas, len(fila))
    
    return max_columnas


def leer_archivo(file_path):
    """
    Lee el contenido de un archivo con manejo de codificaciones.
    
    Args:
        file_path (str): Ruta al archivo
        
    Returns:
        str: Contenido del archivo
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        # Para probar diferentes codificadores (Se empieza con utf-8)
        with open(file_path, 'r', encoding='latin-1') as file:
            content = file.read()
    return content


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

def extraer_tabla_componentes(file_path):
    """
    Extrae los datos de la tabla de componentes de energía.
    
    Args:
        file_path (str): Ruta al archivo CSV de la factura
        
    Returns:
        list: Lista de diccionarios con los datos de los componentes
    """
    content = leer_archivo(file_path)
    
    # Encontrar la tabla de componentes
    table_pattern = r'Componentes,kWh\s+-\s+kVArh,\$/kWh.*?Subtotal\s+energía,.*?"?([-\d,]+)"?'
    table_match = re.search(table_pattern, content, re.DOTALL)
    
    concepto_data = []
    
    if table_match:
        table_content = table_match.group(0)
        
        # Cada componente individual es extraído acá
        for component in COMPONENTES_ENERGIA:
            match = re.search(component["pattern"], table_content)
            
            if match:
                concepto = {}
                concepto["concepto"] = component["name"]
                
                if component["name"] == "Generación" or component["name"] == "Energía inductiva + capacitiva":
                    concepto["kwh_kvarh"] = match.group(1).replace(',', '').replace('"', '') if match.group(1) else "0"
                    concepto["precio_kwh"] = match.group(2).replace(',', '') if match.group(2) else "0"
                    concepto["mes_corriente"] = match.group(3).replace(',', '').replace('"', '') if match.group(3) else "0"
                    concepto["mes_anteriores"] = match.group(4).replace(',', '').replace('"', '') if match.group(4) else "0"
                    concepto["total"] = match.group(5).replace(',', '').replace('"', '') if match.group(5) else "0"
                else:
                    concepto["kwh_kvarh"] = "N/A"
                    concepto["precio_kwh"] = match.group(1).replace(',', '') if match.group(1) else "0"
                    concepto["mes_corriente"] = match.group(2).replace(',', '').replace('"', '') if match.group(2) else "0"
                    concepto["mes_anteriores"] = match.group(3).replace(',', '').replace('"', '') if match.group(3) else "0"
                    concepto["total"] = match.group(4).replace(',', '').replace('"', '') if match.group(4) else "0"
                
                # Limpiar valores negativos, mantener el signo
                if concepto["mes_anteriores"] != "N/A" and concepto["mes_anteriores"].startswith('-'):
                    concepto["mes_anteriores"] = "-" + concepto["mes_anteriores"].replace('-', '')
                if concepto["total"] != "N/A" and concepto["total"].startswith('-'):
                    concepto["total"] = "-" + concepto["total"].replace('-', '')
                    
                concepto_data.append(concepto)
    
    # Si no se encontró la tabla usando el primer método, intentar con el método alternativo
    if not concepto_data:
        # Patrones para extraer diferentes conceptos (Generación, Comercialización, etc.)
        patrones_concepto = [
            r'Generación:[\s\S]*?kWh-kVArh:\s*([-\d,]+)[\s\S]*?\$/kWh:\s*([-\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([-\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([-\d,-]+)"?[\s\S]*?Total \$:\s*"?([-\d,]+)"?',
            r'Comercialización:[\s\S]*?\$/kWh:\s*([-\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([-\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([-\d,-]+)"?[\s\S]*?Total \$:\s*"?([-\d,]+)"?',
            r'Transmisión:[\s\S]*?\$/kWh:\s*([-\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([-\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([-\d,-]+)"?[\s\S]*?Total \$:\s*"?([-\d,]+)"?',
            r'Distribución:[\s\S]*?\$/kWh:\s*([-\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([-\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([-\d,-]+)"?[\s\S]*?Total \$:\s*"?([-\d,]+)"?',
            r'Pérdidas:[\s\S]*?\$/kWh:\s*([-\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([-\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([-\d,-]+)"?[\s\S]*?Total \$:\s*"?([-\d,]+)"?',
            r'Restricciones:[\s\S]*?\$/kWh:\s*([-\d.,-]+)[\s\S]*?Mes corriente \$:\s*"?([-\d,-]+)"?[\s\S]*?Mes anteriores \$:\s*"?([-\d,-]+)"?[\s\S]*?Total \$:\s*"?([-\d,-]+)"?',
            r'Otros cargos:[\s\S]*?\$/kWh:\s*([-\d.,]+)[\s\S]*?Mes corriente \$:\s*"?([-\d,]+)"?[\s\S]*?Mes anteriores \$:\s*"?([-\d,-]+)"?[\s\S]*?Total \$:\s*"?([-\d,]+)"?',
            r'Energía inductiva \+ capacitiva:[\s\S]*?kWh-kVArh:\s*"?([-\d,.]+)"?[\s\S]*?\$/kWh:\s*"?([-\d,.]+)"?[\s\S]*?Mes corriente \$:\s*"?([-\d,.]+)"?[\s\S]*?Mes anteriores \$:\s*"?([-\d,.]+)"?[\s\S]*?Total \$:\s*"?([-\d,.]+)"?']
        
        nombres_conceptos = [
            'Generación', 'Comercialización', 'Transmisión', 'Distribución', 
            'Pérdidas', 'Restricciones', 'Otros cargos', 'Energía inductiva + capacitiva'
        ]
        
        for i, pattern in enumerate(patrones_concepto):
            match = re.search(pattern, content)
            if match:
                concepto = {}
                concepto['concepto'] = nombres_conceptos[i]
                
                # Para la Generación y Energía inductiva + capacitiva que tienen kWh-kVArh
                if i == 0 or i == 7:
                    concepto['kwh_kvarh'] = match.group(1).replace(',', '') if match.group(1) else "0"
                    concepto['precio_kwh'] = match.group(2).replace(',', '') if match.group(2) else "0"
                    concepto['mes_corriente'] = match.group(3).replace(',', '') if match.group(3) else "0"
                    concepto['mes_anteriores'] = match.group(4).replace(',', '') if match.group(4) else "0"
                    concepto['total'] = match.group(5).replace(',', '') if match.group(5) else "0"
                else:
                    concepto['kwh_kvarh'] = "N/A"
                    concepto['precio_kwh'] = match.group(1).replace(',', '') if match.group(1) else "0"
                    concepto['mes_corriente'] = match.group(2).replace(',', '') if match.group(2) else "0"
                    concepto['mes_anteriores'] = match.group(3).replace(',', '') if match.group(3) else "0"
                    concepto['total'] = match.group(4).replace(',', '') if match.group(4) else "0"
                
                # Limpiar cualquier coma al inicio
                for key in concepto:
                    if isinstance(concepto[key], str) and concepto[key].startswith(','):
                        concepto[key] = concepto[key][1:]
                        
                concepto_data.append(concepto)
    
    # Caso particular "Energía inductiva + capacitiva"
    energia_pattern = r'8\.\s+Energ[ií]a\s+inductiva\s+\+\s+capacitiva\s+facturada,\s*([-\d,.]*),\s*([-\d,.]+),\s*"?([-\d,.]*)"?,\s*"?([-\d,.]+)"?,\s*"?([-\d,.]+)"?'
    match = re.search(energia_pattern, content)
    if match:
        concepto = {
            "concepto": "Energía inductiva + capacitiva",
            "kwh_kvarh": match.group(1).replace(',', '') if match.group(1) and match.group(1) != '0' else "0",
            "precio_kwh": match.group(2).replace(',', '') if match.group(2) else "0",
            "mes_corriente": match.group(3).replace(',', '').replace('"', '') if match.group(3) and match.group(3) != '0' else "0",
            "mes_anteriores": match.group(4).replace(',', '').replace('"', '') if match.group(4) else "0",
            "total": match.group(5).replace(',', '').replace('"', '') if match.group(5) else "0"
        }
        
        for i, item in enumerate(concepto_data):
            if item["concepto"] == "Energía inductiva + capacitiva":
                concepto_data[i] = concepto
                break
        else:
            concepto_data.append(concepto)
    concepto_data = [c for c in concepto_data if c["concepto"] != "Energía inductiva + capacitiva"]
    
    # Extracción directa para "Energía inductiva + capacitiva" en el caso que no funcione
    # Buscar fila en el csv que empiece con:  "8. Energía inductiva + capacitiva facturada"
    lines = content.split('\n')
    for line in lines:
        if '8.' in line and 'inductiva' in line and 'capacitiva' in line:
            # Esto separa por comas pero solo cuando no hay comillas
            parts = []
            in_quotes = False
            current_part = ""
            
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                    current_part += char
                elif char == ',' and not in_quotes:
                    parts.append(current_part.strip())
                    current_part = ""
                else:
                    current_part += char
            
            if current_part:
                parts.append(current_part.strip())
            
            # Extracción ind + cap
            if len(parts) >= 6:
                # Formato particular: [label, kwh_kvarh, precio_kwh, mes_corriente, mes_anteriores, total]
                concepto = {
                    "concepto": "Energía inductiva + capacitiva",
                    "kwh_kvarh": parts[1].replace('"', '') if parts[1] else "0",
                    "precio_kwh": parts[2].replace('"', '') if parts[2] else "0",
                    "mes_corriente": parts[3].replace('"', '').replace(',', '') if parts[3] else "0",
                    "mes_anteriores": parts[4].replace('"', '').replace(',', '') if parts[4] else "0",
                    "total": parts[5].replace('"', '').replace(',', '') if parts[5] else "0"
                }
                concepto_data.append(concepto)
                break
    
    return concepto_data
    


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
    