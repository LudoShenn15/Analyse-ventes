import sqlite3
import pandas as pd
from datetime import datetime

def connect_db():
    return sqlite3.connect('database/ventes_magasin.db')

def load_data(conn):
    query = """
    SELECT 
        v.vente_id,
        v.date_vente,
        p.nom as produit,
        p.categorie,
        p.prix as prix_unitaire,
        c.nom as client,
        c.ville,
        v.quantite,
        v.montant
    FROM Ventes v
    JOIN Produits p ON v.produit_id = p.produit_id
    JOIN Clients c ON v.client_id = c.client_id
    """
    df = pd.read_sql_query(query, conn)
    
    # Conversion des types
    df['date_vente'] = pd.to_datetime(df['date_vente'])
    df['montant'] = pd.to_numeric(df['montant'])
    df['mois'] = df['date_vente'].dt.strftime('%Y-%m')  # Format texte pour la visualisation
    
    return df

def analyze(df):
    print("\n=== ANALYSE DES VENTES EN EUROS ===")
    
    # Calcul des statistiques
    ca_total = df['montant'].sum()
    panier_moyen = df['montant'].mean()
    
    print(f"\nCA Total: {ca_total:,.2f} €")
    print(f"Panier moyen: {panier_moyen:,.2f} €")
    
    # Top produits
    top_produits = df.groupby(['produit', 'categorie'])['montant'] \
                   .sum().nlargest(5)
    print("\nTop 5 Produits:")
    print(top_produits.to_string(float_format="%.2f €"))
    
    # Top clients
    top_clients = df.groupby('client') \
                  .agg(CA=('montant', 'sum'), Achats=('vente_id', 'count')) \
                  .nlargest(5, 'CA')
    print("\nTop 5 Clients:")
    print(top_clients.to_string(float_format="%.2f €"))
    
    return {
        'df': df,
        'ca_total': ca_total,
        'panier_moyen': panier_moyen,
        'top_produits': top_produits,
        'top_clients': top_clients
    }

def main():
    try:
        with connect_db() as conn:
            df = load_data(conn)
            results = analyze(df)
        return results
    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")
        return None

if __name__ == '__main__':
    analysis_results = main()