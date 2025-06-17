import smtplib
from email.mime.text import MIMEText

def envoyer_email_confirmation(destinataire, username, mdp_temp):
    msg = MIMEText(
        f"Bonjour {username},\n\n"
        f"Votre compte a été créé.\n"
        f"Voici votre mot de passe temporaire : {mdp_temp}\n"
        f"Merci de vous connecter et de changer votre mot de passe.\n\n"
        "Cordialement,\nL'équipe Clinique"
    )
    msg['Subject'] = "Création de votre compte Clinique"
    msg['From'] = "no-reply@clinique.com"
    msg['To'] = destinataire

    # Connexion SMTP (exemple Gmail)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('alphaousmanedinguicity@gmail.com', 'diallo224')
        server.send_message(msg)