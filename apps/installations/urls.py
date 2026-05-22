from django.urls import path

from . import views


urlpatterns = [
    path("", views.fiche_list, name="installations-index"),
    path("new/", views.fiche_create, name="installations-create"),
    path("<int:pk>/", views.fiche_detail, name="installations-detail"),
    path("admin-panel/", views.admin_panel, name="installations-admin-panel"),
]
