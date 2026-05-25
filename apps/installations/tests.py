import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
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

    def _create_signed_fiche(self, user=None):
        if user is not None:
            self.client.force_login(user)
        statuses = ["ok"] * len(checklist_for_solution("feelback"))
        self.client.post(
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
        return InstallationFiche.objects.latest("id")

    def test_create_signed_installation_creates_checklist_and_jalons(self):
        user = get_user_model().objects.create_user(
            username="technicien",
            password="test-password",
        )
        self.client.force_login(user)

        fiche = self._create_signed_fiche()

        self.assertEqual(fiche.statut, "signee")
        self.assertEqual(fiche.technicien, user)
        self.assertEqual(fiche.checklist_items.count(), len(checklist_for_solution("feelback")))
        self.assertEqual(fiche.jalons.count(), 3)

    def test_signed_installation_can_be_exported_as_pdf(self):
        user = get_user_model().objects.create_user(
            username="technicien-pdf",
            password="test-password",
        )
        self.client.force_login(user)
        fiche = self._create_signed_fiche()

        response = self.client.get(reverse("installations-pdf", args=[fiche.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_staff_detail_has_admin_navigation(self):
        user = get_user_model().objects.create_user(
            username="admin-navigation",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(user)
        fiche = self._create_signed_fiche()

        response = self.client.get(reverse("installations-detail", args=[fiche.pk]))

        self.assertContains(response, "Dashboard")
        self.assertContains(response, "Django admin")
        self.assertContains(response, "PDF")

    def test_invalid_installation_shows_clear_errors(self):
        user = get_user_model().objects.create_user(
            username="technicien-erreur",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("installations-create"), data={})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "pas ete enregistree")
        self.assertContains(response, "Indiquez le nom")

    def test_technician_only_sees_own_fiches(self):
        owner = get_user_model().objects.create_user(
            username="owner",
            password="test-password",
        )
        other = get_user_model().objects.create_user(
            username="other",
            password="test-password",
        )
        fiche = self._create_signed_fiche(owner)
        self._create_signed_fiche(other)

        self.client.force_login(owner)
        list_response = self.client.get(reverse("installations-index"))
        detail_response = self.client.get(reverse("installations-detail", args=[fiche.pk]))

        self.assertContains(list_response, "BTP SARL", count=1)
        self.assertEqual(detail_response.status_code, 200)

    def test_technician_cannot_access_another_technician_fiche(self):
        owner = get_user_model().objects.create_user(
            username="owner-private",
            password="test-password",
        )
        other = get_user_model().objects.create_user(
            username="other-private",
            password="test-password",
        )
        fiche = self._create_signed_fiche(owner)

        self.client.force_login(other)
        detail_response = self.client.get(reverse("installations-detail", args=[fiche.pk]))
        pdf_response = self.client.get(reverse("installations-pdf", args=[fiche.pk]))

        self.assertEqual(detail_response.status_code, 403)
        self.assertEqual(pdf_response.status_code, 403)

    def test_commercial_can_read_all_fiches_but_not_admin_dashboard(self):
        commercial_group = Group.objects.create(name="Commercial")
        commercial = get_user_model().objects.create_user(
            username="commercial",
            password="test-password",
        )
        commercial.groups.add(commercial_group)
        owner = get_user_model().objects.create_user(
            username="owner-commercial",
            password="test-password",
        )
        fiche = self._create_signed_fiche(owner)

        self.client.force_login(commercial)
        list_response = self.client.get(reverse("installations-index"))
        detail_response = self.client.get(reverse("installations-detail", args=[fiche.pk]))
        dashboard_response = self.client.get(reverse("installations-admin-panel"))

        self.assertContains(list_response, "Vue globale equipe")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(dashboard_response.status_code, 302)

    def test_staff_can_read_all_fiches_and_dashboard(self):
        staff = get_user_model().objects.create_user(
            username="staff-reader",
            password="test-password",
            is_staff=True,
        )
        owner = get_user_model().objects.create_user(
            username="owner-staff",
            password="test-password",
        )
        fiche = self._create_signed_fiche(owner)

        self.client.force_login(staff)
        detail_response = self.client.get(reverse("installations-detail", args=[fiche.pk]))
        dashboard_response = self.client.get(reverse("installations-admin-panel"))

        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(dashboard_response.status_code, 200)
