from datetime import timedelta


SOLUTION_CHOICES = [
    ("presencerh_rfid", "PresenseRH RFID"),
    ("presencerh_bio", "PresenseRH Biometrique"),
    ("presencerh_qr", "PresenseRH QR Code"),
    ("feelback", "FeelBack Terminal"),
    ("smartcard", "SmartCard / Carte fidelite"),
    ("kuilinga", "KUILINGA Ecole"),
]

ACCES_DISTANT_CHOICES = [
    ("ssh_vpn", "SSH + VPN"),
    ("vpn", "VPN uniquement"),
    ("na", "Non applicable"),
    ("non_configure", "Non configure"),
]

STATUT_CHOICES = [
    ("brouillon", "Brouillon"),
    ("validee", "Validee"),
    ("signee", "Signee"),
]

CHECKLIST_STATUT_CHOICES = [
    ("ok", "OK"),
    ("probleme", "Probleme"),
    ("a_verifier", "A verifier"),
]

JALON_CHOICES = [
    ("j2", "J+2"),
    ("j7", "J+7"),
    ("j30", "J+30"),
]

JALON_DELAIS = {
    "j2": timedelta(days=2),
    "j7": timedelta(days=7),
    "j30": timedelta(days=30),
}

CHECKLISTS = {
    "default": [
        "Alimentation et mise sous tension verifiee",
        "Connexion WiFi / reseau local etablie",
        "Communication avec TangaFlow confirmee",
        "Test de lecture fonctionnel (badge / empreinte / QR)",
        "Enregistrement des utilisateurs de test effectue",
        "Tableau de bord accessible et donnees visibles",
        "Acces distant technicien configure (SSH/VPN)",
        "Formation utilisateur dispensee (min. 30 min)",
        "Documentation papier remise au client",
        "Numero de serie enregistre dans TangaFlow",
    ],
    "feelback": [
        "Alimentation et mise sous tension verifiee",
        "Connexion WiFi / reseau local etablie",
        "Communication avec TangaFlow confirmee",
        "Test boutons satisfaction fonctionnel (4 niveaux)",
        "Affichage ecran et LEDs operationnels",
        "Donnees de retour visibles dans le tableau de bord",
        "Acces distant technicien configure (SSH/VPN)",
        "Emplacement de fixation valide avec le client",
        "Formation utilisateur dispensee",
        "Documentation papier remise au client",
    ],
    "smartcard": [
        "Alimentation et mise sous tension verifiee",
        "Connexion WiFi / reseau local etablie",
        "Communication avec TangaFlow confirmee",
        "Test de lecture carte reussi",
        "Encodage des cartes de demonstration effectue",
        "Interface partenaires accessible",
        "Acces distant technicien configure",
        "Formation remise au responsable",
        "Documentation remise au client",
    ],
}


def checklist_type_for_solution(solution):
    if solution == "feelback":
        return "feelback"
    if solution == "smartcard":
        return "smartcard"
    return "default"


def checklist_for_solution(solution):
    return CHECKLISTS[checklist_type_for_solution(solution)]


def solution_label(solution):
    return dict(SOLUTION_CHOICES).get(solution, solution)

