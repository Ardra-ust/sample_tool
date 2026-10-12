# L4-04-gate-blocks-forbidden-paths — Gate blocks forbidden paths

CODEOWNERS (or equivalent) protects the build/coverage-config files listed in `.claude/scope.yaml` `deny_gate_files` (e.g. pom.xml, jacoco.xml, pyproject.toml, package.json — whichever apply per `.claude/rules/techstack.md`), plus workflows and config.yaml.

Add project cases under `cases/<id>/` using the three-file or pointer format. Do not copy product-specific fixtures from other programs.
