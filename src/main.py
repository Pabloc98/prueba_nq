from utils import consultar_bases, sabana_datos, q1, q2, q3, q4
import warnings
warnings.filterwarnings('ignore')

#Consultamos las bases ubicadas en el directorio 'datos'
df_barrios, df_dispositivos, df_clientes = consultar_bases()

#Llamamos la función que limpia y cruza las bases para formar la sabana de datos a trabajar
df_sabana = sabana_datos(df_barrios, df_dispositivos, df_clientes)

#Llamamos la función que resuelve la pregunta uno y nos arroja el dataFrame con el listado de clientes
#con transacciones en 5 o más barrios
df_q1 = q1(df_sabana)

#Llamamos la función que resuelve la pregunta dos y nos arroja el dataFrame con el listado de los 6 barrios
#donde la mayor cantidad de clientes únicos realizan transacciones por dispositivo tipo PAC
df_q2 = q2(df_sabana)

#Llamamos la función que resuelve la pregunta tres y nos arroja el diccionario donde tenemos en las llaves
#los clientes (unicos) y en los valores el listado de canales que representan más del 51% de sus transacciones
df_q3 = q3(df_sabana)

#Llamamos la función que resuelve la pregunta dos y nos arroja tres dataFrames, el primero con la matriz de distancias calculadas
#con la api de Waze, el segundo con matriz de distancias calculadas con geoPy y por ultimo el listado de los
#10 dispositivos únicos con mayor distancia entre si
dist_df_waze, dist_df_linear, df_q4 = q4(df_sabana)

#Exportamos todo a excel y json para alimentar el tablero
df_sabana.to_excel('sabana.xlsx', index=False)
df_q1.to_excel('q1.xlsx', index=False)
df_q2.to_excel('q2.xlsx', index=False)
df_q3.to_excel('q3.xlsx', index=False)
dist_df_waze.to_excel('matriz_dist_waze.xlsx', index=False)
dist_df_linear.to_excel('matriz_dist_lineal.xlsx', index=False)
df_q4.to_excel('q4.xlsx', index=False)