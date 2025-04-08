import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ Crée une connexion à la base de données SQLite """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connexion à SQLite réussie : {db_file}")
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ Crée les tables avec l'euro comme monnaie unique """
    try:
        c = conn.cursor()
        
        # Table Produits (prix en euros)
        c.execute("""
        CREATE TABLE IF NOT EXISTS Produits (
            produit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            categorie TEXT,
            prix REAL NOT NULL,  
            stock INTEGER DEFAULT 0
        )""")
        
        # Table Clients
        c.execute("""
        CREATE TABLE IF NOT EXISTS Clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT,
            ville TEXT,
            date_inscription DATE
        )""")
        
        # Table Ventes (montant en euros)
        c.execute("""
        CREATE TABLE IF NOT EXISTS Ventes (
            vente_id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            date_vente DATE NOT NULL,
            quantite INTEGER NOT NULL,
            montant REAL NOT NULL,  
            FOREIGN KEY (produit_id) REFERENCES Produits (produit_id),
            FOREIGN KEY (client_id) REFERENCES Clients (client_id)
        )""")
        
        conn.commit()
        print("Tables créées avec succès ")
        
    except Error as e:
        print(f"Erreur création tables: {e}")
        conn.rollback()

def main():
    database = "database/ventes_magasin.db"
    conn = create_connection(database)
    if conn:
        create_tables(conn)
        conn.close()

if __name__ == '__main__':
    main()