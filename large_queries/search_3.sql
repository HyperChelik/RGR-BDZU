SELECT
    d."Ліцензія",
    d."ПІБ",
    d."Спеціалізація",
    COUNT(z."Номер_пацієнта") AS "Кількість_прийомів",
    COUNT(DISTINCT z."Номер_пацієнта") AS "Унікальних_пацієнтів"
FROM "Лікар" d
INNER JOIN "Запис" z ON d."Ліцензія" = z."Ліцензія_лікаря"
WHERE d."ПІБ" LIKE %s
  AND z."Дата_запису" BETWEEN %s AND %s
GROUP BY d."Ліцензія", d."ПІБ", d."Спеціалізація"
HAVING COUNT(z."Номер_пацієнта") BETWEEN %s AND %s
ORDER BY "Кількість_прийомів" DESC
LIMIT 100;
