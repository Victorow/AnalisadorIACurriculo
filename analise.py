import uuid
import sys
from concurrent.futures import ThreadPoolExecutor
from helper import extract_data_analysis, get_pdf_paths, read_pdf
from database import AnalyseDatabase
from ai import GroqClient
from models.resum import Resum
from models.file import File

# Verifica se a vaga foi passada como argumento
if len(sys.argv) < 2:
    print("Por favor, forneça o nome da vaga como argumento.")
    sys.exit(1)

job_name = sys.argv[1]  # Obtém o nome da vaga a partir dos argumentos
database = AnalyseDatabase()
ai = GroqClient()
job = database.get_job_by_name(job_name)  # Usa o nome da vaga fornecido

if job is None:
    print(f"Vaga '{job_name}' não encontrada no banco de dados.")
    sys.exit(1)

print(f"Iniciando análise para a vaga: {job_name}")

cv_paths = get_pdf_paths(dir='curriculos')

if not cv_paths:
    print("Nenhum currículo encontrado no diretório 'curriculos'.")
    sys.exit(1)

def process_cv(path):
    try:
        content = read_pdf(path)
        resum = ai.resume_cv(content)
        opinion = ai.generate_opnion(content, job)
        score = ai.generate_score(content, job)

        resum_schema = Resum(
            id=str(uuid.uuid4()),
            job_id=job.get('id'),
            content=resum,
            file=str(path),
            opinion=opinion
        )
        
        file_schema = File(
            file_id=str(uuid.uuid4()),
            job_id=job.get('id'),
        )

        analysis_schema = extract_data_analysis(resum, job.get('id'), resum_schema.id, score)

        database.resume.insert(resum_schema.model_dump())
        database.analysis.insert(analysis_schema.model_dump())
        database.files.insert(file_schema.model_dump())

        print(f"Análise concluída para o currículo: {path}")

    except Exception as e:
        print(f"Erro ao processar o currículo '{path}': {e}")

# Usando ThreadPoolExecutor para processar currículos em paralelo
with ThreadPoolExecutor() as executor:
    executor.map(process_cv, cv_paths)