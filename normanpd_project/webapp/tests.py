import os
import pytest
from django.urls import reverse
from django.conf import settings
import subprocess
from scripts.clustering import (
    add_clusters_to_database,
    generate_cluster_plot_with_pca,
    generate_comparison_plot,
    generate_heatmap
)
import sqlite3

@pytest.fixture
def temp_db_path(tmp_path):
    """
    Fixture to create a temporary SQLite database with test data.

    Args:
        tmp_path: Pytest fixture for temporary directories.

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
    return db_path


@pytest.fixture
def setup_media_root(tmp_path):
    """
    Fixture to create a temporary media root directory.

    Args:
        tmp_path: Pytest fixture for temporary directories.

    Returns:
        Path: Path to the temporary media root directory.
    """
    media_root = tmp_path / "media"
    os.makedirs(media_root, exist_ok=True)
    return media_root


def test_upload_files_valid_url(client, mocker, setup_media_root):
    """
    Test that the `upload_files` view successfully processes a valid URL and renders the success page.

    Args:
        client (Client): Django test client for HTTP requests.
        mocker (MockerFixture): Pytest fixture for mocking functions.
        setup_media_root (Path): Temporary media root directory.

    Returns:
        None
    """
    # Mock subprocess.run to simulate successful script execution
    mocker.patch("subprocess.run", return_value=mocker.Mock(returncode=0))

    # Define form data with a valid URL
    form_data = {"url": "https://example.com/incident.pdf"}

    # Send POST request to the upload_files view
    response = client.post(reverse("upload_files"), data=form_data)

    # Assert that the request was successful and the success page is rendered
    assert response.status_code == 200, "Expected status code 200 for successful file upload."
    assert "successfully uploaded the file" in response.content.decode("utf-8").lower(), \
        "Expected success message in response content."


def test_process_files_visualizations(client, mocker, temp_db_path, setup_media_root):
    """
    Test that the `process_files` view generates clustering and visualizations correctly.

    Args:
        client (Client): Django test client for HTTP requests.
        mocker (MockerFixture): Pytest fixture for mocking functions.
        temp_db_path (str): Path to the temporary SQLite database with test data.
        setup_media_root (Path): Temporary media root directory.

    Returns:
        None
    """
    # Mock visualization generation functions
    mocker.patch("scripts.clustering.add_clusters_to_database", return_value=None)
    mocker.patch("scripts.clustering.generate_cluster_plot_with_pca", return_value="pca_cluster_plot.png")
    mocker.patch("scripts.clustering.generate_comparison_plot", return_value="comparison_plot.png")
    mocker.patch("scripts.clustering.generate_heatmap", return_value="heatmap.png")

    # Set up environment variables for testing
    settings.MEDIA_ROOT = setup_media_root
    settings.BASE_DIR = os.path.dirname(temp_db_path)

    # Send GET request to the process_files view
    response = client.get(reverse("process_files"))

    # Assert that the request was successful and visualizations are generated
    assert response.status_code == 200, "Expected status code 200 for successful processing."
    assert "pca_cluster_plot.png" in response.content.decode("utf-8").lower(), \
        "Expected PCA cluster plot in response content."
    assert "comparison_plot.png" in response.content.decode("utf-8").lower(), \
        "Expected comparison plot in response content."
    assert "heatmap.png" in response.content.decode("utf-8").lower(), \
        "Expected heatmap in response content."
