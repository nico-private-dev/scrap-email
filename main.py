#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Programme principal pour la prospection commerciale.
Ce script permet de:
1. Lire un fichier CSV contenant des URLs
2. Extraire les emails de ces sites web
3. Envoyer des emails de prospection
"""

import os
import argparse
from dotenv import load_dotenv

from url_processor import process_urls
from email_sender import send_emails

# Chargement des variables d'environnement
load_dotenv()

def main():
    """Point d'entrée principal du programme."""
    parser = argparse.ArgumentParser(description="Outil de prospection commerciale")
    parser.add_argument("--input", "-i", required=True, help="Fichier CSV contenant les URLs")
    parser.add_argument("--output", "-o", default="emails_extraits.csv", help="Fichier CSV de sortie pour les emails extraits")
    parser.add_argument("--template", "-t", default="email_template.txt", help="Modèle d'email à utiliser")
    parser.add_argument("--subject", "-s", default="Services de création de site internet", help="Sujet de l'email")
    parser.add_argument("--no-send", action="store_true", help="Ne pas envoyer d'emails, juste extraire les adresses")
    
    args = parser.parse_args()
    
    # Vérification que le fichier d'entrée existe
    if not os.path.exists(args.input):
        print(f"Erreur: Le fichier {args.input} n'existe pas.")
        return
    
    # Traitement des URLs et extraction des emails
    print(f"Traitement des URLs depuis {args.input}...")
    process_urls(args.input, args.output)
    
    # Envoi des emails si demandé
    if not args.no_send:
        if not os.path.exists(args.template):
            print(f"Erreur: Le modèle d'email {args.template} n'existe pas.")
            return
        
        # Charger les données du fichier de sortie
        print(f"Chargement des emails depuis {args.output}...")
        
        try:
            import csv
            with open(args.output, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                emails_data = [row for row in reader]
                
            if not emails_data:
                print("Aucun email trouvé dans le fichier de sortie.")
                return
                
            print(f"Envoi des emails avec le sujet: {args.subject}")
            send_emails(emails_data, args.template, args.subject)
        except Exception as e:
            print(f"Erreur lors du chargement ou de l'envoi des emails: {str(e)}")
    
    print("Traitement terminé!")

if __name__ == "__main__":
    main()
