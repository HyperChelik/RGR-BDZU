WITH
    docs AS (SELECT array_agg("Ліцензія") AS arr FROM "Лікар"),
    ills AS (SELECT array_agg("Код") AS arr FROM "Хвороба")
INSERT INTO "Лікування" ("Ліцензія_лікаря", "Код_хвороби")
SELECT
    docs.arr[1 + trunc(random() * array_length(docs.arr, 1))::int],
    ills.arr[1 + trunc(random() * array_length(ills.arr, 1))::int]
FROM generate_series(1, %s) AS g(id)
CROSS JOIN docs
CROSS JOIN ills
WHERE docs.arr IS NOT NULL AND ills.arr IS NOT NULL
ON CONFLICT DO NOTHING;
