from django.contrib import admin

from .models import ChecklistItem, InstallationFiche, Jalon


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 0


class JalonInline(admin.TabularInline):
    model = Jalon
    extra = 0


@admin.register(InstallationFiche)
class InstallationFicheAdmin(admin.ModelAdmin):
    list_display = (
        "client_nom",
        "solution",
        "technicien_nom",
        "date_installation",
        "statut",
        "created_at",
    )
    list_filter = ("solution", "statut", "date_installation")
    search_fields = ("client_nom", "client_contact", "numero_serie", "technicien_nom")
    inlines = [ChecklistItemInline, JalonInline]
    readonly_fields = ("created_at", "updated_at", "signed_at")


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("fiche", "ordre", "statut", "libelle")
    list_filter = ("statut",)


@admin.register(Jalon)
class JalonAdmin(admin.ModelAdmin):
    list_display = ("fiche", "type_jalon", "date_prevue", "statut")
    list_filter = ("type_jalon", "statut", "date_prevue")

