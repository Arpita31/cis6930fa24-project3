import pytest
import os
import sqlite3
import pandas as pd
import django
from scripts.clustering import (
    preprocess_features,
    add_clusters_to_database,
    generate_cluster_plot_with_pca,
    generate_comparison_plot,
    generate_heatmap
)
from django.test.utils import override_settings


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary SQLite database with mock data."""
    db_path = tmp_path / "test_normanpd.db"
    conn = sqlite3.connect(db_path)
    pd.DataFrame({
        "incident_time": ["2024-12-08 10:00:00", "2024-12-08 12:00:00", "2024-12-08 14:00:00"],
        "incident_location": ["A", "B", "A"],
        "nature": ["Theft", "Assault", "Theft"],
        "incident_ori": ["ORI1", "ORI2", "ORI1"]
    }).to_sql("incidents", conn, if_exists="replace", index=False)
    conn.close()
    return str(db_path)


@pytest.fixture
def mock_django_settings(tmp_path):
    """Mock Django settings for MEDIA_ROOT and MEDIA_URL."""
    media_root = tmp_path / "media"
    media_root.mkdir(exist_ok=True)
    if not django.conf.settings.configured:
        django.setup()
    with override_settings(MEDIA_ROOT=str(media_root), MEDIA_URL="/media/"):
        yield media_root


def test_preprocess_features(temp_db_path):
    df, df_numeric, df_scaled = preprocess_features(temp_db_path)
    assert not df.empty and not df_numeric.empty
    assert len(df_scaled) == len(df)


def test_add_clusters_to_database(temp_db_path):
    add_clusters_to_database(temp_db_path, n_clusters=2)
    with sqlite3.connect(temp_db_path) as conn:
        clusters = pd.read_sql_query("SELECT DISTINCT cluster FROM incidents", conn)
    assert clusters["cluster"].nunique() == 2


def test_empty_database(tmp_path):
    empty_db_path = tmp_path / "empty.db"
    sqlite3.connect(empty_db_path).close()
    with pytest.raises(Exception, match="no such table: incidents"):
        preprocess_features(str(empty_db_path))


import pytest
import os
import sqlite3
import pandas as pd
import django
from django.conf import settings
from django.test.utils import override_settings
from scripts.clustering import (
    preprocess_features,
    add_clusters_to_database,
    generate_cluster_plot_with_pca,
    generate_comparison_plot,
    generate_heatmap
)

import os
import django

# Set DJANGO_SETTINGS_MODULE before running any tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "normanpd_project.settings")
django.setup()


def test_generate_cluster_plot_with_pca(temp_db_path, mock_django_settings):
    """
    Test generation of the PCA-based cluster plot.
    """
    media_root = mock_django_settings
    add_clusters_to_database(temp_db_path, n_clusters=2)
    plot_path = generate_cluster_plot_with_pca(temp_db_path, n_clusters=2)
    assert os.path.exists(os.path.join(media_root, os.path.basename(plot_path)))


def test_generate_comparison_plot(temp_db_path, mock_django_settings):
    """
    Test generation of the cluster comparison plot.
    """
    media_root = mock_django_settings
    add_clusters_to_database(temp_db_path, n_clusters=2)
    plot_path = generate_comparison_plot(temp_db_path)
    assert os.path.exists(os.path.join(media_root, os.path.basename(plot_path)))


def test_generate_heatmap(temp_db_path, mock_django_settings):
    """
    Test generation of the cluster heatmap.
    """
    media_root = mock_django_settings
    add_clusters_to_database(temp_db_path, n_clusters=2)
    plot_path = generate_heatmap(temp_db_path)
    assert os.path.exists(os.path.join(media_root, os.path.basename(plot_path)))
