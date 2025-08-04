# 🔧 **GUÍA COMPLETA DE PRE-COMMIT HOOKS**

## 🎯 **¿QUÉ SON LOS PRE-COMMIT HOOKS?**

Los **pre-commit hooks** son scripts que se ejecutan automáticamente **antes** de cada commit para:

- ✅ **Formatear código** automáticamente (Black, isort)
- ✅ **Detectar errores** de sintaxis y estilo (Flake8, MyPy)
- ✅ **Eliminar código innecesario** (autoflake)
- ✅ **Verificar seguridad** (Bandit)
- ✅ **Mantener consistencia** en el equipo

## 🚀 **CONFIGURACIÓN INICIAL (Solo una vez)**

### **1. Instalar dependencias:**
```bash
pip install pre-commit black isort flake8 mypy bandit
```

### **2. Instalar hooks en el repositorio:**
```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

### **3. Verificar instalación:**
```bash
pre-commit --version
```

---

## 💻 **USO DIARIO (Para cada commit)**

### **Opción 1: Automático (Recomendado)**
```bash
# 1. Hacer cambios en tu código
# 2. Stagear archivos
git add .

# 3. Hacer commit (pre-commit se ejecuta automáticamente)
git commit -m "feat: agregar nueva funcionalidad"
```

### **Opción 2: Manual (Para verificar antes)**
```bash
# Ejecutar pre-commit manualmente
pre-commit run --all-files

# Si todo está bien, hacer commit normal
git add .
git commit -m "feat: agregar nueva funcionalidad"
```

### **Opción 3: Script asistente**
```bash
# Usar nuestro script helper
python make_commit.py
```

---

## 🛠️ **HERRAMIENTAS CONFIGURADAS**

| Herramienta | Función | Se ejecuta en |
|-------------|---------|---------------|
| **🧹 Autoflake** | Elimina imports no usados | Código fuente |
| **🎨 Black** | Formatea código Python | Código fuente |
| **📚 Isort** | Ordena imports | Código fuente |
| **🔍 Flake8** | Detecta errores de estilo | Código fuente |
| **⚡ MyPy** | Verifica tipos | Código fuente |
| **🛡️ Bandit** | Detecta vulnerabilidades | Código fuente |
| **📝 Commitizen** | Valida mensajes de commit | Mensajes |

---

## 📁 **ARCHIVOS EXCLUIDOS**

Los hooks **NO** se ejecutan en:
- `test/` y `tests/` (archivos de testing)
- `migrations/` (migraciones de Django)
- `__pycache__/` (archivos compilados)
- `.venv/` y `env/` (entornos virtuales)

---

## ⚠️ **QUÉ HACER SI FALLA PRE-COMMIT**

### **Caso 1: Errores de formateo**
```bash
# Pre-commit corrige automáticamente, solo necesitas:
git add .  # Reagregar archivos corregidos
git commit -m "tu mensaje"  # Volver a hacer commit
```

### **Caso 2: Errores de MyPy (tipos)**
```python
# Antes (sin tipo):
def get_user(id):
    return User.objects.get(id=id)

# Después (con tipo):
def get_user(id: int) -> User:
    return User.objects.get(id=id)
```

### **Caso 3: Errores de Flake8 (estilo)**
```python
# Antes (línea muy larga):
result = very_long_function_name(parameter1, parameter2, parameter3, parameter4)

# Después (dividida):
result = very_long_function_name(
    parameter1, parameter2,
    parameter3, parameter4
)
```

### **Caso 4: Saltar hooks (NO recomendado)**
```bash
# Solo en emergencias:
git commit --no-verify -m "emergency fix"
```

---

## 🎯 **COMANDOS ÚTILES**

### **Ejecutar herramientas manualmente:**
```bash
# Solo Black (formateo)
black --line-length 88 .

# Solo isort (imports)
isort --profile black .

# Solo Flake8 (linting)
flake8 --max-line-length=88 .

# Solo MyPy (tipos)
mypy src/

# Solo Bandit (seguridad)
bandit -r src/
```

### **Actualizar hooks:**
```bash
pre-commit autoupdate
```

### **Ejecutar hooks específicos:**
```bash
pre-commit run black
pre-commit run flake8
pre-commit run mypy
```

---

## 🔧 **CONFIGURACIÓN PERSONALIZADA**

### **Desactivar hook específico temporalmente:**
```yaml
# En .pre-commit-config.yaml, agregar:
- repo: https://github.com/psf/black
  rev: 24.4.2
  hooks:
    - id: black
      stages: [manual]  # Solo manual, no automático
```

### **Excluir archivos específicos:**
```yaml
- repo: https://github.com/psf/black
  rev: 24.4.2
  hooks:
    - id: black
      exclude: ^(specific_file\.py|another_file\.py)$
```

---

## 📊 **BENEFICIOS PARA EL EQUIPO**

### ✅ **Antes de Pre-commit:**
- ❌ Código con estilos diferentes
- ❌ Imports desordenados
- ❌ Errores de tipado
- ❌ Vulnerabilidades no detectadas
- ❌ Discusiones sobre formato en code reviews

### ✅ **Con Pre-commit:**
- ✅ Código consistente automáticamente
- ✅ Imports ordenados siempre
- ✅ Tipos verificados
- ✅ Seguridad validada
- ✅ Code reviews enfocados en lógica

---

## 🚨 **REGLAS DEL EQUIPO**

1. **🚫 NO hacer `--no-verify`** sin autorización
2. **✅ Siempre** ejecutar pre-commit antes de PR
3. **📝 Usar** mensajes de commit descriptivos
4. **🔧 Reportar** problemas de configuración al líder
5. **📚 Mantener** dependencias actualizadas

---

## 🎉 **¡FELICIDADES!**

Ya tienes configurado un sistema profesional de control de calidad que:
- **Mejora la calidad** del código automáticamente
- **Mantiene consistencia** en el equipo
- **Previene errores** antes del deploy
- **Facilita code reviews** más eficientes

**¡Tu código ahora es más profesional y mantenible!** 🚀
