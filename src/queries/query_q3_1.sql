SELECT
    num_doc,
    SUM(num_trx) total_trx
FROM
    df_sabana_datos
GROUP BY
    num_doc