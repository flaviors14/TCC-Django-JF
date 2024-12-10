from unicodedata import name
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import FileResponse, HttpResponse
import pandas as pd
import os
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

# Defina o diretório onde os arquivos filtrados serão salvos
FILTERED_FILES_DIR = os.path.join(settings.MEDIA_ROOT, 'filtered_files')

# Certifique-se de que a pasta existe
os.makedirs(FILTERED_FILES_DIR, exist_ok=True)

@login_required(login_url="/accounts/login/")
def show_articles(request, filename):
    file_path = os.path.join(FILTERED_FILES_DIR, filename)
    df = pd.read_excel(file_path)

    # Aplicar filtros com base nos parâmetros GET
    sort_by = request.GET.get('sort_by', 'cited_by_desc')
    publisher = request.GET.get('publisher')
    source = request.GET.get('source')

    # Filtros por Publisher e Source
    if publisher:
        df = df[df['Publisher'] == publisher]
    if source:
        df = df[df['Source'] == source]

    # Ordenação
    if sort_by == 'cited_by_desc':
        df = df.sort_values(by='Cited by', ascending=False)
    elif sort_by == 'cited_by_asc':
        df = df.sort_values(by='Cited by', ascending=True)
    elif sort_by == 'year_desc':
        df = df.sort_values(by='Year', ascending=False)
    elif sort_by == 'year_asc':
        df = df.sort_values(by='Year', ascending=True)

    # Pegar os primeiros 20 artigos após o filtro
    articles = df.head(20).to_dict('records')

    # Atualizar lista de publishers e sources para exibição
    publishers = df['Publisher'].unique()
    sources = df['Source'].unique()

    context = {
        'articles': articles,
        'filename': filename,
        'publishers': publishers,
        'sources': sources,
    }
  
    return render(request, 'fileupload/show_articles.html', context)


@login_required(login_url="/accounts/login/")
def upload_form(request):
    if request.method == 'POST':
        file1 = request.FILES.get('file1')
        file2 = request.FILES.get('file2')

        if not file1 or not file2:
            return render(request, 'fileupload/upload..html', {'error': 'Por favor, envie os dois arquivos CSV.'})
        
        # Salvar os arquivos temporariamente
        file1_path = os.path.join(settings.MEDIA_ROOT, file1.name)
        file2_path = os.path.join(settings.MEDIA_ROOT, file2.name)

        with open(file1_path, 'wb+') as destination:
            for chunk in file1.chunks():
                destination.write(chunk)

        with open(file2_path, 'wb+') as destination:
            for chunk in file2.chunks():
                destination.write(chunk)

        # Processar os arquivos e obter o nome do arquivo filtrado
        result_filename = process_files(file1_path, file2_path)

        # Deletar os arquivos originais para liberar espaço
        os.remove(file1_path)
        os.remove(file2_path)
    
        # Mostrar a página com a opção de download e exibição dos dados
        return render(request, 'fileupload/upload.html', {
            'result': result_filename,
            'show_filter_button': True  # Adiciona a opção de exibir a lista filtrada
        })
    return render(request, 'fileupload/upload.html')



def process_files(file_path_1, file_path_2):
    # Função para ler os dados de um arquivo CSV
    def read_csv_file(file_path):
        return pd.read_csv(file_path)

    # Ler os arquivos CSV
    S1_0 = read_csv_file(file_path_1)
    SC1_1 = read_csv_file(file_path_2)

    # União das bases de dados e remoção de duplicatas
    U2_2 = pd.concat([S1_0, SC1_1]).drop_duplicates()

    # Defina o nome do arquivo filtrado
    filtered_file_name = 'BaseFiltrada.xlsx'
    filtered_file_path = os.path.join(FILTERED_FILES_DIR, filtered_file_name)

    # Salva a base de dados filtrada no caminho especificado
    U2_2.to_excel(filtered_file_path, index=False)
    return filtered_file_name

def download_file(request, filename):
    file_path = os.path.join(FILTERED_FILES_DIR, filename)
    return FileResponse(open(file_path, 'rb'), as_attachment=True)


