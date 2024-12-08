import pytest
import os
import sqlite3
import pandas as pd
from scripts.clustering import (
    preprocess_features,
    add_clusters_to_database,
    generate_cluster_plot_with_pca,
    generate_comparison_plot,
    generate_heatmap
)
from django.conf import settings


@pytest.fixture
def temp_db_path(tmp_path):
    """
    Fixture to create a temporary SQLite database with mock data for testing.

    Args:
        tmp_path: pytest's temporary path object.

    Returns:
        str: Path to the temporary database.
    """
    db_path = tmp_path / "test_normanpd.db"
    conn = sqlite3.connect(db_path)
    # Create mock data for the `incidents` table
    data = {
        "incident_time": ["2024-12-08 10:00:00", "2024-12-08 12:00:00", "2024-12-08 14:00:00"],
        "incident_location": ["A", "B", "A"],
        "nature": ["Theft", "Assault", "Theft"],
        "incident_ori": ["ORI1", "ORI2", "ORI1"]
    }
    df = pd.DataFrame(data)
    df.to_sql("incidents", conn, if_exists="replace", index=False)
    conn.close()
    return str(db_path)


def test_preprocess_features(temp_db_path):
    """
    Test the preprocessing function to ensure it processes data correctly.

    Args:
        temp_db_path (str): Path to the temporary database.
    """
    df, df_numeric, df_scaled = preprocess_features(temp_db_path)
    assert df.shape[0] > 0, "Dataframe should not be empty"
    assert df_numeric.shape[1] > 0, "Numeric dataframe should not be empty"
    assert len(df_scaled) == len(df), "Scaled data should match original rows"


def test_add_clusters_to_database(temp_db_path):
    """
    Test the add_clusters_to_database function to ensure clusters are added correctly.

    Args:
        temp_db_path (str): Path to the temporary database.
    """
    add_clusters_to_database(temp_db_path, n_clusters=2)
    with sqlite3.connect(temp_db_path) as conn:
        df = pd.read_sql_query("SELECT DISTINCT cluster FROM incidents", conn)
    assert df["cluster"].nunique() == 2, "Number of clusters should match n_clusters"


def test_generate_cluster_plot_with_pca(temp_db_path, tmp_path):
    """
    Test PCA-based cluster plotting.

    Args:
        temp_db_path (str): Path to the temporary database.
        tmp_path: pytest's temporary path object.
    """
    os.environ["MEDIA_ROOT"] = str(tmp_path)  # Mock MEDIA_ROOT
    plot_path = generate_cluster_plot_with_pca(temp_db_path, n_clusters=2)
    assert os.path.exists(plot_path), "PCA cluster plot should be generated"


def test_generate_comparison_plot(temp_db_path, tmp_path):
    """
    Test the generation of the cluster size comparison plot.

    Args:
        temp_db_path (str): Path to the temporary database.
        tmp_path: pytest's temporary path object.
    """
    os.environ["MEDIA_ROOT"] = str(tmp_path)  # Mock MEDIA_ROOT
    plot_path = generate_comparison_plot(temp_db_path)
    assert os.path.exists(plot_path), "Comparison plot should be generated"


def test_generate_heatmap(temp_db_path, tmp_path):
    """
    Test the generation of the heatmap.

    Args:
        temp_db_path (str): Path to the temporary database.
        tmp_path: pytest's temporary path object.
    """
    os.environ["MEDIA_ROOT"] = str(tmp_path)  # Mock MEDIA_ROOT
    plot_path = generate_heatmap(temp_db_path)
    assert os.path.exists(plot_path), "Heatmap plot should be generated"


def test_empty_database(tmp_path):
    """
    Test behavior when the database is empty.

    Args:
        tmp_path: pytest's temporary path object.
    """
    db_path = tmp_path / "empty_normanpd.db"
    sqlite3.connect(db_path).close()  # Create an empty database
    with pytest.raises(Exception, match="no such table: incidents"):
        preprocess_features(str(db_path))


def test_invalid_cluster_number(temp_db_path):
    """
    Test behavior when an invalid number of clusters is provided.

    Args:
        temp_db_path (str): Path to the temporary database.
    """
    with pytest.raises(ValueError, match="Number of clusters must be greater than 1"):
        add_clusters_to_database(temp_db_path, n_clusters=1)
