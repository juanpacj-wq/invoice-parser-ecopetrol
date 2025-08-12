"""
Módulo para la conexión con la base de datos corporativa.
Permite extraer datos para comparación con las facturas procesadas.
"""

import psycopg2
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DBConnector:
    """
    Clase para gestionar la conexión a la base de datos corporativa
    y realizar consultas para la comparación de facturas.
    """
    
    def __init__(self):
        """Inicializa el conector a la base de datos."""
        self.connection_params = {
            'host': '172.16.2.52',
            'database': 'liquidacionxm',
            'user': 'gecc_read',
            'password': 'OSiiErZ229F#',
            'port': '5432'
        }
    
    def connect(self):
        """
        Establece conexión con la base de datos.
        
        Returns:
            connection: Objeto de conexión a la base de datos o None si falla
        """
        try:
            connection = psycopg2.connect(**self.connection_params)
            logger.info("Conexión a la base de datos establecida")
            return connection
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            return None

    def get_factura_data_from_db(self, fecha_inicio, fecha_fin, fronteras=None):
        """
        Obtiene los datos de facturas desde la base de datos en un rango de fechas.
        
        Args:
            fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'
            fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'
            fronteras (list, optional): Lista de fronteras a filtrar
                
        Returns:
            pandas.DataFrame: DataFrame con los datos de las facturas o None si falla
        """
        try:
            # Log de parámetros de consulta para depurar
            logger.info(f"Consultando facturas con fechas: {fecha_inicio} a {fecha_fin}")
            if fronteras:
                logger.info(f"Filtrando por fronteras: {', '.join(fronteras)}")
            
            # Consulta específica por período de facturación con campos adicionales para componentes
            query = """
            SELECT frontera as frt, factura_dian as factura, v_consumo_energia_ajustado as subtotal_energía_total, v_contribucion + v_consumo_energia_ajustado as subtotal_energía_contribución_pesos,
            q_activa as energía_activa, q_inductiva_pen as energía_reactiva_inductiva_facturada, q_reactiva_pen as total_energia_reactiva,
            q_capacitiva_pen as energía_reactiva_capacitiva_facturada, v_gm as generación_mes_corriente, 
            v_rm as restricciones_mes_corriente, v_cm as comercialización_mes_corriente, v_dm as distribución_mes_corriente, 
            v_om as otros_cargos_mes_corriente, v_ppond as pérdidas_mes_corriente, v_tpond as transmisión_mes_corriente, 
            v_reactiva_pen as energía_inductiva_capacitiva_facturada_mes_corriente, v_consumo_energia as subtotal_energía_mes_corriente,  
            v_gm_ajuste as generación_ajustes_anteriores, v_rm_ajuste as restricciones_ajustes_anteriores, 
            v_cm_ajuste as comercialización_ajustes_anteriores, v_dm_ajuste as distribución_ajustes_anteriores, 
            v_om_ajuste as otros_cargos_ajustes_anteriores,  v_ppond_ajuste as pérdidas_ajustes_anteriores, 
            v_tpond_ajuste as transmisión_ajustes_anteriores, v_consumo_energia_ajuste as subtotal_energía_ajustes_anteriores, 
            v_reactiva_pen_ajuste as energía_inductiva_capacitiva_facturada_ajustes_anteriores,  v_gm_ajustado as generación_total, v_iap_ajuste + v_iapb as alumbrado_publico_total,
            v_rm_ajustado as restricciones_total, v_cm_ajustado as comercialización_total, v_dm_ajustado as distribución_total, 
            v_om_ajustado as otros_cargos_total, interes_mora+v_aj_cargos_regulados+v_compensacion+total_saldo_cartera+v_trabajos_otc_gec+v_trabajos_otc_oa+v_sobretasa as otros_cobros,v_trabajos_otc_gec+v_trabajos_otc_oa as recobros,  v_ppond_ajustado as pérdidas_total, v_tpond_ajustado as transmisión_total, 
            v_reactiva_pen_ajustado as energía_inductiva_capacitiva_facturada_total, v_contribucion as contribución, 
            v_compensacion as compensaciones, total_saldo_cartera as amortizacion, v_iapb as impuesto_alumbrado_público, 
            v_iap_ajuste as ajuste_iap_otros_meses, v_sgcv as tasa_especial_convivencia_ciudadana, v_asgcv as ajuste_tasa_convivencia_otros_meses, v_sobretasa as sobretasa,
            v_neto_factura as neto_a_pagar, factor_m, v_aj_cargos_regulados as ajustes_cargos_regulados, 
            interes_mora as interés_por_mora, v_neto_factura as total_servicio_energía_impuestos,v_asgcv + v_sgcv as covivencia_ciudadana,
            
            --interes_mora+v_aj_cargos_regulados+v_compensacion+total_saldo_cartera as otros_cobros

            -- Campos adicionales para componentes detallados
            q_activa as generación_kwh_kvarh, 
            gm_redo as generación_precio_kwh,
            v_gm as generación_mes_corriente_pesos,
            v_gm_ajuste as generación_mes_anteriores_pesos, 
            v_gm_ajustado as generación_total_pesos,
            
            cm_redo as comercialización_precio_kwh, 
            v_cm as comercialización_mes_corriente_pesos,
            v_cm_ajuste as comercialización_mes_anteriores_pesos, 
            v_cm_ajustado as comercialización_total_pesos,
            
            tpond_redo as transmisión_precio_kwh, 
            v_tpond as transmisión_mes_corriente_pesos,
            v_tpond_ajuste as transmisión_mes_anteriores_pesos, 
            v_tpond_ajustado as transmisión_total_pesos,
            
            dm_redo as distribución_precio_kwh, 
            v_dm as distribución_mes_corriente_pesos,
            v_dm_ajuste as distribución_mes_anteriores_pesos, 
            v_dm_ajustado as distribución_total_pesos,
            
            ppond_redo as pérdidas_precio_kwh, 
            v_ppond as pérdidas_mes_corriente_pesos,
            v_ppond_ajuste as pérdidas_mes_anteriores_pesos, 
            v_ppond_ajustado as pérdidas_total_pesos,
            
            rm_redo as restricciones_precio_kwh, 
            v_rm as restricciones_mes_corriente_pesos,
            v_rm_ajuste as restricciones_mes_anteriores_pesos, 
            v_rm_ajustado as restricciones_total_pesos,
            
            om_redo as otros_cargos_precio_kwh, 
            v_om as otros_cargos_mes_corriente_pesos,
            v_om_ajuste as otros_cargos_mes_anteriores_pesos, 
            v_om_ajustado as otros_cargos_total_pesos,
            
            q_inductiva_pen + q_capacitiva_pen as energía_inductiva_capacitiva_kwh_kvarh, 
            v_reactiva_pen as energía_inductiva_capacitiva_mes_corriente_pesos,
            v_reactiva_pen_ajuste as energía_inductiva_capacitiva_mes_anteriores_pesos, 
            v_reactiva_pen_ajustado as energía_inductiva_capacitiva_total_pesos
            
            FROM app_ectc_gecc.reporte_liquidacion_frts 
            WHERE fechafacturacion BETWEEN to_date(%s, 'YYYY-MM-DD') AND to_date(%s, 'YYYY-MM-DD') and factura_dian is not null"""
            
            conn = self.connect()
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            # Preparar parámetros
            params = [fecha_inicio, fecha_fin]
            
            # Añadir filtro de fronteras si es necesario
            if fronteras and len(fronteras) > 0:
                placeholder = ','.join(['%s'] * len(fronteras))
                query += f" AND frontera IN ({placeholder})"
                params.extend(fronteras)
            
            # Log de la consulta completa para depuración
            logger.info(f"Ejecutando consulta: {query}")
            logger.info(f"Con parámetros: {params}")
            
            # Ejecutar consulta
            cursor.execute(query, params)
            
            # Obtener resultados
            results = cursor.fetchall()
            logger.info(f"Consulta ejecutada. Resultados: {len(results)}")
            
            # Si no hay resultados, intentar con una consulta más flexible
            if not results and fronteras and len(fronteras) > 0:
                logger.info("No se encontraron resultados. Intentando búsqueda por frontera...")
                
                # Consulta por frontera sin restricción de fecha
                frontier_query = """
                SELECT frontera as frt, factura_dian as factura, v_consumo_energia_ajustado as subtotal_energía_total,  v_contribucion + v_consumo_energia_ajustado as subtotal_energía_contribución_pesos,
                q_activa as energía_activa, q_inductiva_pen as energía_reactiva_inductiva_facturada, q_reactiva_pen as total_energia_reactiva,
                q_capacitiva_pen as energía_reactiva_capacitiva_facturada, v_gm as generación_mes_corriente, 
                v_rm as restricciones_mes_corriente, v_cm as comercialización_mes_corriente, v_dm as distribución_mes_corriente, 
                v_om as otros_cargos_mes_corriente, v_ppond as pérdidas_mes_corriente, v_tpond as transmisión_mes_corriente, 
                v_reactiva_pen as energía_inductiva_capacitiva_facturada_mes_corriente, v_consumo_energia as subtotal_energía_mes_corriente,  
                v_gm_ajuste as generación_ajustes_anteriores, v_rm_ajuste as restricciones_ajustes_anteriores, 
                v_cm_ajuste as comercialización_ajustes_anteriores, v_dm_ajuste as distribución_ajustes_anteriores, 
                v_om_ajuste as otros_cargos_ajustes_anteriores,  v_ppond_ajuste as pérdidas_ajustes_anteriores, 
                v_tpond_ajuste as transmisión_ajustes_anteriores, v_consumo_energia_ajuste as subtotal_energía_ajustes_anteriores, 
                v_reactiva_pen_ajuste as energía_inductiva_capacitiva_facturada_ajustes_anteriores,  v_gm_ajustado as generación_total, 
                v_rm_ajustado as restricciones_total, v_cm_ajustado as comercialización_total, v_dm_ajustado as distribución_total, 
                v_om_ajustado as otros_cargos_total,  v_ppond_ajustado as pérdidas_total, v_tpond_ajustado as transmisión_total, 
                v_reactiva_pen_ajustado as energía_inductiva_capacitiva_facturada_total,interes_mora+v_aj_cargos_regulados+v_compensacion+total_saldo_cartera+v_trabajos_otc_gec+v_trabajos_otc_oa+v_sobretasa as otros_cobros,v_trabajos_otc_gec+v_trabajos_otc_oa as recobros, v_contribucion as contribución, 
                v_compensacion as compensaciones, total_saldo_cartera as amortizacion, v_iapb as impuesto_alumbrado_público, v_iap_ajuste + v_iapb as alumbrado_publico_total,
                v_iap_ajuste as ajuste_iap_otros_meses, v_sgcv as tasa_especial_convivencia_ciudadana, v_asgcv as ajuste_tasa_convivencia_otros_meses, 
                v_neto_factura as neto_a_pagar, factor_m, v_aj_cargos_regulados as ajustes_cargos_regulados, 
                interes_mora as interés_por_mora,v_asgcv + v_sgcv as covivencia_ciudadana,v_sobretasa as sobretasa,
                fechafacturacion, v_neto_factura as total_servicio_energía_impuestos,
                
                -- Campos adicionales para componentes detallados
                q_activa as generación_kwh_kvarh, 
                gm_redo as generación_precio_kwh,
                v_gm as generación_mes_corriente_pesos,
                v_gm_ajuste as generación_mes_anteriores_pesos, 
                v_gm_ajustado as generación_total_pesos,
                
                cm_redo as comercialización_precio_kwh, 
                v_cm as comercialización_mes_corriente_pesos,
                v_cm_ajuste as comercialización_mes_anteriores_pesos, 
                v_cm_ajustado as comercialización_total_pesos,
                
                tpond_redo as transmisión_precio_kwh, 
                v_tpond as transmisión_mes_corriente_pesos,
                v_tpond_ajuste as transmisión_mes_anteriores_pesos, 
                v_tpond_ajustado as transmisión_total_pesos,
                
                dm_redo as distribución_precio_kwh, 
                v_dm as distribución_mes_corriente_pesos,
                v_dm_ajuste as distribución_mes_anteriores_pesos, 
                v_dm_ajustado as distribución_total_pesos,
                
                ppond_redo as pérdidas_precio_kwh, 
                v_ppond as pérdidas_mes_corriente_pesos,
                v_ppond_ajuste as pérdidas_mes_anteriores_pesos, 
                v_ppond_ajustado as pérdidas_total_pesos,
                
                rm_redo as restricciones_precio_kwh, 
                v_rm as restricciones_mes_corriente_pesos,
                v_rm_ajuste as restricciones_mes_anteriores_pesos, 
                v_rm_ajustado as restricciones_total_pesos,
                
                om_redo as otros_cargos_precio_kwh, 
                v_om as otros_cargos_mes_corriente_pesos,
                v_om_ajuste as otros_cargos_mes_anteriores_pesos, 
                v_om_ajustado as otros_cargos_total_pesos,
                
                q_inductiva_pen + q_capacitiva_pen as energía_inductiva_capacitiva_kwh_kvarh, 
                v_reactiva_pen as energía_inductiva_capacitiva_mes_corriente_pesos,
                v_reactiva_pen_ajuste as energía_inductiva_capacitiva_mes_anteriores_pesos, 
                v_reactiva_pen_ajustado as energía_inductiva_capacitiva_total_pesos

                FROM app_ectc_gecc.reporte_liquidacion_frts 
                WHERE frontera IN ({}) and factura_dian is not null 
                ORDER BY fechafacturacion DESC
                """
                
                placeholder = ','.join(['%s'] * len(fronteras))
                frontier_query = frontier_query.format(placeholder)
                
                logger.info(f"Ejecutando consulta alternativa: {frontier_query}")
                logger.info(f"Con parámetros: {fronteras}")
                
                cursor.execute(frontier_query, fronteras)
                results = cursor.fetchall()
                
                if results:
                    logger.info(f"Se encontraron {len(results)} registros buscando solo por fronteras")
            
            # Obtener los nombres de las columnas
            column_names = [desc[0] for desc in cursor.description]
            
            # Crear DataFrame
            df = pd.DataFrame(results, columns=column_names)
            
            # Cerrar conexión
            cursor.close()
            conn.close()
            
            # Registrar información sobre los datos encontrados
            logger.info(f"Se obtuvieron {len(df)} registros de la base de datos")
            if not df.empty:
                fronteras_encontradas = df['frt'].unique()
                logger.info(f"Fronteras encontradas en la base de datos: {list(fronteras_encontradas)}")
                
                # Si hay fechafacturacion en las columnas, mostrar rango de fechas
                if 'fechafacturacion' in df.columns:
                    min_date = df['fechafacturacion'].min()
                    max_date = df['fechafacturacion'].max()
                    logger.info(f"Rango de fechas en los resultados: {min_date} a {max_date}")
            else:
                logger.warning("No se encontraron datos en la base de datos")
                if fronteras:
                    logger.warning(f"Fronteras buscadas: {fronteras}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al obtener datos de la base de datos: {e}", exc_info=True)
            return None

    def compare_with_facturas(self, facturas_procesadas, fecha_inicio=None, fecha_fin=None):
        """
        Compara las facturas procesadas con los datos de la base de datos.
        
        Args:
            facturas_procesadas (list): Lista de diccionarios con datos de facturas
            fecha_inicio (str, optional): Fecha de inicio en formato 'YYYY-MM-DD'
            fecha_fin (str, optional): Fecha de fin en formato 'YYYY-MM-DD'
                
        Returns:
            pandas.DataFrame: DataFrame con la comparación de facturas
        """
        # Obtener fronteras de las facturas procesadas
        fronteras = []
        periodos_facturacion = []
        
        # Extraer información detallada para depuración
        for factura in facturas_procesadas:
            codigo_sic = factura['datos_generales'].get('codigo_sic', '')
            if codigo_sic and codigo_sic != "No encontrado":
                fronteras.append(codigo_sic)
                
                # Extraer período de facturación
                periodo = factura['datos_generales'].get('periodo_facturacion', 'No encontrado')
                periodos_facturacion.append((codigo_sic, periodo))
        
        if not fronteras:
            logger.warning("No se encontraron códigos de frontera válidos en las facturas procesadas")
            return pd.DataFrame()
        
        logger.info(f"Se encontraron {len(fronteras)} fronteras para comparar: {fronteras}")
        logger.info(f"Períodos de facturación: {periodos_facturacion}")
        
        # Si no se proporcionan fechas, extraerlas de las facturas
        if not fecha_inicio or not fecha_fin:
            fecha_inicio, fecha_fin = self.extract_date_range_from_facturas(facturas_procesadas)
        
        # Obtener datos de la base de datos
        db_data = self.get_factura_data_from_db(fecha_inicio, fecha_fin, fronteras)
        
        if db_data is None or db_data.empty:
            logger.warning("No se obtuvieron datos de la base de datos para comparar")
            
            # Lista de campos a comparar (todos los campos solicitados)
            campos_a_comparar = [
                'periodo_facturacion', 'factor_m', 'codigo_sic', 'subtotal_base_energia', 
                'contribucion', 'contribucion_otros_meses',
                'subtotal_energia_contribucion_pesos', 'otros_cobros', 'sobretasa', 
                'ajustes_cargos_regulados', 'compensaciones', 'saldo_cartera', 
                'interes_mora','recobros', 'alumbrado_publico', 'impuesto_alumbrado_publico', 
                'ajuste_iap_otros_meses', 'convivencia_ciudadana', 'tasa_especial_convivencia', 
                'ajuste_tasa_convivencia', 'total_servicio_energia_impuestos', 
                'ajuste_decena', 'neto_pagar', 'energia_reactiva_inductiva', 
                'energia_reactiva_capacitiva', 'total_energia_reactiva'
            ]
            
            # Crear un DataFrame de comparación con datos de la factura y valores nulos para DB
            comparaciones = []
            for factura in facturas_procesadas:
                codigo_sic = factura['datos_generales'].get('codigo_sic', "")
                if codigo_sic == "No encontrado" or not codigo_sic:
                    continue
                    
                # Agregar datos generales con valor nulo para DB
                for campo in campos_a_comparar:
                    var_factura = factura['datos_generales'].get(campo.lower(), 0)
                    comparaciones.append({
                        'ID_Factura': factura.get('id', ''),
                        'Frontera': codigo_sic,
                        'Concepto': campo,
                        'Valor_Factura': var_factura,
                        'Valor_Datalake': None,
                        'Diferencia': None,
                        'Estado': 'No encontrado en DB'
                    })
                
                # Agregar componentes con valor nulo para DB
                for componente in factura['componentes']:
                    concepto = componente.get('concepto', '')
                    valor_factura = componente.get('total', 0)
                    comparaciones.append({
                        'ID_Factura': factura.get('id', ''),
                        'Frontera': codigo_sic,
                        'Concepto': concepto,
                        'Valor_Factura': valor_factura,
                        'Valor_Datalake': None,
                        'Diferencia': None,
                        'Estado': 'No encontrado en DB'
                    })
                    
                    # Agregar campos detallados de componentes
                    for campo in ['kwh_kvarh', 'precio_kwh', 'mes_corriente', 'mes_anteriores']:
                        concepto_detallado = f"{concepto}_{campo}"
                        valor_factura = componente.get(campo, 0)
                        if valor_factura == "N/A":
                            valor_factura = 0
                        comparaciones.append({
                            'ID_Factura': factura.get('id', ''),
                            'Frontera': codigo_sic,
                            'Concepto': concepto_detallado,
                            'Valor_Factura': valor_factura,
                            'Valor_Datalake': None,
                            'Diferencia': None,
                            'Estado': 'No encontrado en DB'
                        })
            
            # Crear DataFrame con las comparaciones
            return pd.DataFrame(comparaciones)
        
        # Crear DataFrame para almacenar las comparaciones
        comparaciones = []
        
        # Mapeo de nombres de variables para comparar
        mapeo_variables = {
            'periodo_facturacion': 'período facturación',
            'factor_m': 'factor_m',
            'codigo_sic': 'frt',
            'subtotal_base_energia': 'subtotal_energía_total',
            'contribucion': 'contribución',
            'contribucion_otros_meses': 'contribución_otros_meses',
            'subtotal_energia_contribucion_pesos': 'subtotal_energía_contribución_pesos',
            'otros_cobros': 'otros_cobros',
            'sobretasa': 'sobretasa',
            'ajustes_cargos_regulados': 'ajustes_cargos_regulados',
            'compensaciones': 'compensaciones',
            'saldo_cartera': 'amortizacion',
            'interes_mora': 'interés_por_mora',
            'recobros':'recobros',
            'alumbrado_publico': 'alumbrado_publico_total',
            'impuesto_alumbrado_publico': 'impuesto_alumbrado_público',
            'ajuste_iap_otros_meses': 'ajuste_iap_otros_meses',
            'convivencia_ciudadana': 'covivencia_ciudadana',
            'tasa_especial_convivencia': 'tasa_especial_convivencia_ciudadana',
            'ajuste_tasa_convivencia': 'ajuste_tasa_convivencia_otros_meses',
            'total_servicio_energia_impuestos': 'total_servicio_energía_impuestos',
            'ajuste_decena': 'ajuste_decena',
            'neto_pagar': 'neto_a_pagar',
            'energia_reactiva_inductiva': 'energía_reactiva_inductiva_facturada',
            'energia_reactiva_capacitiva': 'energía_reactiva_capacitiva_facturada',
            'total_energia_reactiva': 'total_energia_reactiva'
        }
        
        # Para cada factura procesada, buscar correspondencia en la base de datos
        for factura in facturas_procesadas:
            codigo_sic = factura['datos_generales'].get('codigo_sic', "")
            if codigo_sic == "No encontrado" or not codigo_sic:
                continue
                
            # Buscar la frontera en los datos de la base de datos
            factura_db = db_data[db_data['frt'] == codigo_sic]
            
            if factura_db.empty:
                logger.warning(f"No se encontraron datos en BD para la frontera {codigo_sic}")
                
                # Agregar filas con datos de la factura pero sin datos de BD
                for var_factura, var_db in mapeo_variables.items():
                    valor_factura = factura['datos_generales'].get(var_factura, 0)
                    comparaciones.append({
                        'ID_Factura': factura.get('id', ''),
                        'Frontera': codigo_sic,
                        'Concepto': var_factura,
                        'Valor_Factura': valor_factura,
                        'Valor_Datalake': None,
                        'Diferencia': None,
                        'Estado': 'No encontrado en DB'
                    })
                
                # Agregar componentes
                for componente in factura['componentes']:
                    concepto = componente.get('concepto', '')
                    valor_factura = componente.get('total', 0)
                    comparaciones.append({
                        'ID_Factura': factura.get('id', ''),
                        'Frontera': codigo_sic,
                        'Concepto': concepto,
                        'Valor_Factura': valor_factura,
                        'Valor_Datalake': None,
                        'Diferencia': None,
                        'Estado': 'No encontrado en DB'
                    })
                    
                    # Agregar campos detallados de componentes
                    for campo in ['kwh_kvarh', 'precio_kwh', 'mes_corriente', 'mes_anteriores']:
                        concepto_detallado = f"{concepto}_{campo}"
                        valor_factura = componente.get(campo, 0)
                        if valor_factura == "N/A":
                            valor_factura = 0
                        comparaciones.append({
                            'ID_Factura': factura.get('id', ''),
                            'Frontera': codigo_sic,
                            'Concepto': concepto_detallado,
                            'Valor_Factura': valor_factura,
                            'Valor_Datalake': None,
                            'Diferencia': None,
                            'Estado': 'No encontrado en DB'
                        })
                
                continue
                
            # Si hay múltiples registros para la misma frontera, usar el más reciente
            if len(factura_db) > 1:
                logger.info(f"Se encontraron {len(factura_db)} registros para la frontera {codigo_sic}. Usando el primero.")
                factura_db = factura_db.iloc[[0]]
                
            # Comparar todas las variables generales
            for var_factura, var_db in mapeo_variables.items():
                valor_factura = factura['datos_generales'].get(var_factura, 0)
                
                # Convertir a float para evitar problemas de tipo
                if not isinstance(valor_factura, (int, float)):
                    try:
                        valor_factura = float(valor_factura)
                    except (ValueError, TypeError):
                        valor_factura = 0
                
                valor_db = factura_db[var_db.lower()].values[0] if var_db.lower() in factura_db.columns else 0
                
                # Asegurar que el valor de la BD sea numérico
                if not isinstance(valor_db, (int, float)):
                    try:
                        valor_db = float(valor_db)
                    except (ValueError, TypeError):
                        valor_db = 0
                
                # Caso especial para las variables específicas de energía reactiva
                if var_factura in ['energia_reactiva_inductiva', 'energia_reactiva_capacitiva', 'total_energia_reactiva']:
                    # Calcular diferencia como una simple resta
                    diferencia = abs(valor_factura - valor_db)
                    
                    # Verificar si la diferencia es mayor que 0.5
                    if diferencia > 0.5:
                        estado = 'Alerta'
                    else:
                        estado = 'OK'
                else:
                    # Cálculo original de diferencia para el resto de variables
                    if valor_db == 0:
                        if valor_factura == 0:
                            # Ambos valores son 0, por lo que no hay diferencia
                            diferencia = 0
                            estado = 'OK'
                        else:
                            # valor_db es 0 pero valor_factura no, diferencia es 100% o más
                            diferencia = 100  # O podrías usar float('inf') para representar infinito
                            estado = 'Alerta'
                    else:
                        # Cálculo normal de la diferencia porcentual
                        diferencia = abs(valor_factura - valor_db) / abs(valor_db) * 100
                        
                        # Verificar si la diferencia porcentual es mayor o igual al 1%
                        if diferencia >= 1:
                            estado = 'Alerta'
                        else:
                            estado = 'OK'
                
                # Agregar a la lista de comparaciones
                comparaciones.append({
                    'ID_Factura': factura.get('id', ''),
                    'Frontera': codigo_sic,
                    'Concepto': var_factura,
                    'Valor_Factura': valor_factura,
                    'Valor_Datalake': valor_db,
                    'Diferencia': diferencia,
                    'Estado': estado
                })
            
            # Mapeo detallado para componentes y sus campos
            componentes_map = {
                'Generación': {
                    'total': 'generación_total_pesos',
                    'kwh_kvarh': 'generación_kwh_kvarh',
                    'precio_kwh': 'generación_precio_kwh',
                    'mes_corriente': 'generación_mes_corriente_pesos',
                    'mes_anteriores': 'generación_mes_anteriores_pesos'
                },
                'Transmisión': {
                    'total': 'transmisión_total_pesos',
                    'kwh_kvarh': None,  # No aplica
                    'precio_kwh': 'transmisión_precio_kwh',
                    'mes_corriente': 'transmisión_mes_corriente_pesos',
                    'mes_anteriores': 'transmisión_mes_anteriores_pesos'
                },
                'Distribución': {
                    'total': 'distribución_total_pesos',
                    'kwh_kvarh': None,  # No aplica
                    'precio_kwh': 'distribución_precio_kwh',
                    'mes_corriente': 'distribución_mes_corriente_pesos',
                    'mes_anteriores': 'distribución_mes_anteriores_pesos'
                },
                'Pérdidas': {
                    'total': 'pérdidas_total_pesos',
                    'kwh_kvarh': None,  # No aplica
                    'precio_kwh': 'pérdidas_precio_kwh',
                    'mes_corriente': 'pérdidas_mes_corriente_pesos',
                    'mes_anteriores': 'pérdidas_mes_anteriores_pesos'
                },
                'Comercialización': {
                    'total': 'comercialización_total_pesos',
                    'kwh_kvarh': None,  # No aplica
                    'precio_kwh': 'comercialización_precio_kwh',
                    'mes_corriente': 'comercialización_mes_corriente_pesos',
                    'mes_anteriores': 'comercialización_mes_anteriores_pesos'
                },
                'Restricciones': {
                    'total': 'restricciones_total_pesos',
                    'kwh_kvarh': None,  # No aplica
                    'precio_kwh': 'restricciones_precio_kwh',
                    'mes_corriente': 'restricciones_mes_corriente_pesos',
                    'mes_anteriores': 'restricciones_mes_anteriores_pesos'
                },
                'Otros cargos': {
                    'total': 'otros_cargos_total_pesos',
                    'kwh_kvarh': None,  # No aplica
                    'precio_kwh': 'otros_cargos_precio_kwh',
                    'mes_corriente': 'otros_cargos_mes_corriente_pesos',
                    'mes_anteriores': 'otros_cargos_mes_anteriores_pesos'
                },
                'Energía inductiva + capacitiva': {
                    'total': 'energía_inductiva_capacitiva_total_pesos',
                    'kwh_kvarh': 'energía_inductiva_capacitiva_kwh_kvarh',
                    'precio_kwh': 'distribución_precio_kwh',  
                    'mes_corriente': 'energía_inductiva_capacitiva_mes_corriente_pesos',
                    'mes_anteriores': 'energía_inductiva_capacitiva_mes_anteriores_pesos'
                }
            }
            
            for componente in factura['componentes']:
                concepto = componente.get('concepto', '')
                if concepto in componentes_map:
                    var_db_total = componentes_map[concepto]['total']
                    valor_factura = componente.get('total', 0)
                    
                    # Convertir a float para evitar problemas de tipo
                    if not isinstance(valor_factura, (int, float)):
                        try:
                            valor_factura = float(valor_factura)
                        except (ValueError, TypeError):
                            valor_factura = 0
                    
                    valor_db = factura_db[var_db_total.lower()].values[0] if var_db_total.lower() in factura_db.columns else 0
                    
                    # Asegurar que el valor de la BD sea numérico
                    if not isinstance(valor_db, (int, float)):
                        try:
                            valor_db = float(valor_db)
                        except (ValueError, TypeError):
                            valor_db = 0
                    
                    # Calcular diferencia
                    diferencia = float(valor_factura) - float(valor_db)
                    
                    # Definir estado basado en la diferencia
                    if abs(diferencia) <= 1:  # Tolerancia de 1 para redondeos
                        estado = 'OK'
                    else:
                        estado = 'Alerta'
                    
                    # Agregar a la lista de comparaciones
                    comparaciones.append({
                        'ID_Factura': factura.get('id', ''),
                        'Frontera': codigo_sic,
                        'Concepto': concepto,
                        'Valor_Factura': valor_factura,
                        'Valor_Datalake': valor_db,
                        'Diferencia': diferencia,
                        'Estado': estado
                    })
                    
                    # Comparar campos detallados del componente
                    for campo, var_db_campo in componentes_map[concepto].items():
                        if campo != 'total' and var_db_campo is not None:
                            concepto_detallado = f"{concepto}_{campo}"
                            valor_factura = componente.get(campo, 0)
                            
                            # Manejar valores N/A
                            if valor_factura == "N/A":
                                valor_factura = 0
                                
                            # Convertir a float para evitar problemas de tipo
                            if not isinstance(valor_factura, (int, float)):
                                try:
                                    valor_factura = float(valor_factura)
                                except (ValueError, TypeError):
                                    valor_factura = 0
                            
                            valor_db = factura_db[var_db_campo.lower()].values[0] if var_db_campo.lower() in factura_db.columns else 0
                            
                            # Asegurar que el valor de la BD sea numérico
                            if not isinstance(valor_db, (int, float)):
                                try:
                                    valor_db = float(valor_db)
                                except (ValueError, TypeError):
                                    valor_db = 0
                            
                            # Calcular diferencia
                            diferencia = float(valor_factura) - float(valor_db)
                            
                            # Definir estado basado en la diferencia
                            if abs(diferencia) <= 1:  # Tolerancia de 1 para redondeos
                                estado = 'OK'
                            else:
                                estado = 'Alerta'
                            
                            # Agregar a la lista de comparaciones
                            comparaciones.append({
                                'ID_Factura': factura.get('id', ''),
                                'Frontera': codigo_sic,
                                'Concepto': concepto_detallado,
                                'Valor_Factura': valor_factura,
                                'Valor_Datalake': valor_db,
                                'Diferencia': diferencia,
                                'Estado': estado
                            })
        
        # Crear DataFrame con las comparaciones
        return pd.DataFrame(comparaciones)
    
    def extract_date_range_from_facturas(self, facturas_procesadas):
        """
        Extrae el rango de fechas de las facturas procesadas,
        asegurando que use el período de facturación y el último día del mes.
        
        Args:
            facturas_procesadas (list): Lista de diccionarios con datos de facturas
            
        Returns:
            tuple: (fecha_inicio, fecha_fin) en formato 'YYYY-MM-DD'
        """
        import calendar
        from datetime import datetime, date

        # Buscar períodos de facturación
        periodos_facturacion = []
        
        for factura in facturas_procesadas:
            datos_generales = factura.get('datos_generales', {})
            
            # Extraer período de facturación
            periodo_facturacion = datos_generales.get('periodo_facturacion')
            if periodo_facturacion and periodo_facturacion != "No encontrado":
                logger.info(f"Encontrado período de facturación: {periodo_facturacion}")
                # El período puede tener formato "YYYY-MM-DD a YYYY-MM-DD" o solo "YYYY-MM-DD"
                if ' a ' in periodo_facturacion:
                    inicio, fin = periodo_facturacion.split(' a ')
                    periodos_facturacion.append((inicio, fin))
                else:
                    # Si solo hay una fecha, asumir que es el inicio del período
                    periodos_facturacion.append((periodo_facturacion, ""))
        
        if not periodos_facturacion:
            logger.warning("No se encontraron períodos de facturación. Usando fechas predeterminadas.")
            # Usar el mes actual como predeterminado
            hoy = date.today()
            primer_dia = date(hoy.year, hoy.month, 1)
            ultimo_dia = date(hoy.year, hoy.month, calendar.monthrange(hoy.year, hoy.month)[1])
            return primer_dia.strftime('%Y-%m-%d'), ultimo_dia.strftime('%Y-%m-%d')
        
        # Procesar los períodos encontrados
        fechas_inicio = []
        fechas_fin = []
        
        for inicio, fin in periodos_facturacion:
            try:
                # Convertir fecha de inicio
                fecha_inicio = datetime.strptime(inicio, '%Y-%m-%d').date()
                fechas_inicio.append(fecha_inicio)
                
                # Procesar fecha de fin
                if fin:
                    fecha_fin = datetime.strptime(fin, '%Y-%m-%d').date()
                else:
                    # Si no hay fecha fin, calcular el último día del mes de la fecha de inicio
                    ultimo_dia = calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1]
                    fecha_fin = date(fecha_inicio.year, fecha_inicio.month, ultimo_dia)
                
                fechas_fin.append(fecha_fin)
                
                logger.info(f"Período procesado: {fecha_inicio} a {fecha_fin}")
            except ValueError as e:
                logger.error(f"Error al procesar fecha: {e}")
                continue
        
        if not fechas_inicio or not fechas_fin:
            logger.warning("No se pudieron procesar las fechas. Usando fechas predeterminadas.")
            # Usar el mes actual como predeterminado
            hoy = date.today()
            primer_dia = date(hoy.year, hoy.month, 1)
            ultimo_dia = date(hoy.year, hoy.month, calendar.monthrange(hoy.year, hoy.month)[1])
            return primer_dia.strftime('%Y-%m-%d'), ultimo_dia.strftime('%Y-%m-%d')
        
        # Obtener el rango completo (la fecha más temprana de inicio y la más tardía de fin)
        fecha_inicio_min = min(fechas_inicio)
        fecha_fin_max = max(fechas_fin)
        
        # Asegurar que la fecha de inicio sea el primer día del mes
        fecha_inicio_ajustada = date(fecha_inicio_min.year, fecha_inicio_min.month, 1)
        
        # Asegurar que la fecha de fin sea el último día del mes
        ultimo_dia = calendar.monthrange(fecha_fin_max.year, fecha_fin_max.month)[1]
        fecha_fin_ajustada = date(fecha_fin_max.year, fecha_fin_max.month, ultimo_dia)
        
        logger.info(f"Rango de fechas final: {fecha_inicio_ajustada} a {fecha_fin_ajustada}")
        
        return fecha_inicio_ajustada.strftime('%Y-%m-%d'), fecha_fin_ajustada.strftime('%Y-%m-%d')