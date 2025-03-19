SELECT
    num_doc,
    canal,
    SUM(num_trx) trx_canal
FROM
    df_sabana_datos
GROUP BY
    num_doc,
    canal