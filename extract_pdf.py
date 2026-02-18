import sys
try:
    from pdfminer.high_level import extract_text
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfminer.six"])
    from pdfminer.high_level import extract_text

pdf_path = r'd:\work\linkedIn\Glimpse Tech\trail2\Pythom Developer Intern Assignment.pdf'
text = extract_text(pdf_path)
with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print("Extracted text saved to requirements.txt")

