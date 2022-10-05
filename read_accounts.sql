SELECT (o.first_name || ' ' || o.last_name) AS owner_name, 
    a.name AS account_name, 
    b.name AS bank_name,
    b.account_number AS bank_number,
    SUM(t.amount) AS actual_balance
FROM accounts AS a 
INNER JOIN banks AS b ON a.bank_id = b.id
INNER JOIN owners AS o ON a.owner_id = o.id
INNER JOIN transactions AS t ON t.account_id = a.id
WHERE a.user_id = 1
GROUP BY t.account_id
;

SELECT (o.first_name || ' ' || o.last_name) AS owner_name, 
    a.name AS account_name, 
    b.name AS bank_name,
    b.account_number AS bank_number,
    IFNULL(SUM(t.amount), 0) AS actual_balance
FROM accounts AS a 
INNER JOIN banks AS b ON a.bank_id = b.id
INNER JOIN owners AS o ON a.owner_id = o.id
LEFT JOIN transactions AS t ON t.account_id = a.id
WHERE a.user_id = 1
GROUP BY t.account_id
ORDER BY owner_name, account_name
;

SELECT (o.first_name || ' ' || o.last_name) AS owner_name, 
    a.name AS account_name, 
    b.name AS bank_name,
    b.account_number AS bank_number,
    IFNULL(SUM(t.amount), 0) AS actual_balance
FROM accounts AS a 
INNER JOIN banks AS b ON a.bank_id = b.id
INNER JOIN owners AS o ON a.owner_id = o.id
LEFT JOIN transactions AS t ON t.account_id = a.id
WHERE a.user_id = 1
GROUP BY a.id
ORDER BY owner_name, account_name
;