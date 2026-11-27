"""Python kaynaklarından deterministik ZIP ve repo.tsv üretir. JSON düzenlenmez."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import re
import zipfile

ROOT = Path(__file__).resolve().parent
SECTION_FUNCTIONS = {"sonbolumler": "get_home", "diziler": "get_series", "filmler": "get_movies", "animeler": "get_animes"}
SECTIONS = tuple(SECTION_FUNCTIONS)

def validate_function(folder, module, function):
    file = folder / (module + ".py")
    if not file.is_file(): raise ValueError(f"{folder.name}: {file.name} eksik")
    tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    if not any(isinstance(node, ast.FunctionDef) and node.name == function for node in tree.body):
        raise ValueError(f"{folder.name}: {file.name} içinde def {function} gerekli")

def build():
    target = ROOT / "packages"
    target.mkdir(exist_ok=True)
    rows = ["ZEROIPTV-PYTHON-2"]
    for folder in sorted((ROOT / "plugins").iterdir()):
        if not (folder / "config.py").is_file(): continue
        spec = importlib.util.spec_from_file_location("build_config", folder / "config.py")
        cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
        if not cfg.ENABLED: continue
        assert re.fullmatch(r"[a-z][a-z0-9_]{0,49}", cfg.ID) and cfg.ID == folder.name
        assert isinstance(cfg.VERSION,int) and 0 < cfg.VERSION < 2147483647
        assert cfg.TYPE in ("series","movie","mixed")
        sections = [name for name in SECTIONS if (folder / (name + ".py")).is_file()]
        assert sections, f"{cfg.ID}: en az bir içerik dosyası gerekli"
        if not (folder / "__init__.py").is_file(): raise ValueError(f"{cfg.ID}: __init__.py eksik")
        for module, function in {**{name: SECTION_FUNCTIONS[name] for name in sections}, "search": "search", "detail": "get_details", "extractor": "resolve"}.items():
            validate_function(folder, module, function)
        package = f"zeroext_{cfg.ID}_v{cfg.VERSION}"
        relative = f"packages/{cfg.ID}-{cfg.VERSION}.zip"
        archive = ROOT / relative
        with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for file in sorted(folder.rglob("*.py")):
                if "__pycache__" in file.parts: continue
                entry = zipfile.ZipInfo(f"{package}/{file.relative_to(folder).as_posix()}", (2020,1,1,0,0,0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(entry, file.read_bytes())
        values = [cfg.ID,str(cfg.VERSION),cfg.NAME,cfg.TYPE,cfg.BASE_URL,",".join(cfg.PREVIOUS_HOSTS),",".join(sections),relative,hashlib.sha256(archive.read_bytes()).hexdigest()]
        assert all("\t" not in v and "\n" not in v and "\r" not in v for v in values)
        rows.append("\t".join(values))
    (ROOT / "repo.tsv").write_text("\n".join(rows)+"\n",encoding="utf-8")

if __name__ == "__main__": build()
