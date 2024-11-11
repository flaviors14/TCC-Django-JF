from django.urls import path
from . import views

urlpatterns = [

    path('cadastro/', views.cadastro, name='cadastro'),

    path('login/', views.login, name='login'),
    


    path('upload/', views.upload_form, name='upload_form'),  # Rota para a página de upload
    
    path('show-articles/<str:filename>/', views.show_articles, name='show_articles'),

    path('download/<str:filename>/', views.download_file, name='download_file'),  # Rota para download do arquivo processado
]
