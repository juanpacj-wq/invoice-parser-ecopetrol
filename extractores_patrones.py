"""
Módulo con todos los patrones regex para extracción de datos de facturas.
Este módulo centraliza todos los patrones de expresiones regulares utilizados
para extraer información de las facturas de energía.
"""

# Patrones regex centralizados para extracción de datos generales
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
        r'Energ[ií]a\s*reactiva\s*inductiva[,\s]+"?([0-9.,]+)"?', 
        r'Energ[ií]a\treactiva\tinductiva[,\s]+"?([0-9.,]+)"?',
        r'Energ[ií]a\s*reactiva\s*inductiva[,\s]*(?<!")([0-9.,]+)(?!")',
        r'Energ[ií]a\treactiva\tinductiva[,\s]*(?<!")([0-9.,]+)(?!")'
    ],
    'energia_reactiva_capacitiva': [
        r'Energ[ií]a\s*reactiva\s*capacitiva[,\s]+"?([0-9.,]+)"?', 
        r'Energ[ií]a\treactiva\tcapacitiva[,\s]+"?([0-9.,]+)"?',
        r'Energ[ií]a\s*reactiva\s*capacitiva[,\s]*(?<!")([0-9.,]+)(?!")',
        r'Energ[ií]a\treactiva\tcapacitiva[,\s]*(?<!")([0-9.,]+)(?!")'
    ],
    'total_energia_reactiva': [
        r'Total\s*energ[ií]a\s*reactiva[,\s]+"?([0-9.,]+)"?', 
        r'Total\tenerg[ií]a\treactiva[,\s]+"?([0-9.,]+)"?',
        r'Total\s*energ[ií]a\s*reactiva[,\s]*(?<!")([0-9.,]+)(?!")',
        r'Total\tenerg[ií]a\treactiva[,\s]*(?<!")([0-9.,]+)(?!")'
    ],
    'energia_activa': [
        r'Energ[ií]a\s*activa[,\s]+"?([0-9.,]+)"?',
        r'Energ[ií]a\tactiva[,\s]+"?([0-9.,]+)"?',
        r'Energ[ií]a\s*activa[,\s]*(?<!")([0-9.,]+)(?!")',
        r'Energ[ií]a\tactiva[,\s]*(?<!")([0-9.,]+)(?!")'
    ]
}

# Patrones para componentes de energía - soporta formato viejo y nuevo
COMPONENTES_ENERGIA = [
    {
        "name": "Generación",
        "patterns": [
            # Formato viejo con kWh
            r'1\.\s+Generación,"?([-\d,]*)"?,([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?',
            # Formato nuevo sin kWh
            r'1\.\s+Generación,([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?'
        ],
        "has_kwh": True  # Indica que puede tener kWh en formato viejo
    },
    {
        "name": "Comercialización",
        "patterns": [
            r'2\.\s+Comercialización,([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?'
        ],
        "has_kwh": False
    },
    {
        "name": "Transmisión",
        "patterns": [
            r'3\.\s+Transmisión,([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?'
        ],
        "has_kwh": False
    },
    {
        "name": "Distribución",
        "patterns": [
            r'4\.\s+Distribución,([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?'
        ],
        "has_kwh": False
    },
    {
        "name": "Pérdidas",
        "patterns": [
            r'5\.\s+Perdidas\s+\(\*\),([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?',
            r'5\.\s+Pérdidas\s+\(\*\),([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?'
        ],
        "has_kwh": False
    },
    {
        "name": "Restricciones",
        "patterns": [
            r'6\.\s+Restricciones,([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?'
        ],
        "has_kwh": False
    },
    {
        "name": "Otros cargos",
        "patterns": [
            r'7\.\s+Otros\s+cargos,([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?'
        ],
        "has_kwh": False
    },
    {
        "name": "Energía inductiva + capacitiva",
        "patterns": [
            # Formato viejo con kWh primero
            r'8\.\s+Energía\s+inductiva\s+\+\s+capacitiva\s+facturada,"?([-\d,]*)"?,([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?',
            # Formato nuevo sin kWh
            r'8\.\s+Energía\s+inductiva\s+\+\s+capacitiva\s+facturada,([-\d\.]+),"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?,"?([-\d,]+\.?\d*)"?'
        ],
        "has_kwh": True  # Puede tener kWh en formato viejo
    }
]

# Patrones para extraer los parámetros específicos datos OR
PATRONES_PARAMETROS_ESPECIFICOS = {
    'ir': [
        r'IR:\s*(?:,|\s+)([^,\s]+)', 
        r'IR:,([^,]+)',
        r'IR:\s*(\d+)'
    ],
    'grupo': [
        r'Grupo:\s*(?:,|\s+)(\d+)', 
        r'Grupo:,(\d+)', 
        r'Grupo: (\d+)'
    ],
    'diu_int': [
        r'DIU INT:\s*(?:,|\s+)([^,\s]+)', 
        r'DIU INT:,([^,]+)'
    ],
    'dium_int': [
        r'DIUM INT:\s*(?:,|\s+)([^,\s]+)', 
        r'DIUM INT:,([^,]+)'
    ],
    'fiu_int': [
        r'FIU INT:\s*(?:,|\s+)([^,\s]+)', 
        r'FIU INT:,([^,]+)'
    ],
    'fium_int': [
        r'FIUM INT:\s*(?:,|\s+)([^,\s]+)', 
        r'FIUM INT:,([^,]+)'
    ],
    'fiug': [
        r'FIUG:\s*(?:,|\s+)([\d.]+)', 
        r'FIUG: ([\d.]+)',
        r'FIUG:\s*([\d.]+),\s*DIUG:\s*([\d.]+)'  # Patrón combinado
    ],
    'diug': [
        r'DIUG:\s*(?:,|\s+)([\d.]+)', 
        r'DIUG: ([\d.]+)',
        r'FIUG:\s*([\d.]+),\s*DIUG:\s*([\d.]+)'  # Patrón combinado
    ]
}