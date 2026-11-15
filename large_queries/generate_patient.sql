INSERT INTO "Пацієнт" ("Номер мед. картки", "ПІБ")
SELECT
    chr(trunc(65 + random() * 25)::int) ||
    chr(trunc(65 + random() * 25)::int) ||
    chr(trunc(65 + random() * 25)::int) ||
    (trunc(random() * 900 + 100)::int)::text,
    (array['Іваненко', 'Петренко', 'Коваленко', 'Бондаренко', 'Ткаченко', 'Кравченко', 'Шевченко', 'Мельник'])[1 + trunc(random() * 8)::int]
    || ' ' ||
    chr(ASCII('А') + trunc(random() * (ASCII('Ф') - ASCII('А')))::int) || '. ' || chr(ASCII('А') + trunc(random() * (ASCII('Ф') - ASCII('А')))::int) || '.'
FROM generate_series(1, %s) AS g(id)
ON CONFLICT DO NOTHING
