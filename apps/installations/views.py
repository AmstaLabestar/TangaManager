import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .constants import CHECKLISTS, SOLUTION_CHOICES
from .forms import InstallationFicheForm
from .models import InstallationFiche, Jalon


@login_required
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


@login_required
def fiche_detail(request, pk):
    fiche = get_object_or_404(
        InstallationFiche.objects.prefetch_related("checklist_items", "jalons"),
        pk=pk,
    )
    return render(request, "installations/fiche_detail.html", {"fiche": fiche})


@login_required
def fiche_list(request):
    fiches = InstallationFiche.objects.all()[:30]
    return render(request, "installations/fiche_list.html", {"fiches": fiches})


@staff_member_required
def admin_panel(request):
    total = InstallationFiche.objects.count()
    today = timezone.localdate()
    recent = (
        InstallationFiche.objects.prefetch_related("checklist_items", "jalons")
        .order_by("-created_at")[:10]
    )
    signed_count = InstallationFiche.objects.filter(statut="signee").count()
    today_count = InstallationFiche.objects.filter(created_at__date=today).count()
    issue_count = (
        InstallationFiche.objects.filter(checklist_items__statut="probleme")
        .distinct()
        .count()
    )
    upcoming_jalons = (
        Jalon.objects.select_related("fiche")
        .filter(statut="a_faire", date_prevue__gte=today)
        .order_by("date_prevue")[:6]
    )
    overdue_count = Jalon.objects.filter(statut="a_faire", date_prevue__lt=today).count()
    by_solution_rows = (
        InstallationFiche.objects.values("solution")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    solution_labels = dict(SOLUTION_CHOICES)
    by_solution = [
        {
            "code": row["solution"],
            "label": solution_labels.get(row["solution"], row["solution"]),
            "count": row["count"],
            "percent": round((row["count"] / total) * 100) if total else 0,
        }
        for row in by_solution_rows
    ]
    status_counts = InstallationFiche.objects.aggregate(
        signee=Count("id", filter=Q(statut="signee")),
        validee=Count("id", filter=Q(statut="validee")),
        brouillon=Count("id", filter=Q(statut="brouillon")),
    )
    context = {
        "total": total,
        "signed_count": signed_count,
        "today_count": today_count,
        "issue_count": issue_count,
        "overdue_count": overdue_count,
        "recent": recent,
        "by_solution": by_solution,
        "status_counts": status_counts,
        "upcoming_jalons": upcoming_jalons,
    }
    return render(request, "installations/admin_panel.html", context)
