import pytest
from django.urls import reverse
import sqlite3
import pandas as pd
from unittest.mock import patch, Mock


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary SQLite database with test data."""
    db_path = tmp_path / "test_normanpd.db"
    conn = sqlite3.connect(db_path)
    pd.DataFrame({
        "incident_time": ["2024-12-08 10:00:00", "2024-12-08 12:00:00", "2024-12-08 14:00:00"],
        "incident_location": ["A", "B", "A"],
        "nature": ["Theft", "Assault", "Theft"],
        "incident_ori": ["ORI1", "ORI2", "ORI1"]
    }).to_sql("incidents", conn, if_exists="replace", index=False)
    conn.close()
    return db_path


@pytest.fixture
def setup_media_root(tmp_path):
    """Create a temporary media root directory."""
    media_root = tmp_path / "media"
    media_root.mkdir(exist_ok=True)
    return media_root


def test_upload_files(client):
    """Test file upload with a valid URL."""
    with patch("subprocess.run", return_value=Mock(returncode=0)):
        response = client.post(reverse("upload_files"), data={"url": "https://example.com/incident.pdf"})
    assert response.status_code == 200
    assert "successfully uploaded" in response.content.decode().lower()


def test_process_files(client, temp_db_path, setup_media_root):
    """Test that clustering and visualizations are generated."""
    with patch("scripts.clustering.add_clusters_to_database"), \
         patch("scripts.clustering.generate_cluster_plot_with_pca", return_value="pca_cluster_plot.png"), \
         patch("scripts.clustering.generate_comparison_plot", return_value="comparison_plot.png"), \
         patch("scripts.clustering.generate_heatmap", return_value="heatmap.png"):
        response = client.get(reverse("process_files"))

    assert response.status_code == 200
    content = response.content.decode().lower()
    assert "pca_cluster_plot.png" in content
    assert "comparison_plot.png" in content
    assert "heatmap.png" in content
