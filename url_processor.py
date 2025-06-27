#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour traiter les URLs et extraire les adresses email.
"""

import re
import csv
import os
# Désactiver pandas pour éviter les problèmes de compatibilité
PANDAS_AVAILABLE = False

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import validators
import time
import random

# Expression régulière pour trouver les emails
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

def extract_emails_from_url(url):
    """
    Extrait les adresses email d'une URL donnée.
    
    Args:
        url (str): L'URL du site à scraper
        
    Returns:
        list: Liste des emails uniques trouvés
    """
    emails = set()
    
    # Vérifier si l'URL est valide
    if not validators.url(url):
        print(f"URL invalide: {url}")
        return list(emails)
    
    # Ajouter http:// si nécessaire
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Définir un User-Agent aléatoire pour éviter d'être bloqué
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        headers = {'User-Agent': random.choice(user_agents)}
        
        # Faire la requête HTTP avec un timeout
        response = requests.get(url, headers=headers, timeout=10)
        
        # Vérifier que la requête a réussi
        if response.status_code == 200:
            # Analyser le contenu HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire le texte de la page
            text = soup.get_text()
            
            # Trouver tous les emails dans le texte
            found_emails = re.findall(EMAIL_REGEX, text)
            emails.update(found_emails)
            
            # Chercher les emails dans les attributs href des liens (mailto:)
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href.startswith('mailto:'):
                    email = href[7:]  # Enlever 'mailto:'
                    if '@' in email:
                        emails.add(email)
            
            # Vérifier les pages de contact ou à propos
            contact_links = []
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.get_text().lower()
                if 'contact' in href.lower() or 'contact' in text or 'about' in href.lower() or 'à propos' in text:
                    if href.startswith('/'):
                        contact_links.append(url.rstrip('/') + href)
                    elif href.startswith('http'):
                        contact_links.append(href)
                    else:
                        contact_links.append(url.rstrip('/') + '/' + href)
            
            # Visiter les pages de contact pour y chercher des emails
            for contact_url in contact_links[:2]:  # Limiter à 2 pages de contact pour éviter de trop scraper
                try:
                    contact_response = requests.get(contact_url, headers=headers, timeout=5)
                    if contact_response.status_code == 200:
                        contact_soup = BeautifulSoup(contact_response.text, 'html.parser')
                        contact_text = contact_soup.get_text()
                        contact_emails = re.findall(EMAIL_REGEX, contact_text)
                        emails.update(contact_emails)
                except Exception as e:
                    print(f"Erreur lors de l'accès à la page de contact {contact_url}: {str(e)}")
                
                # Pause pour éviter de surcharger le serveur
                time.sleep(random.uniform(1, 2))
        
    except Exception as e:
        print(f"Erreur lors de l'accès à {url}: {str(e)}")
    
    return list(emails)

def process_urls(input_file, output_file):
    """
    Traite un fichier CSV contenant des URLs et extrait les emails.
    
    Args:
        input_file (str): Chemin vers le fichier CSV d'entrée
        output_file (str): Chemin vers le fichier CSV de sortie
        
    Returns:
        None
    """
    # Lire le fichier CSV
    try:
        with open(input_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = [row for row in reader]
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {input_file}: {str(e)}")
        return
    
    # Vérifier qu'il y a une colonne URL
    url_column = None
    for col in data[0].keys():
        if col.lower() in ['url', 'site', 'website', 'site_web', 'lien']:
            url_column = col
            break
    
    if url_column is None:
        print("Aucune colonne d'URL trouvée dans le fichier CSV.")
        print(f"Colonnes disponibles: {', '.join(data[0].keys())}")
        return
    
    # Créer une nouvelle colonne pour les emails
    for row in data:
        row['emails'] = None
    
    # Traiter chaque URL
    print(f"Extraction des emails à partir de {len(data)} URLs...")
    
    for row in tqdm(data, total=len(data)):
        url = row[url_column]
        if not url:
            continue
            
        # Extraire les emails
        emails = extract_emails_from_url(url)
        
        # Stocker les emails trouvés
        if emails:
            row['emails'] = ';'.join(emails)
        
        # Pause pour éviter de surcharger les serveurs
        time.sleep(random.uniform(0.5, 1.5))
    
    # Filtrer les lignes avec des emails
    emails_data = [row for row in data if row['emails']]
    
    # Sauvegarder les résultats
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(emails_data)
    print(f"{len(emails_data)} emails trouvés et sauvegardés dans {output_file}")

if __name__ == "__main__":
    # Test avec un petit exemple
    test_url = "https://www.example.com"
    print(f"Test d'extraction d'emails depuis {test_url}")
    emails = extract_emails_from_url(test_url)
    print(f"Emails trouvés: {emails}")
