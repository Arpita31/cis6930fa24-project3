import os
import sys
import subprocess
from django.shortcuts import render, redirect
from django.conf import settings
from scripts.project0 import createdb
from .forms import UploadFileForm
from .models import UploadedFile
from scripts.clustering import (
    add_clusters_to_database,
    generate_cluster_plot_with_pca,
    generate_comparison_plot,
    generate_heatmap,
)

def upload_files(request):
    """
    View to process the input URL, pass it to `main.py`, and generate a CSV output.
    """
    # Output CSV file path
    output_file = os.path.join(settings.MEDIA_ROOT, "incident_output.csv")
    
    if request.method == "POST":
        form = UploadFileForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["url"]

            try:
                # Full path to the Python executable
                python_executable = sys.executable

                # Run the `main.py` script with the provided URL
                cwd = os.path.join(settings.BASE_DIR, "scripts")
                print(f"Resolved CWD: {cwd}")
                print(f"Path Exists: {os.path.exists(cwd)}")
                print(f"Directory Contents: {os.listdir(cwd) if os.path.exists(cwd) else 'Not Found'}")


                result = subprocess.run(
                    [python_executable, "main.py", "--incidents", url],
                    capture_output=True,
                    text=True,
                    cwd=os.path.join(settings.BASE_DIR, "scripts"),  # Ensure `main.py` is in the `scripts` folder
                )

                # Check if the script ran successfully
                if result.returncode != 0:
                    raise Exception(result.stderr)

                # Export data from the SQLite database to a CSV file
                db_path = os.path.abspath(os.path.join(os.getcwd(), "media/normanpd.db"))

                # Render the success page with a link to the output CSV
                return render(
                    request,
                    "webapp/success.html",
                    {"url": url, "output_file": os.path.join(settings.MEDIA_URL, "incident_output.csv")},
                )
            except Exception as e:
                # Render the error page with the exception message
                return render(request, "webapp/error.html", {"error": str(e)})

    else:
        form = UploadFileForm()

    # Render the upload page with the URL input form
    return render(request, "webapp/home.html", {"form": form})


def process_files(request):
    try:
        db_path = os.path.join(settings.BASE_DIR, 'scripts', 'resources', 'normanpd.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Process database and generate visualizations
        add_clusters_to_database(db_path, n_clusters=3)
        visualizations = {
            'Cluster_Plot_with_PCA': generate_cluster_plot_with_pca(db_path, n_clusters=3),
            'Comparison_Plot': generate_comparison_plot(db_path),
            'Heatmap': generate_heatmap(db_path),
        }

        # Debug print for paths
        print("Visualizations:", visualizations)

        return render(request, 'webapp/visualizations.html', {'visualizations': visualizations})

    except Exception as e:
        print(f"Error processing files: {e}")
        return render(request, 'webapp/home.html', {"error": f"Error: {e}"})
