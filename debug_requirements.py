#!/usr/bin/env python3
"""Debug script para requirements.txt"""

import os

req_path = "requirements.txt"

if os.path.exists(req_path):
    encodings_to_try = ["utf-8", "utf-16", "utf-16-le", "utf-16-be", "latin-1"]
    lines = []
    used_encoding = None

    for encoding in encodings_to_try:
        try:
            with open(req_path, "r", encoding=encoding) as f:
                lines = f.readlines()
            used_encoding = encoding
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if lines:
        print(f"Successfully read file with encoding: {used_encoding}")
        print(f"Total lines: {len(lines)}")

        # Filtrar líneas válidas
        packages = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                packages.append(line)

        print(f"Total packages: {len(packages)}")
        print(f"Django found: {any('django' in pkg.lower() for pkg in packages)}")
        print(f"First 10 packages: {packages[:10]}")

        # Buscar específicamente Django
        django_packages = [pkg for pkg in packages if "django" in pkg.lower()]
        print(f"Django packages found: {django_packages}")

    else:
        print("Could not read requirements.txt with any encoding")
else:
    print("requirements.txt not found")
