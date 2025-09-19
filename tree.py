import os

EXCLUDED_DIRS = {'.venv', '__pycache__', '.mypy_cache', '.pytest_cache', '.git'}
EXCLUDED_FILES_EXT = {'.pyc', '.pyo'}

def print_tree(startpath, level=0):
    try:
        items = sorted(os.listdir(startpath))
    except PermissionError:
        return

    for item in items:
        path = os.path.join(startpath, item)

        # Excluir directorios
        if os.path.isdir(path) and item in EXCLUDED_DIRS:
            continue

        # Excluir archivos con extensiones no deseadas
        if os.path.isfile(path) and os.path.splitext(item)[1] in EXCLUDED_FILES_EXT:
            continue

        print("    " * level + "|-- " + item)

        if os.path.isdir(path):
            print_tree(path, level + 1)

print_tree(".")