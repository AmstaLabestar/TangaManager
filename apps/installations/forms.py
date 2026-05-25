import base64
import binascii
import json
import uuid

from django import forms
from django.core.files.base import ContentFile
from django.utils import timezone

from .constants import ACCES_DISTANT_CHOICES, SOLUTION_CHOICES
from .models import InstallationFiche


class InstallationFicheForm(forms.ModelForm):
    checklist_statuses = forms.CharField(
        widget=forms.HiddenInput,
        error_messages={"required": "La checklist n'a pas ete initialisee. Selectionnez une solution."},
    )
    signature_client_data = forms.CharField(
        widget=forms.HiddenInput,
        error_messages={"required": "La signature client est obligatoire."},
    )
    signature_technicien_data = forms.CharField(
        widget=forms.HiddenInput,
        error_messages={"required": "La signature technicien est obligatoire."},
    )

    class Meta:
        model = InstallationFiche
        fields = [
            "client_nom",
            "client_contact",
            "client_poste",
            "client_telephone",
            "client_email",
            "client_adresse",
            "technicien_nom",
            "date_installation",
            "heure_installation",
            "solution",
            "numero_serie",
            "quantite",
            "version_firmware",
            "wifi_ssid",
            "ip_statique",
            "acces_distant",
            "note_formation",
            "observations",
        ]
        widgets = {
            "date_installation": forms.DateInput(attrs={"type": "date"}),
            "heure_installation": forms.TimeInput(attrs={"type": "time"}),
            "note_formation": forms.HiddenInput(),
            "observations": forms.Textarea(attrs={"rows": 4}),
            "client_adresse": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["solution"].choices = [("", "Selectionner")] + SOLUTION_CHOICES
        self.fields["acces_distant"].choices = [("", "Selectionner")] + ACCES_DISTANT_CHOICES
        self.fields["date_installation"].initial = timezone.localdate()
        self.fields["note_formation"].min_value = 1
        self.fields["note_formation"].max_value = 5
        required_labels = {
            "client_nom": "Indiquez le nom de l'entreprise ou du client.",
            "client_contact": "Indiquez le nom de la personne qui receptionne.",
            "technicien_nom": "Indiquez le nom du technicien TANGA.",
            "date_installation": "Indiquez la date d'installation.",
            "solution": "Selectionnez la solution installee.",
            "numero_serie": "Indiquez le numero de serie du materiel.",
            "note_formation": "Notez la formation client de 1 a 5.",
        }
        for name, field in self.fields.items():
            if name not in {"checklist_statuses", "signature_client_data", "signature_technicien_data"}:
                field.widget.attrs.setdefault("class", "field")
            if name in required_labels:
                field.error_messages["required"] = required_labels[name]
        self.fields["client_email"].error_messages["invalid"] = "Entrez une adresse email valide."
        self.fields["ip_statique"].error_messages["invalid"] = "Entrez une adresse IP valide, par exemple 192.168.1.50."

    def clean_checklist_statuses(self):
        value = self.cleaned_data["checklist_statuses"]
        try:
            statuses = json.loads(value)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError("Checklist invalide.") from exc
        valid = {"ok", "probleme", "a_verifier"}
        if not isinstance(statuses, list) or any(status not in valid for status in statuses):
            raise forms.ValidationError("Statuts checklist invalides.")
        return statuses

    def _decode_signature(self, field_name, folder):
        value = self.cleaned_data[field_name]
        prefix = "data:image/png;base64,"
        if not value.startswith(prefix):
            raise forms.ValidationError("Signature manquante ou invalide.")
        try:
            content = base64.b64decode(value.removeprefix(prefix))
        except (binascii.Error, ValueError) as exc:
            raise forms.ValidationError("Signature illisible.") from exc
        return ContentFile(content, name=f"{folder}-{uuid.uuid4().hex}.png")

    def clean_signature_client_data(self):
        return self._decode_signature("signature_client_data", "client")

    def clean_signature_technicien_data(self):
        return self._decode_signature("signature_technicien_data", "technicien")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.signature_client = self.cleaned_data["signature_client_data"]
        instance.signature_technicien = self.cleaned_data["signature_technicien_data"]
        instance.statut = "signee"
        instance.signed_at = timezone.now()
        if commit:
            instance.save()
            instance.create_checklist_items(self.cleaned_data["checklist_statuses"])
            instance.create_jalons()
        return instance
