from db.connexion import connect_db
from services.gestion_utilisateurs import (
    lister_medecins, ajouter_utilisateur, ajouter_medecin, supprimer_medecin,
    lister_secretaires, ajouter_secretaire, supprimer_secretaire, lister_utilisateurs_medecins
)
from services.notifications import envoyer_email
import tkinter as tk
from tkinter import ttk, messagebox
from ui.ajout_utilisateur import AjouterUtilisateur
from fpdf import FPDF
import barcode
from barcode.writer import ImageWriter
import matplotlib.pyplot as plt
import calendar
import datetime
import locale

# ... (toutes les importations restent inchangées)

def AdminDashboard(admin_id):
    fenetre = tk.Tk()
    fenetre.title("Tableau de bord - Administrateur")
    fenetre.geometry("1100x650")
    fenetre.configure(bg="#eaf6fb")

    # --- Ajout pour la date en français ---
    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except:
        try:
            locale.setlocale(locale.LC_TIME, "fr_FR")
        except:
            locale.setlocale(locale.LC_TIME, "")

    # HEADER avec logo, titre, date, badge admin et bouton de déconnexion
    header_frame = tk.Frame(fenetre, bg="#eaf6fb")
    header_frame.pack(fill=tk.X, pady=(20, 10))

    try:
        from PIL import Image, ImageTk
        logo = Image.open("logo_clinique.png")
        logo = logo.resize((60, 60))
        logo_img = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(header_frame, image=logo_img, bg="#eaf6fb")
        logo_label.image = logo_img
        logo_label.pack(side=tk.LEFT, padx=(30, 10))
    except Exception:
        logo_label = tk.Label(header_frame, text="🏥", font=("Arial", 36), bg="#eaf6fb")
        logo_label.pack(side=tk.LEFT, padx=(30, 10))

    tk.Label(
        header_frame,
        text="Clinique Médicale - Espace Administrateur",
        font=("Segoe UI", 24, "bold"),
        bg="#eaf6fb",
        fg="#0984e3"
    ).pack(side=tk.LEFT, padx=10)

    # Frame pour regrouper les éléments de droite (date, badge, déconnexion)
    right_header_frame = tk.Frame(header_frame, bg="#eaf6fb")
    right_header_frame.pack(side=tk.RIGHT, padx=20)

    # Badge admin
    badge = tk.Label(
        right_header_frame,
        text="ADMIN",
        font=("Segoe UI", 12, "bold"),
        bg="#00b894",
        fg="white",
        padx=12,
        pady=2
    )
    badge.pack(side=tk.TOP, pady=(0, 5))

    # Date
    date_label = tk.Label(
        right_header_frame,
        text=datetime.datetime.now().strftime("%A %d %B %Y").capitalize(),
        font=("Segoe UI", 11),
        bg="#eaf6fb",
        fg="#636e72"
    )
    date_label.pack(side=tk.TOP)

    # Bouton de déconnexion (ajouté ici)
    deconnexion_btn = tk.Button(
        right_header_frame,
        text="Déconnexion",
        font=("Segoe UI", 10, "bold"),
        bg="#d63031",
        fg="white",
        padx=10,
        pady=4,
        relief=tk.FLAT,
        bd=0,
        activebackground="#ff7675",
        command=fenetre.destroy  # Ferme simplement la fenêtre admin
    )
    deconnexion_btn.pack(side=tk.BOTTOM, pady=(10, 0))

    # Séparateur
    ttk.Separator(fenetre, orient='horizontal').pack(fill=tk.X, padx=30, pady=(0, 20))

    # ... (le reste du code reste EXACTEMENT le même jusqu'à la fin)

# ... (toutes les autres fonctions restent inchangées)

    # LEFT: Menu vertical stylé avec hover et icônes
    left_frame = tk.Frame(fenetre, bg="#eaf6fb")
    left_frame.pack(side=tk.LEFT, anchor="n", padx=100, pady=40)

    btns = [
        {"text": "➕ Ajouter un nouvel utilisateur", "bg": "#27ae60", "fg": "white", "cmd": lambda: AjouterUtilisateur(fenetre)},
        {"text": "🩺 Gérer les Médecins", "bg": "#0984e3", "fg": "white", "cmd": lambda: afficher_gestion_medecins(fenetre)},
        {"text": "👩‍💼 Gérer les Secrétaires", "bg": "#00b894", "fg": "white", "cmd": lambda: afficher_gestion_secretaires(fenetre)},
        {"text": "🗓️ Planning Médecin", "bg": "#fdcb6e", "fg": "#2d3436", "cmd": lambda: afficher_planning_medecin(fenetre)},
        {"text": "📊 Statistiques", "bg": "#a29bfe", "fg": "white", "cmd": lambda: afficher_statistiques(fenetre)},
    ]

    def on_enter(e, btn, color):
        btn["bg"] = "#dfe6e9"
        btn["fg"] = color

    def on_leave(e, btn, color, bg):
        btn["bg"] = bg
        btn["fg"] = color

    for b in btns:
        btn = tk.Button(
            left_frame,
            text=b["text"],
            bg=b["bg"],
            fg=b["fg"],
            activeforeground=b["fg"],
            width=28,
            height=2,
            anchor="w",
            font=("Segoe UI", 13, "bold"),
            relief=tk.FLAT,
            bd=0,
            activebackground="#dfe6e9",
            command=b["cmd"]
        )
        btn.pack(pady=10)
        btn.bind("<Enter>", lambda e, btn=btn, color=b["fg"]: on_enter(e, btn, color))
        btn.bind("<Leave>", lambda e, btn=btn, color=b["fg"], bg=b["bg"]: on_leave(e, btn, color, bg=b["bg"]))

    # RIGHT: Carte utilisateur stylée
    right_frame = tk.Frame(fenetre, bg="#eaf6fb")
    right_frame.pack(side=tk.RIGHT, anchor="n", padx=100, pady=40)

    card = tk.Frame(right_frame, bg="white", bd=2, relief=tk.GROOVE)
    card.pack(pady=10, ipadx=10, ipady=10)

    tk.Label(card, text="👥", font=("Arial", 36), bg="white").pack(pady=(10, 0))
    tk.Label(card, text="Afficher la liste des utilisateurs", font=("Segoe UI", 14, "bold"), bg="white", fg="#636e72").pack(pady=(5, 15))
    tk.Button(
        card,
        text="Voir la liste",
        bg="#636e72",
        fg="white",
        activeforeground="white",
        width=20,
        height=2,
        font=("Segoe UI", 12, "bold"),
        relief=tk.FLAT,
        bd=0,
        activebackground="#b2bec3",
        command=lambda: afficher_liste_utilisateurs(fenetre)
    ).pack(pady=(0, 15))

    # Ajout d'une citation inspirante
    quote = tk.Label(
        fenetre,
        text="« La santé est le trésor le plus précieux. »",
        font=("Segoe UI", 13, "italic"),
        bg="#eaf6fb",
        fg="#00b894"
    )
    quote.place(relx=0.5, rely=0.93, anchor="center")

    # Footer
    footer = tk.Label(
        fenetre,
        text="Clinique Médicale - Système de gestion | © 2025",
        font=("Segoe UI", 10),
        bg="#eaf6fb",
        fg="#b2bec3"
    )
    footer.pack(side=tk.BOTTOM, pady=10)

    fenetre.mainloop()

def afficher_liste_utilisateurs(parent):
    fen = tk.Toplevel(parent)
    fen.title("Liste des utilisateurs")
    fen.geometry("700x400")
    fen.configure(bg="white")

    tree = ttk.Treeview(fen, columns=("ID", "Login", "Email", "Rôle"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)
    tree.pack(expand=True, fill=tk.BOTH, pady=10)

    from db.connexion import connect_db
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, login, email, role FROM utilisateurs")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=(row['id'], row['login'], row['email'], row['role']))
        cursor.close()
        conn.close()

def afficher_gestion_medecins(parent):
    fenetre = tk.Toplevel(parent)
    fenetre.title("Gestion des Médecins")
    fenetre.geometry("800x400")
    fenetre.configure(bg="white")

    tree = ttk.Treeview(fenetre, columns=("ID", "Login", "Email", "Spécialité", "Matricule"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)
    tree.pack(expand=True, fill=tk.BOTH, pady=10)

    def charger():
        tree.delete(*tree.get_children())
        for row in lister_medecins():
            tree.insert("", tk.END, values=(row['id'], row['login'], row['email'], row['specialite'], row['matricule']))

    charger()

    def ajouter_ou_modifier(medecin=None):
        fen = tk.Toplevel(fenetre)
        fen.title("Ajouter un médecin" if medecin is None else "Modifier le médecin")
        fen.geometry("400x300")
        fen.configure(bg="white")

        utilisateurs = lister_utilisateurs_medecins()
        user_choices = [f"{u['login']} ({u['email']})" for u in utilisateurs]
        tk.Label(fen, text="Utilisateur Médecin", bg="white").pack(pady=5)
        combo_user = ttk.Combobox(fen, values=user_choices, state="readonly")
        combo_user.pack(pady=5)

        tk.Label(fen, text="Spécialité", bg="white").pack(pady=5)
        entry_specialite = tk.Entry(fen)
        entry_specialite.pack(pady=5)
        tk.Label(fen, text="Matricule", bg="white").pack(pady=5)
        entry_matricule = tk.Entry(fen)
        entry_matricule.pack(pady=5)

        if medecin:
            for idx, u in enumerate(utilisateurs):
                if u['id'] == int(medecin['id']):
                    combo_user.current(idx)
                    break
            entry_specialite.insert(0, medecin['specialite'])
            entry_matricule.insert(0, medecin['matricule'])

        def enregistrer():
            idx = combo_user.current()
            if idx == -1:
                messagebox.showerror("Erreur", "Sélectionnez un utilisateur médecin.")
                return
            user_id = utilisateurs[idx]['id']
            specialite = entry_specialite.get()
            matricule = entry_matricule.get()
            if not (specialite and matricule):
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
                return

            from db.connexion import connect_db
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                if medecin:
                    cursor.execute(
                        "UPDATE medecins SET specialite=%s, matricule=%s WHERE id=%s",
                        (specialite, matricule, medecin['id'])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO medecins (user_id, specialite, matricule) VALUES (%s, %s, %s)",
                        (user_id, specialite, matricule)
                    )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Succès", "Médecin enregistré avec succès.")
                fen.destroy()
                charger()

        tk.Button(fen, text="Enregistrer", bg="#00b894", fg="white", command=enregistrer).pack(pady=20)

    tk.Button(fenetre, text="Ajouter un médecin", bg="#00b894", fg="white", command=lambda: ajouter_ou_modifier()).pack(pady=10)

    def supprimer_selection():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un médecin à supprimer.")
            return
        medecin_id = tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce médecin ?"):
            if supprimer_medecin(medecin_id):
                messagebox.showinfo("Succès", "Médecin supprimé.")
                charger()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression.")

    tk.Button(fenetre, text="Supprimer le médecin sélectionné", bg="#d63031", fg="white", command=supprimer_selection).pack(pady=5)

    def on_double_click(event):
        item = tree.selection()
        if item:
            values = tree.item(item, "values")
            medecin = {
                'id': values[0],
                'login': values[1],
                'email': values[2],
                'specialite': values[3],
                'matricule': values[4]
            }
            ajouter_ou_modifier(medecin)

    tree.bind("<Double-1>", on_double_click)

def afficher_gestion_secretaires(parent):
    fenetre = tk.Toplevel(parent)
    fenetre.title("Gestion des Secrétaires")
    fenetre.geometry("700x400")
    fenetre.configure(bg="white")

    tree = ttk.Treeview(fenetre, columns=("ID", "Login", "Email"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)
    tree.pack(expand=True, fill=tk.BOTH, pady=10)

    def charger():
        tree.delete(*tree.get_children())
        from db.connexion import connect_db
        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, login, email FROM utilisateurs WHERE role = 'secretaire'")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=(row['id'], row['login'], row['email']))
            cursor.close()
            conn.close()

    charger()

    def modifier_selection():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez une secrétaire à modifier.")
            return
        values = tree.item(item, "values")
        secretaire = {
            'id': values[0],
            'login': values[1],
            'email': values[2]
        }
        fen = tk.Toplevel(fenetre)
        fen.title("Modifier la secrétaire")
        fen.geometry("400x200")
        fen.configure(bg="white")

        tk.Label(fen, text="Login", bg="white").pack(pady=5)
        entry_login = tk.Entry(fen)
        entry_login.pack(pady=5)
        entry_login.insert(0, secretaire['login'])

        tk.Label(fen, text="Email", bg="white").pack(pady=5)
        entry_email = tk.Entry(fen)
        entry_email.pack(pady=5)
        entry_email.insert(0, secretaire['email'])

        def enregistrer():
            login = entry_login.get()
            email = entry_email.get()
            if not (login and email):
                messagebox.showerror("Erreur", "Login et email sont obligatoires.")
                return
            from db.connexion import connect_db
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE utilisateurs SET login=%s, email=%s WHERE id=%s",
                    (login, email, secretaire['id'])
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Succès", "Secrétaire modifiée avec succès.")
                fen.destroy()
                charger()

        tk.Button(fen, text="Enregistrer", bg="#00b894", fg="white", command=enregistrer).pack(pady=20)

    def supprimer_selection():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez une secrétaire à supprimer.")
            return
        secretaire_id = tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette secrétaire ?"):
            from db.connexion import connect_db
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM utilisateurs WHERE id = %s", (secretaire_id,))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Succès", "Secrétaire supprimée.")
                charger()

    tk.Button(fenetre, text="Modifier la secrétaire sélectionnée", bg="#0984e3", fg="white", command=modifier_selection).pack(pady=5)
    tk.Button(fenetre, text="Supprimer la secrétaire sélectionnée", bg="#d63031", fg="white", command=supprimer_selection).pack(pady=5)

# === Gestion des Patients ===
def afficher_gestion_patients(parent):
    fenetre = tk.Toplevel(parent)
    fenetre.title("Gestion des Patients")
    fenetre.geometry("800x400")
    fenetre.configure(bg="white")

    tree = ttk.Treeview(fenetre, columns=("ID", "Nom", "Email"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)
    tree.pack(expand=True, fill=tk.BOTH, pady=10)

    def charger():
        tree.delete(*tree.get_children())
        from db.connexion import connect_db
        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email FROM patient")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=(row['id'], row['username'], row['email']))
            cursor.close()
            conn.close()

    charger()

    def supprimer_selection():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un patient à supprimer.")
            return
        patient_id = tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce patient ?"):
            from db.connexion import connect_db
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patient WHERE id = %s", (patient_id,))
                conn.commit()
                cursor.close()
                conn.close()
                charger()
                messagebox.showinfo("Succès", "Patient supprimé.")

    tk.Button(fenetre, text="Supprimer le patient sélectionné", bg="#d63031", fg="white", command=supprimer_selection).pack(pady=5)

    # Bouton Export PDF
    def exporter_pdf_selection():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un patient à exporter.")
            return
        patient_id = tree.item(item, "values")[0]
        exporter_dossier_pdf(patient_id)

    tk.Button(fenetre, text="Exporter le dossier PDF", bg="#6c5ce7", fg="white", command=exporter_pdf_selection).pack(pady=5)

def afficher_planning_medecin(parent):
    fenetre = tk.Toplevel(parent)
    fenetre.title("Planning d'un Médecin")
    fenetre.geometry("800x500")
    fenetre.configure(bg="white")

    from services.gestion_utilisateurs import lister_medecins, annuler_rendezvous
    medecins = lister_medecins()
    medecin_noms = [f"{m['login']} ({m['specialite']})" for m in medecins]
    tk.Label(fenetre, text="Choisir un médecin :", bg="white").pack(pady=10)
    combo = ttk.Combobox(fenetre, values=medecin_noms, state="readonly")
    combo.pack(pady=5)

    tree = ttk.Treeview(fenetre, columns=("ID", "Patient", "Date", "Durée", "Statut"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)
    tree.pack(expand=True, fill=tk.BOTH, pady=20)

    def charger_rdv(event=None):
        tree.delete(*tree.get_children())
        idx = combo.current()
        if idx == -1:
            return
        medecin_id = medecins[idx]['id']
        from db.connexion import connect_db
        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.id, u.login AS patients, r.date_rdv, r.duree, r.statut
                FROM rendezvous r
                JOIN utilisateurs u ON r.patient_id = u.id
                WHERE r.medecin_id = %s
                ORDER BY r.date_rdv DESC
            """, (medecin_id,))
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=(row['id'], row['patients'], row['date_rdv'], row['duree'], row['statut']))
            cursor.close()
            conn.close()

    combo.bind("<<ComboboxSelected>>", charger_rdv)

    # Bouton d'annulation
    def annuler_selection():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Attention", "Sélectionnez un rendez-vous à annuler.")
            return
        rdv_id = tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment annuler ce rendez-vous ?"):
            if annuler_rendezvous(rdv_id):
                messagebox.showinfo("Succès", "Rendez-vous annulé.")
                charger_rdv()
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'annulation.")

    tk.Button(fenetre, text="Annuler le rendez-vous sélectionné", bg="#d63031", fg="white", command=annuler_selection).pack(pady=5)

    # Bouton de rappel (simulation)
def enregistrer_rappel(tree):
    item = tree.selection()
    if not item:
        messagebox.showwarning("Attention", "Sélectionnez un rendez-vous pour enregistrer un rappel.")
        return

    rdv = tree.item(item, "values")
    id_rdv = rdv[0]  # Assure-toi que la colonne ID du rendez-vous est en première position
    date_rdv = rdv[2]  # Ex: '2025-06-20 10:00'

    message = f"Rappel : Vous avez un rendez-vous prévu le {date_rdv}."

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO rappels (id_rendezvous, message) VALUES (%s, %s)", (id_rdv, message))
            conn.commit()
            messagebox.showinfo("Succès", "Rappel enregistré avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement du rappel : {e}")
        finally:
            cursor.close()
            conn.close()

def afficher_statistiques(parent):
    fen = tk.Toplevel(parent)
    fen.title("📊 Statistiques de fréquentation")
    fen.geometry("450x350")
    fen.configure(bg="#f8f9fa")
    fen.resizable(False, False)

    # Titre
    tk.Label(
        fen,
        text="📈 Statistiques Globales",
        font=("Helvetica", 18, "bold"),
        fg="#2d3436",
        bg="#f8f9fa"
    ).pack(pady=20)

    # Frame des statistiques
    stat_frame = tk.Frame(fen, bg="white", bd=2, relief="groove")
    stat_frame.pack(padx=20, pady=10, fill="both", expand=True)

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patients")
        nb_patients = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM rendezvous")
        nb_rdv = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM consultations")
        nb_consult = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Erreur BD", f"Impossible de récupérer les statistiques\n{e}")
        return

    # Affichage stylisé
    infos = [
        ("👤 Patients enregistrés", nb_patients, "#0984e3"),
        ("📅 Rendez-vous pris", nb_rdv, "#fdcb6e"),
        ("🩺 Consultations effectuées", nb_consult, "#00b894"),
    ]

    for label, value, color in infos:
        item = tk.Frame(stat_frame, bg="white")
        item.pack(fill="x", padx=10, pady=8)

        tk.Label(item, text=label, font=("Arial", 12, "bold"), fg=color, bg="white").pack(anchor="w")
        tk.Label(item, text=str(value), font=("Arial", 14), bg="white").pack(anchor="w")

    # Bouton de fermeture
    ttk.Button(fen, text="Fermer", command=fen.destroy).pack(pady=10)
def afficher_facturation(parent):
    fen = tk.Toplevel(parent)
    fen.title("Facturation")
    fen.geometry("600x400")
    fen.configure(bg="white")

    tree = ttk.Treeview(fen, columns=("ID", "Patient", "Montant", "Statut", "Date"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)
    tree.pack(expand=True, fill=tk.BOTH, pady=10)

    from db.connexion import connect_db
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.id, p.username AS patient, f.montant, f.statut, f.date_facture
            FROM factures f
            JOIN patients p ON f.patient_id = p.id
            ORDER BY f.date_facture DESC
        """)
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=(row['id'], row['patient'], row['montant'], row['statut'], row['date_facture']))
        cursor.close()
        conn.close()

    def ajouter_facture():
        fen_add = tk.Toplevel(fen)
        fen_add.title("Ajouter une facture")
        fen_add.geometry("300x250")
        tk.Label(fen_add, text="ID Patient:").pack(pady=5)
        entry_patient = tk.Entry(fen_add)
        entry_patient.pack(pady=5)
        tk.Label(fen_add, text="Montant:").pack(pady=5)
        entry_montant = tk.Entry(fen_add)
        entry_montant.pack(pady=5)
        tk.Label(fen_add, text="Statut:").pack(pady=5)
        entry_statut = tk.Entry(fen_add)
        entry_statut.pack(pady=5)
        def enregistrer():
            from db.connexion import connect_db
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO factures (patient_id, montant, statut) VALUES (%s, %s, %s)",
                    (entry_patient.get(), entry_montant.get(), entry_statut.get())
                )
                conn.commit()
                cursor.close()
                conn.close()
                # Recharge la liste
                tree.delete(*tree.get_children())
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT f.id, p.username AS patients, f.montant, f.statut, f.date_facture
                    FROM factures f
                    JOIN patient p ON f.patient_id = p.id
                    ORDER BY f.date_facture DESC
                """)
                for row in cursor.fetchall():
                    tree.insert("", tk.END, values=(row['id'], row['patient'], row['montant'], row['statut'], row['date_facture']))
                cursor.close()
                fen_add.destroy()
        tk.Button(fen_add, text="Enregistrer", bg="#00b894", fg="white", command=enregistrer).pack(pady=10)
    tk.Button(fen, text="Ajouter une facture", bg="#00b894", fg="white", command=ajouter_facture).pack(pady=5)

def exporter_dossier_pdf(patient_id):
    from db.connexion import connect_db
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patient WHERE id = %s", (patient_id,))
        patient = cursor.fetchone()
        cursor.execute("""
            SELECT c.date_consultation, c.diagnostic, c.prescription
            FROM consultations c
            JOIN rendezvous r ON c.rdv_id = r.id
            WHERE r.patient_id = %s
            ORDER BY c.date_consultation DESC
        """, (patient_id,))
        consultations = cursor.fetchall()
        cursor.close()
        conn.close()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Dossier du patient {patient['username']}", ln=True)
        for c in consultations:
            pdf.cell(200, 10, txt=f"{c['date_consultation']} - {c['diagnostic']} - {c['prescription']}", ln=True)
        pdf.output(f"dossier_patient_{patient_id}.pdf")
        messagebox.showinfo("Export PDF", "Dossier exporté en PDF !")

        barcode.generate('code128', str(patient_id), writer=ImageWriter(), output=f'barcode_{patient_id}')

def ouvrir_admin(admin_id):
    AdminDashboard(admin_id)

def afficher_stats_graphiques(parent):
    from db.connexion import connect_db
    conn = connect_db()
    mois = []
    nb_rdv = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MONTH(date_rdv) as mois, COUNT(*) as total
            FROM rendezvous
            GROUP BY mois
            ORDER BY mois
        """)
        for row in cursor.fetchall():
            mois_num = int(row[0])
            mois.append(calendar.month_name[mois_num])
            nb_rdv.append(row[1])
        cursor.close()
        conn.close()
    if mois:
        plt.figure(figsize=(8,4))
        plt.bar(mois, nb_rdv, color="#6c5ce7")
        plt.title("Nombre de rendez-vous par mois")
        plt.xlabel("Mois")
        plt.ylabel("Nombre de rendez-vous")
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showinfo("Statistiques", "Aucune donnée à afficher.")

def ouvrir_statistiques(self):
    from ui.page_statistiques import StatistiquesPage
    StatistiquesPage()