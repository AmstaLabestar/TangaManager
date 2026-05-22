# Generated manually for the initial TANGA Manage Support app.

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InstallationFiche",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("client_nom", models.CharField(max_length=180)),
                ("client_contact", models.CharField(max_length=180)),
                ("client_poste", models.CharField(blank=True, max_length=120)),
                ("client_telephone", models.CharField(blank=True, max_length=60)),
                ("client_email", models.EmailField(blank=True, max_length=254)),
                ("client_adresse", models.TextField(blank=True)),
                ("technicien_nom", models.CharField(max_length=180)),
                ("date_installation", models.DateField(default=django.utils.timezone.localdate)),
                ("heure_installation", models.TimeField(blank=True, null=True)),
                (
                    "solution",
                    models.CharField(
                        choices=[
                            ("presencerh_rfid", "PresenseRH RFID"),
                            ("presencerh_bio", "PresenseRH Biometrique"),
                            ("presencerh_qr", "PresenseRH QR Code"),
                            ("feelback", "FeelBack Terminal"),
                            ("smartcard", "SmartCard / Carte fidelite"),
                            ("kuilinga", "KUILINGA Ecole"),
                        ],
                        max_length=40,
                    ),
                ),
                ("numero_serie", models.CharField(max_length=120)),
                ("quantite", models.CharField(blank=True, max_length=180)),
                ("version_firmware", models.CharField(blank=True, max_length=80)),
                ("wifi_ssid", models.CharField(blank=True, max_length=120)),
                ("ip_statique", models.GenericIPAddressField(blank=True, null=True)),
                (
                    "acces_distant",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("ssh_vpn", "SSH + VPN"),
                            ("vpn", "VPN uniquement"),
                            ("na", "Non applicable"),
                            ("non_configure", "Non configure"),
                        ],
                        max_length=30,
                    ),
                ),
                ("note_formation", models.PositiveSmallIntegerField()),
                ("observations", models.TextField(blank=True)),
                ("signature_client", models.ImageField(upload_to="signatures/clients/")),
                ("signature_technicien", models.ImageField(upload_to="signatures/techniciens/")),
                (
                    "statut",
                    models.CharField(
                        choices=[
                            ("brouillon", "Brouillon"),
                            ("validee", "Validee"),
                            ("signee", "Signee"),
                        ],
                        default="signee",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("signed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "technicien",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fiches_installation",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "fiche d'installation",
                "verbose_name_plural": "fiches d'installation",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Jalon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type_jalon",
                    models.CharField(choices=[("j2", "J+2"), ("j7", "J+7"), ("j30", "J+30")], max_length=10),
                ),
                ("date_prevue", models.DateField()),
                (
                    "statut",
                    models.CharField(
                        choices=[("a_faire", "A faire"), ("fait", "Fait"), ("annule", "Annule")],
                        default="a_faire",
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "fiche",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jalons",
                        to="installations.installationfiche",
                    ),
                ),
            ],
            options={
                "ordering": ["date_prevue"],
                "unique_together": {("fiche", "type_jalon")},
            },
        ),
        migrations.CreateModel(
            name="ChecklistItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ordre", models.PositiveSmallIntegerField()),
                ("libelle", models.CharField(max_length=255)),
                (
                    "statut",
                    models.CharField(
                        choices=[("ok", "OK"), ("probleme", "Probleme"), ("a_verifier", "A verifier")],
                        default="a_verifier",
                        max_length=20,
                    ),
                ),
                (
                    "fiche",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checklist_items",
                        to="installations.installationfiche",
                    ),
                ),
            ],
            options={
                "ordering": ["ordre"],
                "unique_together": {("fiche", "ordre")},
            },
        ),
    ]

