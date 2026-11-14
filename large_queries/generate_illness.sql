INSERT INTO "Хвороба" ("Код", "Назва")
SELECT
    chr(trunc(65 + random() * 25)::int) ||
    (trunc(random() * 9)::int)::text ||
    chr(trunc(65 + random() * 25)::int) ||
    (trunc(random() * 9)::int)::text ||
    chr(trunc(65 + random() * 25)::int) ||
    (trunc(random() * 9)::int)::text,
    (array['Гострий бронхіт', 'Гіпертонічна хвороба', 'Мігрень', 'Гастрит', 'Аритмія', 'Пневмонія', 'Синусит'])[1 + floor(random() * 7)::int]
                        || ' (тип ' || g.id::text || ')'
FROM generate_series(1, %s) AS g(id)
ON CONFLICT DO NOTHING
