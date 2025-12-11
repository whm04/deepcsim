import os


def get_file_type(filename: str, is_dir: bool) -> str:
    if is_dir:
        return 'folder'
    ext = os.path.splitext(filename)[1].lower()
    type_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.md': 'markdown',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image',
        '.svg': 'image'
    }
    return type_map.get(ext, 'file')
