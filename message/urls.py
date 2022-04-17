from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_threads, name="get-threads"),
    path('create-thread/', views.CreateThread,name="create-thread"),
    path('<str:pk>/read/', views.read_message, name="read-message"),
    path('create/', views.create_message, name="create-message"),
    path('<str:pk>/messages/',views.get_messages ,name="get-messages"),
    path('unread/count/',views.get_un_read_count,name="get-unread-count")
]
