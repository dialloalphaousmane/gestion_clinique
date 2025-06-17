import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="alpho224",
            database="cliniques"
        )
        if connection.is_connected():
            print("✅ Connexion réussie à la base de données MySQL")
            return connection
    except Error as e:
        print("❌ Erreur lors de la connexion à MySQL :", e)
        return None

# Exemple d’utilisation
if __name__ == "__main__":
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        for table in cursor.fetchall():
            print("📄 Table :", table[0])
        cursor.close()
        conn.close()