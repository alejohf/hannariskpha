import sys
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except Exception as e:
    print('Falta PyPDF2. Instale dependencias: pip install -r tools/requirements.txt')
    raise


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    texts = []
    for i, page in enumerate(reader.pages):
        try:
            texts.append(page.extract_text() or '')
        except Exception as e:
            texts.append('')
    return '\n\n'.join(texts)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python tools/extract_pdf_text.py <ruta_pdf> [ruta_salida]')
        sys.exit(2)
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f'Archivo no encontrado: {pdf_path}')
        sys.exit(3)
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('tools/extracted_text.txt')
    text = extract_text(pdf_path)
    out_path.write_text(text, encoding='utf-8')
    print(f'Texto extraído escrito en: {out_path}')
