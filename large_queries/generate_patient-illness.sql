WITH
    pats AS (SELECT array_agg("Номер мед. картки") AS arr FROM "Пацієнт"),
    dis AS (SELECT array_agg("Код") AS arr FROM "Хвороба")
INSERT INTO "Діагноз" ("Номер_пацієнта", "Код_хвороби", "Дата_Захворювання")
SELECT
    pats.arr[1 + trunc(random() * array_length(pats.arr, 1))::int],
    dis.arr[1 + trunc(random() * array_length(dis.arr, 1))::int],
    timestamp '2024-01-01 00:00:00' +
    (random() * (timestamp '2026-11-01 23:59:59' - timestamp '2024-01-01 00:00:00'))
FROM generate_series(1, %s) AS g(id)
CROSS JOIN pats
CROSS JOIN dis
WHERE pats.arr IS NOT NULL AND dis.arr IS NOT NULL
ON CONFLICT DO NOTHING;
