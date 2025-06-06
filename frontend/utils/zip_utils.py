
import zipfile
import io

def extract_files(uploaded_file):
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        return {name: zip_ref.read(name).decode("utf-8", errors="ignore")
                for name in zip_ref.namelist()
                if name.endswith(('.py', '.js', '.java'))}
