# E2E spec header

E2E framework: `.claude/rules/techstack.md`. Every generated spec starts with this provenance block. Uncited specs fail `/run-tests` Validate.

```ts
/**
 * Scope: {{sprint item / story pack}}
 * TC: {{case_id}}
 * AC / FR / BR: {{ids}}
 * Source: {{case body | OpenAPI operation | Figma node}}
 */
import { test, expect } from "@playwright/test"; // swap for the E2E framework's import if techstack.md changes
```

- One journey per AC cluster
- Use page objects from `../pages/`; do not inline brittle CSS
- Test data from `../data/`; fixtures from `../fixtures/`
- No secrets; synthetic data only
