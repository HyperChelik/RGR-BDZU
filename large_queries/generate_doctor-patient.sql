WITH
    docs AS (SELECT array_agg("Ліцензія") AS arr FROM "Лікар"),
    pats AS (SELECT array_agg("Номер мед. картки") AS arr FROM "Пацієнт")
INSERT INTO "Запис" ("Ліцензія_лікаря", "Номер_пацієнта", "Дата_запису")
SELECT
    docs.arr[1 + floor(random() * array_length(docs.arr, 1))::int],
    pats.arr[1 + floor(random() * array_length(pats.arr, 1))::int],
    timestamp '2024-01-01 08:00:00' +
    (random() * (timestamp '2026-12-31 18:00:00' - timestamp '2024-01-01 08:00:00'))
FROM generate_series(1, %s) AS g(id)
CROSS JOIN docs
CROSS JOIN pats
WHERE docs.arr IS NOT NULL AND pats.arr IS NOT NULL
ON CONFLICT DO NOTHING;