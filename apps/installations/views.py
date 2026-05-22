import json

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .constants import CHECKLISTS, SOLUTION_CHOICES
from .forms import InstallationFicheForm
from .models import InstallationFiche
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count


def fiche_create(request):
    if request.method == "POST":
        form = InstallationFicheForm(request.POST)
        if form.is_valid():
            fiche = form.save()
            messages.success(request, "Fiche signee et enregistree.")
            return redirect("installations-detail", pk=fiche.pk)
    else:
        form = InstallationFicheForm()

    return render(
        request,
        "installations/fiche_form.html",
        {
            "form": form,
            "solutions": SOLUTION_CHOICES,
            "checklists": CHECKLISTS,
            "checklists_json": json.dumps(CHECKLISTS),
        },
    )


def fiche_detail(request, pk):
    fiche = get_object_or_404(
        InstallationFiche.objects.prefetch_related("checklist_items", "jalons"),
        pk=pk,
    )
    return render(request, "installations/fiche_detail.html", {"fiche": fiche})


def fiche_list(request):
    fiches = InstallationFiche.objects.all()[:30]
    return render(request, "installations/fiche_list.html", {"fiches": fiches})


@staff_member_required
def admin_panel(request):
    """Vue simple pour le panneau admin avec statistiques et liste rapide."""
    total = InstallationFiche.objects.count()
    recent = InstallationFiche.objects.order_by("-created_at")[:10]
    by_solution = (
        InstallationFiche.objects.values("solution").annotate(count=Count("id")).order_by("-count")
    )
    context = {
        "total": total,
        "recent": recent,
        "by_solution": by_solution,
    }
    return render(request, "installations/admin_panel.html", context)
