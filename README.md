# 🛡️ TUDO CTF: White-Box Penetration Test Write-up

This repository documents the comprehensive security assessment and exploitation of the TUDO vulnerable web application (PHP / PostgreSQL). The project served as a white-box simulation, successfully chaining multiple critical vulnerabilities to achieve Remote Code Execution (RCE) and full administrative control.

## 🎯 Engagement Goal

The primary objective was to demonstrate the ability to identify, exploit, and document critical vulnerabilities in source code to achieve Remote Code Execution (RCE), aligned with advanced penetration-testing methodologies (e.g., OSWE / AWAE preparation).

## 🔎 Overview

This write-up contains a structured record of the assessment: the vulnerabilities discovered, the sequence used to exploit them, concrete reproduction steps, and recommended mitigations. It is intended for technical audiences (developers, security engineers, and red-teamers) and as study material for those preparing for practical web application security certifications.

## 📌 Scope

- **Target**: TUDO vulnerable web application (PHP + PostgreSQL)
- **Type**: White-box (source code available)
- **Goal**: Achieve Remote Code Execution (RCE) and administrative control via chained vulnerabilities

## 🛠️ Methodology

- **Source code review** — static analysis of PHP code, templates, and SQL usage.
- **Dynamic testing** — manual HTTP requests and targeted payloads to confirm behavior.
- **Exploit chaining** — combining multiple issues (logical flaws, input validation failures, unsafe deserialization / template injection, SQL issues, etc.) to escalate to RCE.
- **Post-exploitation** — validate persistence and administrative access without causing destructive impact.

## 🛡️ Recommended Remediation Mandate

To transition the TUDO application to a Secure-by-Design model, the following actions are mandatory:

- **Eliminate SQL Injection**: Implement Parameterized Queries across the entire application to ensure user input is treated as data and not code.
- **Restrict Privileges**: Revoke all filesystem and shell execution privileges from the PostgreSQL database user (Principle of Least Privilege).
- **Secure Uploads**: Adopt a strict whitelist for file extensions and rename all uploaded files to a cryptographically random, unique name.
- **Use CSPRNG**: Replace `srand()` and `rand()` with Cryptographically Secure Pseudo-Random Number Generators (CSPRNGs) (e.g., `random_bytes()`) for all security-sensitive tokens.
- **Mitigate Enumeration**: Ensure all authentication failures return a single, generic, ambiguous response.

## ⚔️ Final Remarks and Acknowledgements

This assessment confirms that the TUDO web application was fully compromised, demonstrating that its security model, based on blacklisting and passive checks, is critically flawed. The successful exploitation of the SQLi and File Upload flaws establishes two independent paths to Remote Code Execution, signifying a complete loss of server control.

The immediate mandate is to implement Secure-by-Design transformations, focusing on robust input validation and cryptographic security, to eliminate these fundamental classes of vulnerabilities.

A sincere thank you is extended to the author, William Moody (@bmdyy), for creating this realistic and challenging vulnerable application. TUDO is an exceptional tool for preparing for advanced certifications by enforcing deep, source code-level vulnerability analysis.
