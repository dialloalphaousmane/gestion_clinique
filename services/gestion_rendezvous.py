from db.connexion import connect_db

def lister_rendezvous():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT r.id, r.date_rdv, r.duree, r.statut,
                       u_p.nom AS nom_patient, u_p.prenom AS prenom_patient,
                       u_m.nom AS nom_medecin, u_m.prenom AS prenom_medecin
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                JOIN medecins m ON r.medecin_id = m.id
                JOIN utilisateurs u_p ON p.user_id = u_p.id
                JOIN utilisateurs u_m ON m.user_id = u_m.id
                ORDER BY r.date_rdv DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return []

def creer_rendezvous(patient_id, medecin_id, date_rdv, duree, statut="en attente"):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO rendezvous (patient_id, medecin_id, date_rdv, duree, statut)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_id, medecin_id, date_rdv, duree, statut))
            conn.commit()
            return True
        except Exception as e:
            print("Erreur création rendez-vous :", e)
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def supprimer_rendezvous(rdv_id):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rendezvous WHERE id = %s", (rdv_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("Erreur suppression rendez-vous :", e)
            return False
        finally:
            cursor.close()
            conn.close()
    return False