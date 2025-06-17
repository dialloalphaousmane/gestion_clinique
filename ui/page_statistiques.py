import tkinter as tk
from tkinter import ttk
from db.connexion import connect_db

class StatistiquesPage(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Statistiques de la Clinique")
        self.geometry("500x400")
        self.configure(bg="#f5f6fa")

        tk.Label(self, text="Statistiques de fréquentation", font=("Arial", 16, "bold"), bg="#f5f6fa", fg="#0984e3").pack(pady=10)

        stats_frame = tk.Frame(self, bg="#f5f6fa")
        stats_frame.pack(pady=20)

        # Nombre de patients
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM patients")
            nb_patients = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM rendezvous")
            nb_rdv = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM consultations")
            nb_consult = cursor.fetchone()[0]

            cursor.execute("""
                SELECT DATE(date_rdv), COUNT(*) 
                FROM rendezvous 
                GROUP BY DATE(date_rdv) 
                ORDER BY DATE(date_rdv) DESC 
                LIMIT 7
            """)
            rdv_par_jour = cursor.fetchall()

            cursor.close()
            conn.close()
        else:
            nb_patients = nb_rdv = nb_consult = 0
            rdv_par_jour = []

        tk.Label(stats_frame, text=f"Nombre total de patients : {nb_patients}", font=("Arial", 12), bg="#f5f6fa").pack(anchor="w", pady=5)
        tk.Label(stats_frame, text=f"Nombre total de rendez-vous : {nb_rdv}", font=("Arial", 12), bg="#f5f6fa").pack(anchor="w", pady=5)
        tk.Label(stats_frame, text=f"Nombre total de consultations : {nb_consult}", font=("Arial", 12), bg="#f5f6fa").pack(anchor="w", pady=5)

        tk.Label(stats_frame, text="Rendez-vous par jour (7 derniers jours) :", font=("Arial", 12, "bold"), bg="#f5f6fa").pack(anchor="w", pady=10)
        for date, count in rdv_par_jour:
            tk.Label(stats_frame, text=f"{date} : {count} rendez-vous", font=("Arial", 11), bg="#f5f6fa").pack(anchor="w")

        # Ajoute d'autres stats selon tes besoins
