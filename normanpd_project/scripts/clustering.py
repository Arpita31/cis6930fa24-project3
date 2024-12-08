import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
import sqlite3
import os
from django.conf import settings
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler



def preprocess_features(db_path):
    """
    Load and preprocess features from the database for clustering.
    """
    with sqlite3.connect(db_path) as conn:
        # Load data
        df = pd.read_sql_query("SELECT * FROM incidents", conn)

    # Select meaningful features for clustering
    selected_features = ['incident_time', 'incident_location', 'nature', 'incident_ori']
    df = df[selected_features]

    # Convert categorical features to numeric using One-Hot Encoding
    df_numeric = pd.get_dummies(df, drop_first=True)

    # Remove low-variance columns
    df_numeric = df_numeric.loc[:, df_numeric.var() > 0.01]

    # Standardize features
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_numeric)

    return df, df_numeric, df_scaled

def add_clusters_to_database(db_path, n_clusters):
    """
    Perform clustering on the data and add cluster labels to the SQLite database.
    """
    try:
        # Preprocess features
        df, _, df_scaled = preprocess_features(db_path)

        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df['cluster'] = kmeans.fit_predict(df_scaled)

        # Debugging: Check cluster distribution
        print("Cluster distribution:")
        print(df['cluster'].value_counts())

        # Save updated DataFrame back to the database
        with sqlite3.connect(db_path) as conn:
            df.to_sql('incidents', conn, if_exists='replace', index=False)
        print("Clusters added to the database.")
    except Exception as e:
        print(f"Error adding clusters to database: {e}")
        raise



def generate_cluster_plot_with_pca(db_path, n_clusters):
    """
    Generate a scatter plot for clustering results using PCA for dimensionality reduction.
    """
    try:
        # Ensure media directory exists
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # Preprocess features
        df, df_numeric, df_scaled = preprocess_features(db_path)

        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df['cluster'] = kmeans.fit_predict(df_scaled)

        # Reduce dimensions to 2D using PCA
        pca = PCA(n_components=2, random_state=42)
        reduced_data = pca.fit_transform(df_scaled)
        df['pca_x'] = reduced_data[:, 0]
        df['pca_y'] = reduced_data[:, 1]

        # Debugging: Validate PCA variance explained
        explained_variance = pca.explained_variance_ratio_
        print(f"PCA Explained Variance: {explained_variance}")

        # Create scatter plot
        plt.figure(figsize=(10, 6))
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        for cluster in df['cluster'].unique():
            cluster_data = df[df['cluster'] == cluster]
            plt.scatter(
                cluster_data['pca_x'],
                cluster_data['pca_y'],
                label=f'Cluster {cluster}',
                color=colors[cluster % len(colors)]
            )

        # Add cluster centroids in PCA space
        centroids_reduced = pca.transform(kmeans.cluster_centers_)
        plt.scatter(
            centroids_reduced[:, 0],
            centroids_reduced[:, 1],
            s=300,
            c='black',
            marker='X',
            label='Centroids'
        )

        # Add labels and title
        plt.title('PCA-Reduced Scatter Plot with Clusters')
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Save the plot
        plot_path = os.path.join(settings.MEDIA_ROOT, 'pca_cluster_plot.png')
        plt.savefig(plot_path)
        plt.close()
        return os.path.join(settings.MEDIA_URL, 'pca_cluster_plot.png')
    except Exception as e:
        print(f"Error generating PCA-based scatter plot: {e}")
        raise


def generate_comparison_plot(db_path):
    """
    Generate a bar chart comparing cluster sizes using data from SQLite database.
    """
    try:
        # Load data from the database
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query("SELECT cluster, COUNT(*) as count FROM incidents GROUP BY cluster", conn)

        # Create the bar chart
        plt.figure(figsize=(8, 6))
        plt.bar(df['cluster'], df['count'], color='skyblue')
        plt.title('Cluster Size Comparison')
        plt.xlabel('Cluster')
        plt.ylabel('Number of Records')

        # Save the plot
        plot_path = os.path.join(settings.MEDIA_ROOT, 'comparison_plot.png')
        plt.savefig(plot_path)
        plt.close()
        return os.path.join(settings.MEDIA_URL, 'comparison_plot.png')
    except Exception as e:
        print(f"Error generating comparison plot: {e}")
        raise

def generate_heatmap(db_path):
    """
    Generate a heatmap showing the frequency of incidents by time and location.
    """
    try:
        # Load data from the database
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query("SELECT incident_time, incident_location FROM incidents", conn)

        # Preprocess data for heatmap
        # Convert `incident_time` to hour of the day
        df['hour'] = pd.to_datetime(df['incident_time'], errors='coerce').dt.hour

        # Count incidents by hour and location
        heatmap_data = df.groupby(['hour', 'incident_location']).size().unstack(fill_value=0)

        # Create the heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, cmap='coolwarm', linewidths=0.5, cbar=True)
        plt.title('Incident Frequency by Hour and Location')
        plt.xlabel('Location')
        plt.ylabel('Hour of Day')
        plt.tight_layout()

        # Save the heatmap
        plot_path = os.path.join(settings.MEDIA_ROOT, 'heatmap.png')
        plt.savefig(plot_path)
        plt.close()
        return os.path.join(settings.MEDIA_URL, 'heatmap.png')
    except Exception as e:
        print(f"Error generating heatmap: {e}")
        raise

