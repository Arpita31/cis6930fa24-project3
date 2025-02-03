# Data visualization

Name: Arpita Patnaik
<br>cis6930fa24 -- Project 3

# Project Description
This project processes police incident data by performing clustering, dimensionality reduction, and generating insightful visualizations. It handles file uploads, extracts features, clusters the data into meaningful groups, and provides visual analysis through scatter plots, heatmaps, and bar charts. The project uses PCA to visualize clusters in two dimensions and includes tools to determine the optimal number of clusters.

# Application video link - 
https://drive.google.com/file/d/17LIxbcCFP_8z0oH4IaRqH7wxqY9SEbLQ/view?usp=sharing

# How to Install
```
$ pipenv install django
$ pipenv install scikit-learn
$ pipenv install pandas
$ pipenv install numpy
$ pipenv install matplotlib
$ pipenv install seaborn
$ pipenv install gunicorn
$ pipenv install -e .
```


## How to Run
To run the Django application:
```$ pipenv run python manage.py runserver```


To access the application:
1. Open a web browser and navigate to `http://127.0.0.1:8000/`.
2. Upload the required incident data file link from https://www.normanok.gov/public-safety/police-department/crime-prevention-data/department-activity-reports. A data file example: https://www.normanok.gov/sites/default/files/documents/2024-12/2024-12-05_daily_incident_summary.pdf.
3. Click the process button to perform clustering and generate visualizations.
4. View the generated plots and cluster details on the results page.

Sample visualizations generated include:
1. PCA-based scatter plot for clusters.
2. Bar chart comparing cluster sizes.
3. Heatmap of incidents by time and location.

## Functions
1. **File Upload and Preprocessing**
   - Uploads incident files via the web interface and extracts data.

2. **Clustering**
   - Uses KMeans clustering to group incidents based on selected features.
   - Reduces dimensionality with PCA for better visualization.

3. **Visualizations**
   - Generates PCA-based scatter plots to show cluster separation.
   - Creates heatmaps for incident density by time and location.
   - Produces bar charts comparing the sizes of different clusters.

4. **Django Views**
   - `process_files`: Handles file uploads, updates the database, performs clustering, and generates visualizations.
   - Renders results on an HTML page for user analysis.

6. **Database Management**
   - Stores processed incident data and cluster labels in SQLite.
   - Provides APIs to fetch data for visualizations.

## Bugs and Assumptions

### Bugs:
1. Clustering might assign imbalanced clusters if features are highly correlated or not well-scaled.
2. Certain low-variance features might inadvertently affect PCA-based visualizations.

### Assumptions:
1. Data preprocessing removes low-variance features to improve clustering accuracy.
2. Incident data adheres to a consistent format, with well-defined time, location, and nature columns.
3. Here 3 clusters are used.




