from tinydb import TinyDB, Query


class AnalyseDatabase(TinyDB):
    def __init__(self, db_path= 'db.json'):
        super().__init__(db_path)
        self.jobs = self.table('jobs')
        self.resume = self.table('resums')
        self.analysis = self.table('analysis')
        self.files = self.table('files')

    def get_job_by_name(self, name):
        job = Query()
        result = self.jobs.search(job.name == name)
        return result[0] if result else None
    
    def get_resum_by_id(self, id):
        resum = Query()
        result = self.resume.search(resum.id == id)
        return result[0] if result else None
    
    def get_analysis_by_job_id(self, job_id):
        analysis = Query()
        result = self.analysis.search(analysis.job_id == job_id)
        return result 
    
    def get_resums_by_job_id(self, job_id):
        resum = Query()
        result = self.resume.search(resum.job_id == job_id)
        return result
    
    def delete_all_resums_by_job_id(self, job_id):
        resum = Query()
        self.resume.remove(resum.job_id == job_id)

    def delete_all_analysis_by_job_id(self, job_id):
        analysis = Query()    
        self.analysis.remove(analysis.job_id == job_id)

    def delete_all_files_by_job_id(self, job_id):
        file = Query()
        self.files.remove(file.job_id == job_id)

    def delete_job_by_id(self, job_id):
        job = Query()
        result = self.jobs.search(job.id == job_id)  # Busca o job pelo ID
        if result:
            self.jobs.remove(doc_ids=[result[0].doc_id])  # Remove o job usando o doc_id
        else:
            raise KeyError(f"Job with ID {job_id} not found.")
    
    

