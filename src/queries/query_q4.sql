SELECT DISTINCT
    canal,
    cod_dispositivo,
    latitud,
    longitud
FROM
    df_sabana_datos
WHERE
    nombre LIKE '%Panamericano%'