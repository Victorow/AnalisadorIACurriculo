import os 
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from database import AnalyseDatabase
from create_job import create_job
import subprocess

# Inicializando o banco de dados
database = AnalyseDatabase()
st.set_page_config(layout='wide', page_title='Analisador e Registro de Vagas')

# Opção de seleção entre Análise de Candidatos, Registrar Nova Vaga e Análise de Currículos
menu_option = st.sidebar.selectbox("Escolha a funcionalidade", ["Análise de Candidatos", "Registrar Nova Vaga", "Análise de Currículos"])

if menu_option == "Análise de Candidatos":
    option = st.selectbox(
        'Escolha sua vaga',
        [job.get('name') for job in database.jobs.all()],
        index=None
    )   

    data = None

    if option: 
        job = database.get_job_by_name(option)
        data = database.get_analysis_by_job_id(job.get('id'))

        df = pd.DataFrame(
            data if data else {},
            columns=[
                'name',
                'education',
                'skills',
                'language',
                'score',
                'resum_id',
                'id'
            ]
        )

        df['skills'] = df['skills'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

        df.rename(
            columns={
                'name': 'Nome',
                'education': 'Educação',
                'skills': 'Habilidades',
                'language': 'Idiomas',
                'score': 'Score',
                'resum_id': 'ID do Resumo',
                'id': 'ID da Análise'   
            },
            inplace=True
        )

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)

        if data:
            gb.configure_column('Score', header_name='Score', sort='desc')
            gb.configure_selection(selection_mode='multiple', use_checkbox=True)

        grid_options = gb.build()

        st.subheader('Classificação dos Candidatos')
        st.bar_chart(df, x="Nome", y="Score", color="Nome", horizontal=True)

        response = AgGrid(
            df,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme='streamlit',
        )

        select_candidates = response.get('selected_rows', [])
        candidates_df = pd.DataFrame(select_candidates)

        resums = database.get_resums_by_job_id(job.get('id'))

        def delete_files_resum(resums):
            for resum in resums:
                path = resum.get('file')
                if os.path.isfile(path):
                    os.remove(path)

        if st.button('Limpar Análise'):
            database.delete_all_resums_by_job_id(job.get('id'))  # Deleta todos os currículos
            database.delete_all_analysis_by_job_id(job.get('id'))  # Deleta todas as análises
            database.delete_all_files_by_job_id(job.get('id')) # Deleta todos os arquivos
            st.rerun()

        if st.button('Limpar Todos os Currículos'):
            curriculo_path = 'curriculos'  # Caminho da pasta onde os currículos estão armazenados
            if os.path.exists(curriculo_path):
                for filename in os.listdir(curriculo_path):
                    file_path = os.path.join(curriculo_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)  # Remove o arquivo
                st.success('Todos os currículos foram limpos.')
            else:
                st.error('A pasta "curriculo" não existe.')

        if st.button('Baixar Curriculos!'):
            try:
                subprocess.run(['python', 'download_cv.py'], check=True)
                st.success('Curriculos baixados com sucesso!')
            except subprocess.CalledProcessError as e:
                st.error(f'Erro, Não foi possível baixar os curriculos! {e}')

        if not candidates_df.empty:
            cols = st.columns(len(candidates_df))
            for idx, row in enumerate(candidates_df.iterrows()):
                with st.container():
                    if resum_data := database.get_resum_by_id(row[1]['ID do Resumo']):
                        st.markdown(resum_data.get("content"))
                        st.markdown(resum_data.get("opinion"))

                        with open(resum_data.get('file'), 'rb') as file:
                            pdf_data = file.read()

                            st.download_button(label=f"Download Curriculo {row[1]['Nome']}",
                                data=pdf_data,
                                file_name=f"{row[1]['Nome']}.pdf",
                                mime='application/pdf'
                            )

elif menu_option == "Registrar Nova Vaga":
    st.title('Registrar Nova Vaga')

    # Formulário para entrada de dados da vaga
    with st.form(key='job_form'):
        job_name = st.text_input('Nome da Vaga', placeholder='Digite o nome da vaga')
        job_activities = st.text_area('Atividades Principais', placeholder='Descreva as atividades principais aqui')
        job_prerequisites = st.text_area('Requisitos', placeholder='Liste os requisitos aqui')
        job_differentials = st.text_area('Diferenciais', placeholder='Liste os diferenciais aqui')
        
        submit_button = st.form_submit_button(label='Registrar Vaga')

    if submit_button:
        # Verifica se todos os campos estão preenchidos
        if job_name and job_activities and job_prerequisites and job_differentials:
            # Chama a função para criar a vaga
            create_job(job_name, job_activities, job_prerequisites, job_differentials)
            st.success('Vaga registrada com sucesso!')
            
            # Limpa os campos do formulário após o registro
            job_name = ""
            job_activities = ""
            job_prerequisites = ""
            job_differentials = ""
        else:
            st.error('Por favor, preencha todos os campos.')

    # Seção para remover uma vaga existente
    st.subheader('Remover Vaga Existente')
    existing_jobs = [job.get('name') for job in database.jobs.all()]
    job_to_remove = st.selectbox('Selecione a vaga a ser removida', existing_jobs)

    if st.button('Remover Vaga'):
        if job_to_remove:
            job = database.get_job_by_name(job_to_remove)
            if job:  # Verifica se a vaga foi encontrada
                try:
                    database.delete_job_by_id(job.get('id'))  # Chama a função para remover a vaga do banco de dados
                    st.success(f'Vaga "{job_to_remove}" removida com sucesso!')
                except KeyError as e:
                    st.error(str(e))  # Mostra a mensagem de erro se a vaga não for encontrada
            else:
                st.error('Vaga não encontrada.')
        else:
            st.error('Por favor, selecione uma vaga para remover.')

elif menu_option == "Análise de Currículos":
    st.title('Análise de Currículos')

    job_option = st.selectbox(
        'Escolha a vaga para análise',
        [job.get('name') for job in database.jobs.all()],
        index=None
    )

    if job_option:
        if st.button('Executar Análise'):
            try:
                subprocess.run(['python', 'analise.py', job_option], check=True)
                st.success('Análise executada com sucesso!')
            except subprocess.CalledProcessError as e:
                st.error(f'Erro ao executar a análise: {e}')