import re, uuid, os
import fitz
from models.analysis import Analysis

def read_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf: 
            text += page.get_text()

    return text

def get_pdf_paths(dir):
    pdf_paths = []

    for filename in os.listdir(dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(dir, filename)
            pdf_paths.append(file_path)

    return pdf_paths

def extract_data_analysis(resum_cv, job_id, resum_id, score) -> Analysis:
    secoes_dict = {
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "resum_id": resum_id,
        "name": "",
        "skills": [],
        "education": [],
        "language": [],
        "score": score
    }

    patterns = {
        "name": r"(?:## Nome Completo\s*|Nome Completo\s*\|\s*Valor\s*\|\s*\S*\s*\|\s*)(.*)",
        "skills": r"## Habilidades\s*([\s\S]*?)(?=##|$)",
        "education": r"## Educação\s*([\s\S]*?)(?=##|$)",
        "language": r"## Idiomas\s*([\s\S]*?)(?=##|$)",
        "salary_expectation": r"## Pretensão Salarial\s*([\s\S]*?)(?=##|$)"
    }

    def clean_string(string: str) -> str:
        return re.sub(r"[\*\-]+", "", string).strip()
    
    for secao, pattern in patterns.items():
        match = re.search(pattern, resum_cv)
        if match:
            if secao == "name":
                secoes_dict[secao] = clean_string(match.group(1))
            else:
                secoes_dict[secao] = [clean_string(item) for item in match.group(1).split('\n') if item.strip()]


    # Validação para garantir que nenhuma seção obrigatória esteja vazia
    for key in ["name", "education", "skills"]:
        if not secoes_dict[key] or (isinstance(secoes_dict[key], list) and not any(secoes_dict[key])):
            raise ValueError(f"A seção '{key}' não pode ser vazia ou uma string vazia.")

    return Analysis(**secoes_dict)

