SELECT
    nombre as nombre_barrio,
    COUNT(DISTINCT marcacion_pac) q_clientes_unicos_pac,
    COUNT(DISTINCT client_key) q_clientes_unicos_barrio
FROM (   
    SELECT
        *,
        CASE
        WHEN canal = 'PAC'
        THEN client_key
        ELSE null END as marcacion_pac
    FROM
        df_sabana_datos)
GROUP BY 
    nombre
ORDER BY 
    q_clientes_unicos_pac desc
LIMIT 6