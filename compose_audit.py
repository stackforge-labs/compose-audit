#!/usr/bin/env python3
"""compose-audit: lint docker-compose files for common self-hosting mistakes.

Dependency-free (line-based, no YAML parser). Usage: compose_audit.py FILE [FILE...]
Exit code 1 if any finding. Written by an AI agent (Whopper-Agent / StackForge Labs).
"""
import re, sys

RULES = [
    (re.compile(r'^\s*image:\s*["\']?[^\s"\'#:]+["\']?\s*(#.*)?$'), "image has no tag (defaults to :latest) - pin a version"),
    (re.compile(r'^\s*image:\s*["\']?\S+:latest\b'), "image uses :latest - pin a version"),
    (re.compile(r'^\s*privileged:\s*true'), "privileged: true gives the container full host access"),
    (re.compile(r'^\s*network_mode:\s*["\']?host'), "network_mode: host removes network isolation"),
    (re.compile(r'^\s*-\s*["\']?/var/run/docker\.sock'), "docker.sock mounted - container can control the host"),
    (re.compile(r'^\s*-\s*["\']?(\d{1,5}):\d+'), "port published on all interfaces - bind to 127.0.0.1:HOST:CONTAINER unless intended"),
    (re.compile(r'^\s*(\w*(PASSWORD|SECRET|TOKEN|KEY)\w*)\s*[:=]\s*["\']?(?!\$)\S+', re.I), "possible hardcoded secret - use env_file or secrets"),
]

def audit(path):
    out, svc_has_restart, cur = [], {}, None
    with open(path) as f:
        lines = f.read().splitlines()
    in_services = False
    for n, line in enumerate(lines, 1):
        if re.match(r'^services:\s*$', line):
            in_services = True; continue
        if re.match(r'^\S', line) and in_services:
            in_services = False
        m = re.match(r'^  (\w[\w.-]*):\s*$', line)
        if in_services and m:
            cur = m.group(1); svc_has_restart[cur] = (n, False)
        if cur and re.match(r'^\s+restart:', line):
            svc_has_restart[cur] = (svc_has_restart[cur][0], True)
        if line.strip().startswith('#'):
            continue
        for rx, msg in RULES:
            if rx.match(line):
                if msg.startswith("image has no tag") and ':' in line.split('image:',1)[1]:
                    continue
                out.append((n, msg))
    for s, (n, ok) in svc_has_restart.items():
        if not ok:
            out.append((n, f"service '{s}' has no restart policy"))
    return sorted(out)

if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:] or ["docker-compose.yml"]:
        for n, msg in audit(p):
            print(f"{p}:{n}: {msg}"); bad += 1
    sys.exit(1 if bad else 0)
