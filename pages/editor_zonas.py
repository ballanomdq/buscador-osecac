# ==================== INSPECCIONAR CAMPOS ====================
from fillpdf import fillpdfs
import json

pdf_path = "PLANILLA INSPECTORES.pdf"   # pon el archivo en la misma carpeta

print("🔍 Analizando campos del PDF...\n")
campos = fillpdfs.get_form_fields(pdf_path)

# Guardar en un archivo bonito para que lo veas fácil
with open("campos_del_formulario.json", "w", encoding="utf-8") as f:
    json.dump(campos, f, indent=4, ensure_ascii=False)

print(f"Se encontraron {len(campos)} campos.")
print("\nNombres de los campos:")
for nombre in sorted(campos.keys()):
    print(f"→ {nombre}")
