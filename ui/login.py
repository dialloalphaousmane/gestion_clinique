import tkinter as tk
from tkinter import messagebox
from db.connexion import connect_db

from ui.admin_dashboard import AdminDashboard
from ui.page_medecin import MedecinPage
from ui.page_secretaire import SecretairePage
from ui.page_patient import PatientPage

def afficher_page_connexion():
    root = tk.Tk()
    root.title("Connexion - Clinique Médicale")
    root.geometry("900x500")
    root.configure(bg="#f0f4f7")

    # Création d'un cadre central
    frame = tk.Frame(root, bg="white", bd=2, relief="groove")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=350)

    # Titre
    tk.Label(frame, text="Connexion", font=("Helvetica", 18, "bold"), bg="white", fg="#007ACC").pack(pady=20)

    # Champ Login
    tk.Label(frame, text="Login", font=("Helvetica", 12), bg="white").pack(pady=(5, 0))
    entry_login = tk.Entry(frame, font=("Helvetica", 12), width=30)
    entry_login.pack(pady=5)

    # Champ Mot de passe
    tk.Label(frame, text="Mot de passe", font=("Helvetica", 12), bg="white").pack(pady=(10, 0))
    entry_password = tk.Entry(frame, font=("Helvetica", 12), show="*", width=30)
    entry_password.pack(pady=5)

    # ✅ Checkbox pour afficher/masquer le mot de passe
    def toggle_password():
        if show_password_var.get():
            entry_password.config(show="")
        else:
            entry_password.config(show="*")

    show_password_var = tk.BooleanVar()
    show_password_check = tk.Checkbutton(
        frame, 
        text="Afficher le mot de passe", 
        variable=show_password_var,
        command=toggle_password,
        bg="white",
        font=("Helvetica", 10)
    )
    show_password_check.pack(pady=(0, 10))

    # Fonction de connexion
    def se_connecter():
        login = entry_login.get()
        password = entry_password.get()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, login, password, role, doit_modifier_mdp FROM utilisateurs WHERE login = %s", (login,))
            utilisateur = cursor.fetchone()
            conn.close()

            if utilisateur:
                user_id, username, hashed_pw, role, doit_modifier = utilisateur
                if password == hashed_pw:
                    messagebox.showinfo("Connexion réussie", f"Bienvenue, {role}")
                    root.destroy()

                    user = {
                        'id': user_id,
                        'username': username,
                        'role': role
                    }

                    if role == "admin":
                        AdminDashboard(user).mainloop()
                    elif role == "medecin":
                        MedecinPage(user).mainloop()
                    elif role == "secretaire":
                        SecretairePage(user).mainloop()
                    elif role == "patient":
                        PatientPage(user).mainloop()
                    else:
                        messagebox.showerror("Erreur", "Rôle inconnu.")
                else:
                    messagebox.showerror("Erreur", "Mot de passe incorrect.")
            else:
                messagebox.showerror("Erreur", "Utilisateur non trouvé.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

    # Bouton Se connecter
    tk.Button(
        frame, 
        text="Se connecter", 
        command=se_connecter, 
        font=("Helvetica", 12, "bold"), 
        bg="#007ACC", 
        fg="white", 
        width=20
    ).pack(pady=10)

    root.mainloop()
