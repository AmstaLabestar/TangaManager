from django.conf import settings
from django.db import models
from django.utils import timezone

from .constants import (
    ACCES_DISTANT_CHOICES,
    CHECKLIST_STATUT_CHOICES,
    JALON_CHOICES,
    JALON_DELAIS,
    SOLUTION_CHOICES,
    STATUT_CHOICES,
    checklist_for_solution,
)


class InstallationFiche(models.Model):
    client_nom = models.CharField(max_length=180)
    client_contact = models.CharField(max_length=180)
    client_poste = models.CharField(max_length=120, blank=True)
    client_telephone = models.CharField(max_length=60, blank=True)
    client_email = models.EmailField(blank=True)
    client_adresse = models.TextField(blank=True)

    technicien = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="fiches_installation",
        null=True,
        blank=True,
    )
    technicien_nom = models.CharField(max_length=180)
    date_installation = models.DateField(default=timezone.localdate)
    heure_installation = models.TimeField(null=True, blank=True)

    solution = models.CharField(max_length=40, choices=SOLUTION_CHOICES)
    numero_serie = models.CharField(max_length=120)
    quantite = models.CharField(max_length=180, blank=True)
    version_firmware = models.CharField(max_length=80, blank=True)
    wifi_ssid = models.CharField(max_length=120, blank=True)
    ip_statique = models.GenericIPAddressField(null=True, blank=True)
    acces_distant = models.CharField(
        max_length=30,
        choices=ACCES_DISTANT_CHOICES,
        blank=True,
    )

    note_formation = models.PositiveSmallIntegerField()
    observations = models.TextField(blank=True)
    signature_client = models.ImageField(upload_to="signatures/clients/")
    signature_technicien = models.ImageField(upload_to="signatures/techniciens/")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="signee")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "fiche d'installation"
        verbose_name_plural = "fiches d'installation"

    def __str__(self):
        return f"{self.client_nom} - {self.get_solution_display()}"

    @property
    def ok_count(self):
        return self.checklist_items.filter(statut="ok").count()

    @property
    def probleme_count(self):
        return self.checklist_items.filter(statut="probleme").count()

    def create_checklist_items(self, statuses=None):
        statuses = statuses or []
        items = checklist_for_solution(self.solution)
        for index, label in enumerate(items):
            status = statuses[index] if index < len(statuses) else "a_verifier"
            ChecklistItem.objects.create(
                fiche=self,
                ordre=index + 1,
                libelle=label,
                statut=status or "a_verifier",
            )

    def create_jalons(self):
        signed_date = (self.signed_at or timezone.now()).date()
        for code, delay in JALON_DELAIS.items():
            Jalon.objects.get_or_create(
                fiche=self,
                type_jalon=code,
                defaults={"date_prevue": signed_date + delay},
            )


class ChecklistItem(models.Model):
    fiche = models.ForeignKey(
        InstallationFiche,
        on_delete=models.CASCADE,
        related_name="checklist_items",
    )
    ordre = models.PositiveSmallIntegerField()
    libelle = models.CharField(max_length=255)
    statut = models.CharField(
        max_length=20,
        choices=CHECKLIST_STATUT_CHOICES,
        default="a_verifier",
    )

    class Meta:
        ordering = ["ordre"]
        unique_together = [("fiche", "ordre")]

    def __str__(self):
        return f"{self.ordre}. {self.libelle}"


class Jalon(models.Model):
    fiche = models.ForeignKey(
        InstallationFiche,
        on_delete=models.CASCADE,
        related_name="jalons",
    )
    type_jalon = models.CharField(max_length=10, choices=JALON_CHOICES)
    date_prevue = models.DateField()
    statut = models.CharField(
        max_length=20,
        choices=[
            ("a_faire", "A faire"),
            ("fait", "Fait"),
            ("annule", "Annule"),
        ],
        default="a_faire",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_prevue"]
        unique_together = [("fiche", "type_jalon")]

    def __str__(self):
        return f"{self.get_type_jalon_display()} - {self.fiche.client_nom}"

