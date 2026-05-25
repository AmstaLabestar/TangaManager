import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .constants import checklist_for_solution
from .models import InstallationFiche


MEDIA_ROOT = tempfile.mkdtemp()
PNG_DATA_URL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ"
    "l31N5WQAAAABJRU5ErkJggg=="
)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class InstallationFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def test_healthcheck_returns_ok(self):
        response = self.client.get(reverse("healthcheck"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_staff_admin_panel_renders(self):
        user = get_user_model().objects.create_user(
            username="admin",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("installations-admin-panel"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

    def test_create_signed_installation_creates_checklist_and_jalons(self):
        user = get_user_model().objects.create_user(
            username="technicien",
            password="test-password",
        )
        self.client.force_login(user)

        statuses = ["ok"] * len(checklist_for_solution("feelback"))
        response = self.client.post(
            reverse("installations-create"),
            data={
                "client_nom": "BTP SARL",
                "client_contact": "Awa Ouedraogo",
                "client_poste": "DRH",
                "client_telephone": "+226 00 00 00 00",
                "client_email": "awa@example.com",
                "client_adresse": "Ouagadougou",
                "technicien_nom": "Technicien TANGA",
                "date_installation": "2026-05-22",
                "heure_installation": "14:30",
                "solution": "feelback",
                "numero_serie": "FB-001",
                "quantite": "1 terminal",
                "version_firmware": "v1",
                "wifi_ssid": "ClientWifi",
                "ip_statique": "192.168.1.50",
                "acces_distant": "ssh_vpn",
                "note_formation": "5",
                "observations": "RAS",
                "checklist_statuses": json.dumps(statuses),
                "signature_client_data": PNG_DATA_URL,
                "signature_technicien_data": PNG_DATA_URL,
            },
        )

        self.assertEqual(response.status_code, 302)
        fiche = InstallationFiche.objects.get()
        self.assertEqual(fiche.statut, "signee")
        self.assertEqual(fiche.checklist_items.count(), len(statuses))
        self.assertEqual(fiche.jalons.count(), 3)
