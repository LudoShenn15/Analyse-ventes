import matplotlib.pyplot as plt
import seaborn as sns
from analyse_data import main as analyze_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import plotly.express as px
import pandas as pd

# Configuration
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
os.makedirs('rapport', exist_ok=True)

def validate_data(results):
    """Valide la structure des données d'entrée"""
    if not results or not isinstance(results, dict):
        print("Erreur: Résultats d'analyse invalides")
        return False
    
    required_keys = ['df', 'top_produits', 'top_clients']
    for key in required_keys:
        if key not in results:
            print(f"Erreur: Clé manquante '{key}' dans les résultats")
            return False
    
    if not isinstance(results['df'], pd.DataFrame) or results['df'].empty:
        print("Erreur: DataFrame principal vide ou invalide")
        return False
    
    required_columns = ['montant', 'categorie', 'mois']
    for col in required_columns:
        if col not in results['df'].columns:
            print(f"Erreur: Colonne '{col}' manquante dans le DataFrame")
            return False
    
    return True

def plot_interactive_dashboard(results):
    """Crée un dashboard interactif HTML avec gestion robuste des erreurs"""
    try:
        if not validate_data(results):
            return

        df = results['df']
        
        # Création de la figure avec titre explicite
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "scatter"}, {"type": "bar"}],
            ],
            subplot_titles=(
                f"Top 5 Produits (€) - Total: {df['montant'].sum():,.2f}€",
                "Répartition par Catégorie",
                "Évolution Mensuelle (€)",
                "Meilleurs Clients (Nombre d'achats)"
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )

        # 1. Top produits
        top_produits = results['top_produits'].reset_index().head(5)
        fig.add_trace(
            go.Bar(
                x=top_produits['montant'],
                y=top_produits['produit'],
                orientation='h',
                text=top_produits['montant'].apply(lambda x: f"{x:,.2f}€"),
                textposition='auto',
                marker_color='#636EFA',
                name='CA par produit'
            ),
            row=1, col=1
        )

        # 2. Répartition catégories
        cat_df = df.groupby('categorie', as_index=False)['montant'].sum()
        fig.add_trace(
            go.Pie(
                labels=cat_df['categorie'],
                values=cat_df['montant'],
                textinfo='percent+label',
                marker=dict(colors=px.colors.qualitative.Pastel),
                hole=0.3,
                name='Par catégorie'
            ),
            row=1, col=2
        )

        # 3. Évolution mensuelle
        monthly = df.groupby('mois', as_index=False)['montant'].sum()
        fig.add_trace(
            go.Scatter(
                x=monthly['mois'],
                y=monthly['montant'],
                mode='lines+markers+text',
                text=monthly['montant'].apply(lambda x: f"{x:,.0f}€"),
                textposition='top center',
                line=dict(color='#00CC96', width=3),
                marker=dict(size=10),
                name='Évolution mensuelle'
            ),
            row=2, col=1
        )

        # 4. Top clients
        top_clients = results['top_clients'].reset_index().head(5)
        fig.add_trace(
            go.Bar(
                x=top_clients['client'],
                y=top_clients['CA'],
                text=top_clients['CA'].apply(lambda x: f"{x:,.2f}€"),
                textposition='auto',
                marker_color='#EF553B',
                name='CA par client'
            ),
            row=2, col=2
        )

        # Mise en page améliorée
        fig.update_layout(
            title_text=f"Tableau de Bord des Ventes - {len(df)} transactions analysées",
            height=1000,
            showlegend=False,
            template='plotly_white',
            margin=dict(t=100, b=50),
            hovermode='closest'
        )
        
        # Améliorations des axes
        fig.update_xaxes(title_text="Montant (€)", row=1, col=1)
        fig.update_yaxes(title_text="Produits", row=1, col=1)
        fig.update_xaxes(title_text="Mois", row=2, col=1)
        fig.update_yaxes(title_text="Montant (€)", row=2, col=1)
        fig.update_xaxes(title_text="Client", row=2, col=2)
        fig.update_yaxes(title_text="CA (€)", row=2, col=2)

        # Sauvegarde avec options optimisées
        fig.write_html(
            "rapport/dashboard_ventes.html",
            include_plotlyjs='cdn',  # Plus léger
            full_html=False,
            auto_open=True  # Ouvre automatiquement
        )
        print("\n Dashboard interactif généré: rapport/dashboard_ventes.html")

    except Exception as e:
        print(f"\n Erreur lors de la génération du dashboard: {str(e)}")
        if 'df' in locals():
            print("Aperçu des données problématiques:")
            print(df.head(2))
            if 'top_produits' in results:
                print("Top produits:")
                print(results['top_produits'].head(2))

def plot_static_charts(results):
    """Génère des graphiques statiques PNG avec vérifications"""
    try:
        if not validate_data(results):
            return

        df = results['df']
        
        # 1. Évolution mensuelle
        plt.figure(figsize=(14, 7))
        monthly = df.groupby('mois', as_index=False)['montant'].sum()
        ax = sns.lineplot(
            data=monthly,
            x='mois',
            y='montant',
            marker='o',
            markersize=10,
            linewidth=3,
            color='#1f77b4'
        )
        
        # Ajout des valeurs sur le graphique
        for line in range(0, monthly.shape[0]):
            ax.text(
                monthly['mois'].iloc[line],
                monthly['montant'].iloc[line],
                f"{monthly['montant'].iloc[line]:,.0f}€",
                horizontalalignment='center',
                size='medium',
                color='black'
            )

        plt.title(f"Évolution du CA Mensuel - Total: {monthly['montant'].sum():,.2f}€")
        plt.ylabel("Montant (€)")
        plt.xlabel("Mois")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("rapport/evolution_mensuelle.png", dpi=120)
        plt.close()

        # 2. Top produits
        plt.figure(figsize=(12, 7))
        top_produits = results['top_produits'].reset_index().head(5)
        ax = sns.barplot(
            data=top_produits,
            x='montant',
            y='produit',
            palette='viridis',
            edgecolor='black',
            linewidth=1
        )
        
        # Ajout des valeurs
        for p in ax.patches:
            width = p.get_width()
            ax.text(
                width + (0.02 * width),
                p.get_y() + p.get_height() / 2,
                f"{width:,.2f}€",
                ha='center',
                va='center'
            )

        plt.title("Top 5 Produits par Chiffre d'Affaires")
        plt.xlabel("Montant Total (€)")
        plt.ylabel("Produit")
        plt.tight_layout()
        plt.savefig("rapport/top_produits.png", dpi=120)
        plt.close()

        print("\n Graphiques statiques générés dans le dossier 'rapport'")

    except Exception as e:
        print(f"\n Erreur lors de la génération des graphiques statiques: {str(e)}")

def main():
    print("\nDébut de la génération des visualisations...")
    results = analyze_data()
    
    if results:
        plot_static_charts(results)
        plot_interactive_dashboard(results)
    else:
        print("Aucune donnée à visualiser")

if __name__ == '__main__':
    main()