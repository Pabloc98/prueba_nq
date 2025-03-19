from geopy.distance import geodesic
import pandas as pd
import numpy as np
import os
from pandasql import sqldf
import openpyxl
import WazeRouteCalculator as wrc
from geopy.distance import geodesic
from tqdm import tqdm

src_path = os.path.dirname(__file__)

#Funciones Auxiliares
#----------------------------------------------------------------------------------------
def leer_query(file_name: str) -> str:
    file_path = os.path.join(src_path, 'queries/{}'.format(file_name))
    fd = open(file_path, 'r')
    file = fd.read()
    fd.close()
    return file

def leer_bdd(file_name):
    file_path = os.path.join(src_path, 'datos/{}'.format(file_name))
    df = pd.read_csv(file_path)
    return df

def consultar_bases():
    print("consultando bases de datos")
    df_barrios = leer_bdd('barrios.csv')
    df_dispositivos = leer_bdd('dispositivos.csv')
    df_clientes = leer_bdd('clientes.csv')
    print("bases de datos consultadas")
    return df_barrios, df_dispositivos, df_clientes

def dist_dict(df):
  #Esta función construye un diccionario donde la clave es el codigo del dispositivo y el valor son las coordenadas del mismo
  #Es una función auxiliar utilizada para la q4
  dist_dict = {}
  for i in range(0,len(df)):

    dist_dict[df['cod_dispositivo'].iloc[i]] = df['loc'].iloc[i]
  
  return dist_dict

def dist_matrix(dicc):
    #Esta función cosntruye una matriz donde los codigos de dispositivos están a lo largo de las columnas y los indices de las filas,
    #Donde cada valor representa la distancia entre ambos puntos utilizando la metodología de API Waze (calculando la distancia de un recorrido por carretera)
    #y utilizando la libreria geopy que calcula la distancia lineal entre esos dos puntos
    #Es una función auxiliar utilizada para la q4
    print("construyendo matrices de distancia")
    keys = list(dicc.keys())
    lista1 = keys.copy()
    lista2 = keys.copy()
    values = np.zeros((len(lista1),len(lista2)))
    values1 = np.zeros((len(lista1),len(lista2)))

    for loc0, value0 in tqdm(enumerate(dicc.values()), desc='Procesando', unit='its'):
        for loc1, value1 in enumerate(dicc.values()):
        
            if loc0 == loc1:
                route_dist = 0
                linear_dist = 0        
            else:
                from_address = value0
                to_address = value1

                route = wrc.WazeRouteCalculator(from_address, to_address)
                linear_dist = geodesic(from_address, to_address).kilometers
                try:
                    route_time, route_dist = route.calc_route_info()
                except wrc.WRCError as err:
                    print(err)

        
            values[(loc0),(loc1)] = route_dist
            values1[(loc0),(loc1)] = linear_dist

    df = pd.DataFrame(data=values, index=lista1, columns=lista2)
    df1 = pd.DataFrame(data=values1, index=lista1, columns=lista2)
    print("Matrices de distancia construidas con exito")
    return values, df, values1, df1

def sabana_datos(df_barrios, df_dispositivos, df_clientes):
    #Marcamos los codigos de dispositivos duplicados para que esta dimension tenga codigos unicos
    df_dispositivos['dup_validate'] = df_dispositivos.duplicated(subset='codigo', keep='first')
    #Filtramos el df y eliminamos la marcacion de duplicados
    df_dispositivos_clean = (
        df_dispositivos.copy()
        .query('dup_validate != True')
        .drop(['dup_validate'], axis=1)
    )
    #Realizamos el cruce para unir la columna del nombre del barrio a la tabla de dispositivos por medio del id del barrio
    df_tmp_merge = df_dispositivos_clean.merge(df_barrios, how='left', left_on=['id_barrio'], right_on=['codigo'], indicator=True)
    df_tmp_merge = df_tmp_merge.drop(['codigo_y', '_merge'], axis=1)
    df_tmp_merge = df_tmp_merge.rename(columns={'codigo_x':'codigo'})
    #Realizamos el cruce con la tabla de clientes para tener la sabana de datos completa
    df_sabana_datos = df_clientes.merge(df_tmp_merge, how='left', left_on=['cod_dispositivo'], right_on=['codigo'], indicator=True)
    print("sabana de datos consolidada exitosamente")
    return df_sabana_datos

#Solución Preguntas
#---------------------------------------------------------------------------------------------------------------
def q1(df_sabana_datos):
    df_sabana_datos = df_sabana_datos
    #Realizamos la consulta sobre el dataframe donde agrupamos por tipo de documento y realizamos un conteo de 
    #Los distintos barrios en los que el cliente ha tenido transaccion, identificandolos por el id_barrio
    query_q1 = leer_query('query_q1.sql')
    df_q1 = sqldf(query_q1, env=None)
    print("q1 resuelta de forma exitosa")
    return df_q1

def q2(df_sabana_datos):
    df_sabana_datos = df_sabana_datos
    #Concatenamos el tipo de documento y el numero de documento para asegurar que no van a haber falsos duplicados
    df_sabana_datos['client_key'] = df_sabana_datos['num_doc'].astype(str) + "_" + df_sabana_datos['tipo_doc'].astype(str)
    query_q2 = leer_query('query_q2.sql')
    df_q2 = sqldf(query_q2, env=None)
    print("q2 resuelta de forma exitosa")
    return df_q2

def q3(df_sabana_datos):
    df_sabana_datos = df_sabana_datos
    #En primera instancia identificamos el total de transacciones por cliente
    query_q3_1 = leer_query('query_q3_1.sql')
    df_q3_1 = sqldf(query_q3_1, env=None)
    #Posteriormente calculamos el numero de transacciones por cada cliente en cada canal
    query_q3_2 = leer_query('query_q3_2.sql')
    #Cruzamos los dos insumos anteriores y tenemos en una unica tabla el numero de transacciones por cliente por canal
    #y el numero total de transacciones, con estos valores podemos calcular el porcentaje de uso de cada canal sobre el total de transacciones
    #de cada cliente
    df_q3_2 = sqldf(query_q3_2, env=None).merge(df_q3_1, how='left', on=['num_doc'])
    df_q3_2['proporcion_uso_canal'] = df_q3_2['trx_canal'] / df_q3_2['total_trx']
    #Finalmente creamos un dataframe donde tenemos los clientes (unicos), el listado de canales que representan
    #más del 51% de sus transacciones separados por comas y la suma exacta de la proporcion que representan estos canales frente al total.
    df_q3 = df =pd.DataFrame(columns=["num_doc", "canales", "proporcion_uso"])
    #dicc_clientes_canales = {}
    for i in tqdm(df_q3_2['num_doc'].unique(), desc="Procesando", unit="its"):
        df_tmp = df_q3_2[df_q3_2['num_doc'] == i].sort_values(['proporcion_uso_canal'], ascending =[False])
        tmp_list = []
        tmp_sum = 0
        for row in range(0,len(df_tmp)):
            tmp_list.append(df_tmp.iloc[row]['canal'])
            tmp_sum += df_tmp.iloc[row]['proporcion_uso_canal']
            if tmp_sum >= 0.51:
                break
        new_row = [i, ','.join(tmp_list), tmp_sum]
        df_q3.loc[len(df_q3)] = new_row
        #dicc_clientes_canales[i] = tmp_list
    
    #for i in tqdm(dicc_clientes_canales.keys(), desc="Procesando", unit="its"):
    #    new_row = [i, ','.join(dicc_clientes_canales[i])]
    #    #df_q3 = df_q3.append(new_row, ignore_index=True)
    #    df_q3.loc[len(df_q3)] = new_row
    print("q3 resuelta de forma exitosa")
    return df_q3

def q4(df_sabana_datos):
    df_sabana_datos = df_sabana_datos
    #Para esto primero aislamos el barrio panamericano e identificamos los dispositivos unicos junto con sus ubicaciones
    query_q4_1 = leer_query('query_q4.sql')
    df_q4_1 = sqldf(query_q4_1, env=None)
    #Concatenamos la latitud y la longitud para tener las coordenadas en un unico campo
    df_q4_1['loc'] = df_q4_1['latitud'].astype(str) + ", " + df_q4_1['longitud'].astype(str)
    #llamamos las funciones auxiliares para construir el diccionario de las ubicaciones de los dispositivos del barrio
    #y para construir las matrices y dataframes que contienen las distancias
    loc_dict = dist_dict(df_q4_1)
    dist_matrix_waze, dist_df_waze, dist_matriz_linear, dist_df_linear = dist_matrix(loc_dict)
    #Finalmente las matrices sirven para algo más visual, pero para la respuesta de la q4 opté por crear en estructura tabular
    #un df que tenga para cada registro todas las combinaciones posibles de los otros dispositivos (id_codigo), para calcular
    #en la misma linea la distancia con la metodología de geopy y poder ordenar más facilmente los de mayor distancia
    df_result = pd.DataFrame([])
    for codigo in tqdm(df_q4_1['cod_dispositivo'], desc="Procesando", unit="its"):
        #Tomamos todos los valores menos el codigo a buscar
        aux = df_q4_1[df_q4_1['cod_dispositivo']!=codigo]
        #Tomamos el código a buscar
        row = df_q4_1[df_q4_1['cod_dispositivo']==codigo]
        #Asignamos una columna con el valor del código para tener en la misma fila el código consultado.
        aux['codigo_consultado'] = codigo
        aux['loc_consultado'] = row.iloc[0]['loc']
        
        #definimos la columna distancia en la que vamos a asignar el resultado de haber aplicado la función al df.
        aux['distancia'] = aux.apply(lambda fila: geodesic(row.iloc[0]['loc'], fila['loc']).kilometers,
                                    axis=1)
        #Agregamos el dataframe reducido a nuestro dataframe resultante.
        df_result = pd.concat([df_result, aux])

    #Ordenamos los resultados por la distancia de mayor a menor, y limitamos el df a los 20 primeros registros
    #(dado que por las combinaciones posibles la misma comparacion de dispositivos queda dos veces)
    df_q4_2 = df_result.sort_values(['distancia'], ascending =[False]).head(20)
    #Marcamos los registros repetidos para dejar unicamente los 10 dispositivos con mas distancia
    df_q4_2['dup_validation'] = df_q4_2.duplicated(subset='distancia', keep='first')
    #Filtramos para eliminar duplicados
    df_q4_2 = df_q4_2[df_q4_2['dup_validation'] == False].reset_index(drop=True)
    print("q4 resuelta de forma exitosa")
    return dist_df_waze, dist_df_linear, df_q4_2