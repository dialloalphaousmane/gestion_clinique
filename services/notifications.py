import smtplib
from email.mime.text import MIMEText

def envoyer_email(destinataire, sujet, message, expediteur, mdp):
    msg = MIMEText(message)
    msg['Subject'] = sujet
    msg['From'] = expediteur
    msg['To'] = destinataire

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(expediteur, mdp)
            server.sendmail(expediteur, [destinataire], msg.as_string())
        return True
    except Exception as e:
        print("Erreur envoi mail:", e)
        return False