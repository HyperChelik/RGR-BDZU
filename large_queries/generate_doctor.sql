INSERT INTO "Лікар" ("Ліцензія", "ПІБ", "Спеціалізація")
SELECT
    (trunc(random() * 900 + 100)::int)::text ||
    chr(trunc(65 + random() * 25)::int) ||
    chr(trunc(65 + random() * 25)::int) ||
    chr(trunc(65 + random() * 25)::int),
    (array['Іваненко', 'Петренко', 'Коваленко', 'Бондаренко', 'Ткаченко', 'Кравченко', 'Шевченко', 'Мельник'])[1 + trunc(random() * 8)::int]
    || ' ' ||
    chr(ASCII('А') + trunc(random() * (ASCII('Ф') - ASCII('А')))::int) || '. ' || chr(ASCII('А') + trunc(random() * (ASCII('Ф') - ASCII('А')))::int) || '.',
    (array['Терапевт', 'Хірург', 'Кардіолог', 'Невролог', 'Педіатр', 'Офтальмолог', 'Отоларинголог'])[1 + trunc(random() * 7)::int]
FROM generate_series(1, %s) AS g(id)
ON CONFLICT DO NOTHING
