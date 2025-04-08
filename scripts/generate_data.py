import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('fr_FR')

def generate_products():
    """ Génère des produits """
    categories = ['Electronique', 'Vêtements', 'Alimentation', 'Maison', 'Loisirs']
    products = []
    
    for _ in range(20):  # 20 produits
        category = random.choice(categories)
        if category == 'Electronique':
            name = f"{fake.word().capitalize()} {random.choice(['Pro', 'Max', 'Lite'])}"
            price = round(random.uniform(50, 1000), 2)  # 50-1000€
        elif category == 'Vêtements':
            name = f"{fake.word().capitalize()} {random.choice(['T-shirt', 'Pantalon', 'Robe'])}"
            price = round(random.uniform(10, 200), 2)  # 10-200€
        elif category == 'Alimentation':
            name = f"{fake.word().capitalize()} {random.choice(['Bio', 'Premium', 'Classique'])}"
            price = round(random.uniform(1, 20), 2)  # 1-20€
        else:
            name = fake.catch_phrase()
            price = round(random.uniform(5, 500), 2)  # 5-500€
            
        products.append((name, category, price, random.randint(10, 100)))
    
    return products

def generate_clients(n=50):
    """ Génère n clients """
    return [
        (fake.name(), fake.email(), fake.city(), fake.date_between('-2y').strftime('%Y-%m-%d'))
        for _ in range(n)
    ]

def generate_sales(conn):
    """ Génère des ventes en euros """
    c = conn.cursor()
    
    # Récupère les produits et clients
    produits = c.execute("SELECT produit_id, prix FROM Produits").fetchall()
    clients = c.execute("SELECT client_id FROM Clients").fetchall()
    
    if not produits or not clients:
        raise ValueError("Aucun produit ou client trouvé")
    
    # Génère 500 ventes
    for _ in range(500):
        produit_id, prix = random.choice(produits)
        client_id = random.choice(clients)[0]
        quantite = random.randint(1, 5)
        
        c.execute("""
        INSERT INTO Ventes (produit_id, client_id, date_vente, quantite, montant)
        VALUES (?, ?, ?, ?, ?)
        """, (
            produit_id,
            client_id,
            fake.date_between('-1y').strftime('%Y-%m-%d'),
            quantite,
            round(prix * quantite, 2)  # Montant total en euros
        ))
    
    conn.commit()

def main():
    try:
        with sqlite3.connect("database/ventes_magasin.db") as conn:
            # Produits
            conn.executemany("""
            INSERT INTO Produits (nom, categorie, prix, stock)
            VALUES (?, ?, ?, ?)
            """, generate_products())
            
            # Clients
            conn.executemany("""
            INSERT INTO Clients (nom, email, ville, date_inscription)
            VALUES (?, ?, ?, ?)
            """, generate_clients())
            
            # Ventes
            generate_sales(conn)
            
        print("Données générées avec succès ")
    except Exception as e:
        print(f"ERREUR: {e}")

if __name__ == '__main__':
    main()