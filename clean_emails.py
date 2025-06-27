#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour nettoyer les adresses email extraites.
"""

import re
import csv
import os

# Expression régulière pour extraire uniquement les adresses email valides
# Cette regex est plus stricte que celle utilisée pour l'extraction initiale
# Utilisation de \b (word boundary) pour s'assurer que l'email se termine correctement
# Limitation des TLDs à 2-6 caractères pour éviter de capturer des caractères indésirables
EMAIL_REGEX = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]{2,6})\b'

def clean_email(email):
    """
    Nettoie une adresse email en extrayant uniquement la partie valide.
    
    Args:
        email (str): Adresse email potentiellement mal formatée
        
    Returns:
        str: Adresse email nettoyée ou chaîne vide si invalide
    """
    match = re.search(EMAIL_REGEX, email)
    if match:
        return match.group(1)
    return ""

def clean_emails_file(input_file, output_file):
    """
    Nettoie toutes les adresses email dans un fichier CSV.
    
    Args:
        input_file (str): Chemin vers le fichier CSV d'entrée
        output_file (str): Chemin vers le fichier CSV de sortie
    """
    # Vérifier que le fichier d'entrée existe
    if not os.path.exists(input_file):
        print(f"Erreur: Le fichier {input_file} n'existe pas.")
        return
    
    # Lire le fichier CSV
    try:
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {input_file}: {str(e)}")
        return
    
    # Vérifier la structure du fichier
    if not data:
        print("Le fichier CSV est vide.")
        return
    
    # Trouver l'index de la colonne des emails
    header = data[0]
    email_col_idx = None
    
    for i, col in enumerate(header):
        if col.lower() in ['emails', 'email', 'mail', 'courriel']:
            email_col_idx = i
            break
    
    if email_col_idx is None:
        # Si pas de colonne spécifique, on suppose que c'est la dernière colonne
        email_col_idx = len(header) - 1
    
    # Nettoyer les emails
    cleaned_data = []
    cleaned_data.append(header)  # Ajouter l'en-tête
    
    total_emails_before = 0
    total_emails_after = 0
    
    for row in data[1:]:  # Ignorer l'en-tête
        if len(row) <= email_col_idx:
            # Ignorer les lignes trop courtes
            continue
        
        # Récupérer les emails
        emails_str = row[email_col_idx]
        if not emails_str:
            cleaned_data.append(row)
            continue
        
        # Séparer les emails (ils peuvent être séparés par des points-virgules)
        emails_list = emails_str.split(';')
        total_emails_before += len(emails_list)
        
        # Nettoyer chaque email
        cleaned_emails = []
        for email in emails_list:
            cleaned = clean_email(email)
            if cleaned:
                cleaned_emails.append(cleaned)
        
        total_emails_after += len(cleaned_emails)
        
        # Mettre à jour la ligne avec les emails nettoyés
        new_row = row.copy()
        new_row[email_col_idx] = ';'.join(cleaned_emails)
        cleaned_data.append(new_row)
    
    # Écrire le fichier de sortie
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(cleaned_data)
        print(f"Nettoyage terminé! Fichier sauvegardé sous {output_file}")
        print(f"Emails avant nettoyage: {total_emails_before}")
        print(f"Emails après nettoyage: {total_emails_after}")
        print(f"Emails supprimés: {total_emails_before - total_emails_after}")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {output_file}: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Nettoyer les adresses email extraites")
    parser.add_argument("--input", "-i", default="emails_extraits.csv", help="Fichier CSV contenant les emails à nettoyer")
    parser.add_argument("--output", "-o", default="emails_propres.csv", help="Fichier CSV de sortie pour les emails nettoyés")
    
    args = parser.parse_args()
    
    clean_emails_file(args.input, args.output)
