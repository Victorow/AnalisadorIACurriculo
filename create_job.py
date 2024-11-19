import uuid
from models.job import job
from database import AnalyseDatabase

database = AnalyseDatabase()

def create_job(name, main_activities, prerequisites, differentials):
    # Cria uma nova instância do modelo de vaga
    new_job = job(
        id=str(uuid.uuid4()),
        name=name,
        main_activities=main_activities,
        prerequisites=prerequisites,
        differentials=differentials
    )
    
    # Insere a nova vaga no banco de dados
    database.jobs.insert(new_job.model_dump())