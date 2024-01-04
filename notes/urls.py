from django.urls import path
from . import views
urlpatterns = [
    path('api/auth/signup', views.SignUp.as_view()),
    path('api/auth/login', views.SignIn.as_view()),

    path('api/notes', views.NotesList.as_view()),
    path('api/notes/', views.NoteById.as_view()),
    path('api/notes/<id>/share', views.ShareNote.as_view()),
    path('api/search', views.SearchUsingKeyWords.as_view())
]