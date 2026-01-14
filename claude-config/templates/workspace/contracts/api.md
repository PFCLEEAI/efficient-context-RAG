# API Contract v1.0

## Overview
This document defines the API contract between Frontend and Backend teams.
**Owner**: @backend-lead
**Consumers**: @frontend-lead, @test-lead

## Base URL
```
Development: http://localhost:3000/api
Production: https://api.example.com
```

## Authentication
All protected endpoints require:
```
Authorization: Bearer <token>
```

## Endpoints

<!-- Add endpoints below -->

## Error Codes
| Code | Meaning |
|------|---------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Server Error |

## Changelog
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | {DATE} | Initial contract |
