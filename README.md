# compose-audit

Tiny, dependency-free linter for `docker-compose.yml` files. Flags common self-hosting mistakes:
unpinned / `:latest` images, `privileged`, host networking, mounted `docker.sock`,
ports published on all interfaces, hardcoded secrets, missing restart policy.

```
python3 compose_audit.py docker-compose.yml
```
Exit code 1 if anything is found (usable in CI). Try it on `example-bad.yml`.

Line-based heuristics, not a YAML parser, so expect some false positives/negatives. MIT licensed.
Made by an AI agent (Whopper-Agent) for StackForge Labs. More self-hosting templates: https://github.com/stackforge-labs/selfhost-starter
