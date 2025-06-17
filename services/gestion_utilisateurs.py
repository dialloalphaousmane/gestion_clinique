from db.connexion import connect_db
import bcrypt

def ajouter_utilisateur(login, password, role, email):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO utilisateurs (login, password, role, email) VALUES (%s, %s, %s, %s)",
                (login, hashed, role, email)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()
    return None

def ajouter_medecin(user_id, specialite, matricule):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO medecins (user_id, specialite, matricule) VALUES (%s, %s, %s)",
                (user_id, specialite, matricule)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()
    return None

def lister_medecins():
    conn = connect_db()
    medecins = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT m.id, u.login, u.email, m.specialite, m.matricule
                FROM medecins m
                JOIN utilisateurs u ON m.user_id = u.id
            """)
            medecins = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return medecins

def supprimer_medecin(medecin_id):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medecins WHERE id = %s", (medecin_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    return False

def ajouter_secretaire(user_id):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO secretaire (user_id) VALUES (%s)",
                (user_id,)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()
    return None

def lister_secretaires():
    conn = connect_db()
    secretaires = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT s.id, u.login, u.email
                FROM secretaire s
                JOIN utilisateurs u ON s.user_id = u.id
            """)
            secretaires = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return secretaires

def supprimer_secretaire(secretaire_id):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM secretaire WHERE id = %s", (secretaire_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    return False

def annuler_rendezvous(rdv_id):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE rendezvous SET statut = 'annulé' WHERE id = %s", (rdv_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    return False

def lister_utilisateurs_medecins():
    conn = connect_db()
    utilisateurs = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, login, email FROM utilisateurs WHERE role = 'medecin'")
            utilisateurs = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return utilisateurs