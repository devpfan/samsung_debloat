#!/bin/bash
echo "Buscando ruta de CustomTkinter..."
CTK_PATH=$(poetry run python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))")

echo "Compilando aplicación en un único archivo ejecutable (Linux Standalone)..."
poetry run pyinstaller --noconfirm \
    --onefile \
    --windowed \
    --add-data "$CTK_PATH:customtkinter/" \
    --add-data "src/core/bloatware_dict.json:src/core/" \
    --name SamsungDebloat \
    src/ui/app.py

echo "=========================================="
echo "¡COMPILACIÓN EXITOSA!"
echo "Tu ejecutable portátil está en: dist/SamsungDebloat"
echo "Cualquier persona con Linux puede ejecutar este archivo sin instalar Python."
