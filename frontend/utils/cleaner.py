import zipfile
import io
import os
import re

ALLOWED_EXT = {".js", ".py"}

def clean_code_content(zip_bytes: bytes, clean: bool = True):
    input_zip = zipfile.ZipFile(io.BytesIO(zip_bytes))
    output_buffer = io.BytesIO()
    file_cleaned, file_raw = {}, {}

    with zipfile.ZipFile(output_buffer, "w", zipfile.ZIP_DEFLATED) as output_zip:
        for file_info in input_zip.infolist():
            filename = file_info.filename
            ext = os.path.splitext(filename)[1].lower()
            if "node_modules" in filename or ext not in ALLOWED_EXT:
                continue
            with input_zip.open(file_info) as f:
                raw = f.read().decode("utf-8")
                file_raw[filename] = raw
                if clean:
                    raw = strip_comments(filename, raw)
                output_zip.writestr(filename, raw)
                file_cleaned[filename] = raw
    return output_buffer.getvalue(), file_cleaned, file_raw

def strip_comments(filename, content):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".js":
        content = re.sub(r'/\*[\s\S]*?\*/', '', content, flags=re.DOTALL)
    elif ext == ".py":
        content = re.sub(r'\"\"\"[\s\S]*?\"\"\"', '', content, flags=re.DOTALL)
        content = re.sub(r"\'\'\'[\s\S]*?\'\'\'", '', content, flags=re.DOTALL)
    lines = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith(('#', '//')):
            continue
        line = re.sub(r'#.*', '', line)
        line = re.sub(r'//.*', '', line)
        if line.strip():
            lines.append(line.strip())
    return '\n'.join(lines)
