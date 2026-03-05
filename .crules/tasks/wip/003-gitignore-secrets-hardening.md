# Task 003: .gitignore and Secret Prevention Hardening

**Type:** `chore`
**Priority:** High
**Version Bump:** Patch

## Description

Harden `.gitignore` per the GIT_POLICY secret prevention rules. Remove hardcoded fallback passwords from source code.

## Acceptance Criteria

- [ ] `.gitignore` contains entries for: `.env`, `.env.*`, `*.pem`, `*.key`, `credentials.json`
- [ ] `.gitignore` covers `dense_context.txt`, `graph_dump.json`, `training_data.txt`
- [ ] `recall.py` no longer has hardcoded `password123` fallback — uses empty string or raises error
- [ ] `check_memory.py` no longer has hardcoded `password123` fallback
- [ ] No staged file contains patterns matching GIT_POLICY secret regexes

## Notes

- The `.env` entry already exists but `.env.*` wildcard is missing.
- The hardcoded `password123` in `recall.py` and `check_memory.py` is a security smell even if it's a dev default.
