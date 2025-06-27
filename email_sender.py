#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour l'envoi d'emails de prospection.
"""

import os
import smtplib
import time
import random
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tqdm import tqdm

# Désactiver pandas pour éviter les problèmes de compatibilité
PANDAS_AVAILABLE = False

def send_email(to_email, subject, body, from_email=None, smtp_server=None, smtp_port=None, 
               smtp_username=None, smtp_password=None):
    """
    Envoie un email à une adresse spécifiée.
    
    Args:
        to_email (str): Adresse email du destinataire
        subject (str): Sujet de l'email
        body (str): Corps de l'email (peut contenir du HTML)
        from_email (str, optional): Adresse email de l'expéditeur
        smtp_server (str, optional): Serveur SMTP
        smtp_port (int, optional): Port SMTP
        smtp_username (str, optional): Nom d'utilisateur SMTP
        smtp_password (str, optional): Mot de passe SMTP
        
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    # Utiliser les variables d'environnement si les paramètres ne sont pas spécifiés
    from_email = from_email or os.environ.get('SMTP_FROM_EMAIL')
    smtp_server = smtp_server or os.environ.get('SMTP_SERVER')
    smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', 587))
    smtp_username = smtp_username or os.environ.get('SMTP_USERNAME')
    smtp_password = smtp_password or os.environ.get('SMTP_PASSWORD')
    
    # Vérifier que toutes les informations nécessaires sont disponibles
    if not all([from_email, smtp_server, smtp_port, smtp_username, smtp_password]):
        print("Erreur: Informations SMTP manquantes. Veuillez configurer les variables d'environnement ou fournir les paramètres.")
        return False
    
    try:
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Ajouter le corps du message
        msg.attach(MIMEText(body, 'html'))
        
        # Connexion au serveur SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Sécuriser la connexion
        server.login(smtp_username, smtp_password)
        
        # Envoyer l'email
        server.send_message(msg)
        server.quit()
        
        return True
    
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email à {to_email}: {str(e)}")
        return False

def send_emails(emails_data, template_file, subject):
    """
    Envoie des emails à toutes les adresses dans les données.
    
    Args:
        emails_data (list ou DataFrame): Données contenant les emails et autres informations
        template_file (str): Chemin vers le fichier modèle d'email
        subject (str): Sujet de l'email
        
    Returns:
        int: Nombre d'emails envoyés avec succès
    """
    # Vérifier que les données contiennent des emails
    if not isinstance(emails_data, list) or not all(isinstance(row, dict) for row in emails_data):
        print("Données invalides. Veuillez fournir une liste de dictionnaires.")
        return 0
    
    # Lire le modèle d'email
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture du modèle d'email {template_file}: {str(e)}")
        return 0
    
    # Vérifier les variables d'environnement SMTP
    if not all([os.environ.get('SMTP_FROM_EMAIL'), os.environ.get('SMTP_SERVER'),
                os.environ.get('SMTP_USERNAME'), os.environ.get('SMTP_PASSWORD')]):
        print("Configuration SMTP manquante. Veuillez créer un fichier .env avec les variables suivantes:")
        print("SMTP_FROM_EMAIL=votre_email@exemple.com")
        print("SMTP_SERVER=smtp.exemple.com")
        print("SMTP_PORT=587")
        print("SMTP_USERNAME=votre_username")
        print("SMTP_PASSWORD=votre_password")
        return 0
    
    # Compteur d'emails envoyés
    sent_count = 0
    
    # Parcourir toutes les lignes des données
    print(f"Envoi d'emails à {len(emails_data)} destinataires...")
    for row in tqdm(emails_data, total=len(emails_data)):
        # Récupérer les emails (peut contenir plusieurs emails séparés par des ;)
        email_list = row.get('emails', '').split(';')
        
        for email in email_list:
            email = email.strip()
            if not email:
                continue
                
            # Personnaliser le modèle d'email avec les informations disponibles
            personalized_body = template
            
            # Remplacer les variables dans le modèle
            for key, value in row.items():
                if key != 'emails':
                    placeholder = f"{{{{{key}}}}}"
                    personalized_body = personalized_body.replace(placeholder, str(value))
            
            # Envoyer l'email
            if send_email(email, subject, personalized_body):
                sent_count += 1
                
            # Pause aléatoire pour éviter d'être marqué comme spam
            time.sleep(random.uniform(2, 5))
    
    print(f"{sent_count} emails envoyés avec succès.")
    return sent_count

if __name__ == "__main__":
    # Test avec un petit exemple
    # Créer des données de test
    test_data = [
        {'url': 'https://example.com', 'emails': 'test@example.com'}
    ]
    
    # Créer un modèle d'email de test
    with open('test_template.txt', 'w', encoding='utf-8') as f:
        f.write("""
        <html>
        <body>
        <p>Bonjour,</p>
        <p>J'ai visité votre site {{url}} et je souhaite vous proposer mes services de création de site internet.</p>
        <p>Cordialement,<br>Votre Nom</p>
        </body>
        </html>
        """)
    
    # Tester l'envoi d'email (ne fonctionnera pas sans configuration SMTP valide)
    print("Test d'envoi d'email (nécessite une configuration SMTP valide)")
    send_emails(test_data, 'test_template.txt', 'Test de prospection')
