"""Tek dosyalık Python eklentilerinden ZIP + TSV üretir (SDK 3)."""
from pathlib import Path
from urllib.parse import urlsplit
import ast
import hashlib
import re
import zipfile

ROOT = Path(__file__).resolve().parent
SECTION_FUNCTIONS = {"sonbolumler": "get_home", "diziler": "get_series", "filmler": "get_movies", "animeler": "get_animes"}
REQUIRED = ("search", "get_details", "resolve")
METADATA = ("ID", "NAME", "VERSION", "TYPE", "BASE_URL", "PREVIOUS_HOSTS", "ENABLED")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def inspect_source(file):
    tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file), feature_version=(3, 11))
    cfg = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [x.id for x in node.targets if isinstance(x, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        else:
            continue
        for name in names:
            if name in METADATA:
                require(name not in cfg, f"{file.name}: {name} tekrarlanmış")
                cfg[name] = ast.literal_eval(node.value)
    require(set(cfg) == set(METADATA), f"{file.name}: metadata eksik: {set(METADATA)-set(cfg)}")
    require(type(cfg['ENABLED']) is bool, f"{file.name}: ENABLED bool olmalı")
    if not cfg['ENABLED']:
        return cfg, []
    require(isinstance(cfg['ID'], str) and re.fullmatch(r"[a-z][a-z0-9_]{0,49}", cfg['ID']) and cfg['ID'] == file.stem, f"{file.name}: ID hatalı")
    require(type(cfg['VERSION']) is int and 0 < cfg['VERSION'] < 2147483647, f"{file.name}: VERSION hatalı")
    require(isinstance(cfg['NAME'], str) and 1 <= len(cfg['NAME']) <= 100, f"{file.name}: NAME hatalı")
    require(cfg['TYPE'] in ('series','movie','mixed'), f"{file.name}: TYPE hatalı")
    u = urlsplit(cfg['BASE_URL'])
    require(u.scheme == 'https' and u.hostname and not u.username and not u.password and not u.path and not u.query and not u.fragment and u.port is None, f"{file.name}: BASE_URL yalnız HTTPS origin olmalı")
    require(isinstance(cfg['PREVIOUS_HOSTS'], (list,tuple)) and all(isinstance(h,str) and re.fullmatch(r'[a-zA-Z0-9.-]+',h) for h in cfg['PREVIOUS_HOSTS']), f"{file.name}: PREVIOUS_HOSTS hatalı")
    funcs = {}
    known = set(SECTION_FUNCTIONS.values()) | set(REQUIRED)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in known:
            require(isinstance(node, ast.FunctionDef) and node.name not in funcs, f"{file.name}: {node.name} tek bir normal def olmalı")
            a = node.args
            expected = 2
            require(len(a.posonlyargs)+len(a.args)==expected and not a.vararg and not a.kwarg and not a.kwonlyargs, f"{file.name}: {node.name} iki parametre almalı")
            funcs[node.name] = node
    sections = [section for section, fn in SECTION_FUNCTIONS.items() if fn in funcs]
    require(sections, f"{file.name}: en az bir içerik fonksiyonu gerekli")
    require(set(REQUIRED) <= funcs.keys(), f"{file.name}: zorunlu fonksiyon eksik: {set(REQUIRED)-funcs.keys()}")
    return cfg, sections

def build():
    target = ROOT / 'packages'; target.mkdir(exist_ok=True)
    rows = ['ZEROIPTV-PYTHON-3']
    common = ROOT / 'common'
    helpers = sorted(common.glob('*.py')) if common.is_dir() else []
    if helpers:
        require((common/'__init__.py').is_file(), 'common/__init__.py eksik')
    for helper in helpers:
        ast.parse(helper.read_text(encoding='utf-8'), filename=str(helper), feature_version=(3,11))
    for file in sorted((ROOT/'plugins').glob('*.py')):
        if file.name.startswith('_'): continue
        cfg, sections = inspect_source(file)
        if not cfg['ENABLED']: continue
        ident, ver = cfg['ID'], cfg['VERSION']
        package = f'zeroext_{ident}_v{ver}'
        relative = f'packages/{ident}-{ver}.zip'
        archive = ROOT/relative
        entries = [(f'{package}/__init__.py',file.read_bytes())] + [(f'{package}/common/{h.name}',h.read_bytes()) for h in helpers]
        require(len(entries)<=100 and all(len(data)<=500_000 for _,data in entries) and sum(len(data) for _,data in entries)<=2_000_000, f'{ident}: paket çok büyük')
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,data in entries:
                entry = zipfile.ZipInfo(name,(2020,1,1,0,0,0)); entry.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(entry,data)
        require(archive.stat().st_size<=2_000_000, f'{ident}: ZIP çok büyük')
        values = [ident,str(ver),cfg['NAME'],cfg['TYPE'],cfg['BASE_URL'],','.join(cfg['PREVIOUS_HOSTS']),','.join(sections),relative,hashlib.sha256(archive.read_bytes()).hexdigest()]
        require(all('\t' not in v and '\n' not in v and '\r' not in v for v in values),f'{ident}: geçersiz TSV alanı')
        rows.append('\t'.join(values))
    require(len(rows)<=101,'En fazla 100 eklenti desteklenir')
    (ROOT/'repo.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')

if __name__ == '__main__': build()
