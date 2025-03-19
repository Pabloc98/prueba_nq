SELECT
    *
FROM(
    SELECT
        num_doc,
        COUNT(DISTINCT id_barrio) as barrios_con_trx
    FROM 
        df_sabana_datos
    WHERE 
        num_trx > 0
    GROUP BY 
        num_doc
)
WHERE 
    barrios_con_trx >= 5
ORDER BY 
    barrios_con_trx desc