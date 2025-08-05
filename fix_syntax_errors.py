#!/usr/bin/env python
"""
Script para arreglar errores de sintaxis comunes             # Solo escribir si hay cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("  ✅ Corregido exitosamente")
            else:
                print("  ✅ Sin cambios necesarios")ivos de test.
Corrige paréntesis mal cerrados y strings no terminados.
"""
import os
import re


def fix_syntax_errors():
    """Arregla errores de sintaxis comunes en archivos de test."""

    # Patrones de errores comunes
    patterns = [
        # assert method( == value -> assert method() == value
        (r"assert (.+?)\.is_valid\(\s+==\s+(.+?)\)", r"assert \1.is_valid() == \2"),
        (r"assert (.+?)\.count\(\s+>=\s+(.+?)\)", r"assert \1.count() >= \2"),
        (r"assert (.+?)\.first\(\.(.+?)\)", r"assert \1.first().\2"),
        # Strings no terminados con color hex
        (
            r'"color_hex"] == "\s+#\s+nosec B101',
            r'"color_hex"] == "#FF0000"  # nosec B101',
        ),
        (
            r'assert representation\["color_hex"\] == "\s+#\s+nosec B101',
            r'assert representation["color_hex"] == "#FF0000"  # nosec B101',
        ),
    ]

    # Archivos con errores reportados
    files_to_fix = [
        "test/albums/api/test_serializers.py",
        "test/albums/infrastructure/test_models.py",
        "test/genres/api/test_serializers.py",
        "test/genres/infrastructure/test_models.py",
        "test/songs/test_models_direct.py",
    ]

    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            print(f"⚠️ Archivo no encontrado: {file_path}")
            continue

        print(f"🔧 Arreglando: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Aplicar patrones de corrección
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            # Arreglos específicos adicionales
            content = content.replace(
                "assert serializer_empty.is_valid( == False)",
                "assert serializer_empty.is_valid() == False)",
            )
            content = content.replace(
                "assert search_serializer_long.is_valid( == False)",
                "assert search_serializer_long.is_valid() == False)",
            )
            content = content.replace(
                "assert serializer_color.is_valid( == True)",
                "assert serializer_color.is_valid() == True)",
            )
            content = content.replace(
                'assert genre_entity.color_hex == "  # nosec B101',
                'assert genre_entity.color_hex == "#FF0000"  # nosec B101',
            )
            content = content.replace(
                'assert representation["color_hex"] == "  # nosec B101',
                'assert representation["color_hex"] == "#FF0000"  # nosec B101',
            )

            # Solo escribir si hay cambios
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print("  ✅ Corregido exitosamente")
            else:
                print("  ✅ Sin cambios necesarios")

        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    fix_syntax_errors()
    print("\n🎉 Corrección de errores de sintaxis completada")
