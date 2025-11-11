import re
import sys
import os

def extract_prototypes(code):
    pattern = r'^prototype\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*(?:->\s*(\w+))?$'
    return re.findall(pattern, code, re.MULTILINE)

def make_stubs(prototypes):
    stubs = []
    for name, args, ret in prototypes:
        ret_annot = f" -> {ret}" if ret else ""
        stubs.append(f"def {name}({args}){ret_annot}:\n    pass\n")
    return "\n".join(stubs)

def remove_prototypes(code):
    return re.sub(r'^prototype.*$', '', code, flags=re.MULTILINE)

def split_code_sections(code):
    """Separate function defs from top-level code."""
    func_defs = []
    top_level = []
    lines = code.splitlines()
    in_def = False

    for line in lines:
        if line.strip().startswith("def "):
            in_def = True
            func_defs.append(line)
        elif in_def and (line.startswith(" ") or line.startswith("\t")):
            func_defs.append(line)
        else:
            in_def = False
            top_level.append(line)

    return "\n".join(func_defs), "\n".join(top_level)

def compile_pyproto(path):
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    prototypes = extract_prototypes(code)
    stubs = make_stubs(prototypes)
    clean_code = remove_prototypes(code)
    func_defs, top_level = split_code_sections(clean_code)

    # Phase 1: stubs + real functions
    definitions = stubs + "\n" + func_defs
    return definitions, top_level

def run_pyproto(path):
    defs, body = compile_pyproto(path)
    g = {}
    exec(defs, g)   # load stubs and real function defs
    exec(body, g)   # run main code (which may call the now-defined funcs)

def compile_to_py(path, out_path=None):
    defs, body = compile_pyproto(path)
    out_path = out_path or path.replace(".pyproto", "_compiled.py")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(defs + "\n" + body)
    print(f"Compiled to {out_path}")

def main():
    if len(sys.argv) < 3:
        print("Usage:\n  python main.py run <file.pyproto>\n  python main.py compile <file.pyproto>")
        return

    cmd, file = sys.argv[1], sys.argv[2]
    if not os.path.exists(file):
        print(f"File not found: {file}")
        return

    if cmd == "run":
        run_pyproto(file)
    elif cmd == "compile":
        compile_to_py(file)
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
