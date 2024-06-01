import os
import pandas as pd
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import requests
import pandas as pd
import supplementary_functions
import config

def analyze_crawled_data(crawled_data, task_id):
    # Create unique directory for each task
    base_dir = f"./output/{task_id}"
    os.makedirs(base_dir, exist_ok=True)
    supplementary_functions.ensure_writable(base_dir)
    # Convert list of dictionaries to a DataFrame
    df = pd.DataFrame(crawled_data)
    print("DataFrame shape:", df.shape)
    df.columns = df.columns.astype(str)
    df.columns = df.columns.str.lower()
    expected_columns = ["name", "description", "hq_city", "hq_country", "startup_friendly_badge", "startup_partners_count"]

    # Check for missing columns and add them with default values
    for column in expected_columns:
        if column not in df.columns:
            # Assign default value based on the expected data type
            if column == "startup_friendly_badge":
                df[column] = "NO"  # Default to 'NO'
            elif column == "startup_partners_count":
                df[column] = 0  # Default to 0
            else:
                df[column] = ""
       
    # Convert to strings and ensure proper values
    df["startup_friendly_badge"] = df["startup_friendly_badge"].apply(
        lambda x: 1 if str(x).strip().upper() == "YES" else 0
    )

    # Check the number of rows in the DataFrame
    print("Number of rows:", len(df))

    # Check for missing or NaN values in key columns
    print("Missing values:", df.isnull().sum())
 
    # Fill NaN or None with a default value in key columns
    for column in expected_columns:
        if column not in df.columns:
            df[column] = ""  # Default to empty string for text
        else:
            df[column].fillna("", inplace=True)  # Default to empty string

    # Define the transformation for text-based features (TF-IDF)
    name_vectorizer = TfidfVectorizer(sublinear_tf=True).fit(df['name'])   # For 'name'
    description_vectorizer = TfidfVectorizer(  sublinear_tf=True).fit(df['description'])   # For 'description'

    # Define the transformation for categorical features (One-Hot Encoding)
    categorical_transformer = OneHotEncoder(sparse_output=False)

    # Define the transformation for numeric features (Standard Scaling)
    numeric_transformer = StandardScaler()

    # Combine the transformations into a ColumnTransformer
    feature_transformer = ColumnTransformer(
        transformers=[
            #("description_tfidf", description_vectorizer, "description"),
            ("categorical", categorical_transformer, ["hq_country"]),
            ("numeric", numeric_transformer, ["startup_partners_count"]),
            #("name_tfidf", name_vectorizer, "name"),  # TF-IDF for 'name'
            ("boolean", "passthrough", ["startup_friendly_badge"]),  # Boolean values are pass-through
        ],
        sparse_threshold=0.3,  # Controls the sparsity of the output
    )

    for column in df.columns:
      print(f"Number of rows in '{column}':", len(df[column]))

    feature_matrix = feature_transformer.fit_transform(df)
    num_clusters = 24 

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=num_clusters)
    clusters = kmeans.fit_predict(feature_matrix)

    # Add cluster labels to the DataFrame
    df["cluster"] = clusters

    # Display the companies in each cluster
    for cluster in df["cluster"].unique():
        cluster_data = df[df["cluster"] == cluster]
        print(f"Cluster {cluster}:")
        print(cluster_data[["name", "hq_city", "hq_country", "startup_friendly_badge", "startup_partners_count"]])

    # Calculate the silhouette score to evaluate cluster quality
    silhouette_avg = silhouette_score(feature_matrix, df["cluster"])
    print(f"Silhouette Score: {silhouette_avg}")

    # Reduce dimensionality with PCA for 2D visualization
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(feature_matrix)

    # Create and save the PCA plot
    plt.figure(figsize=(10, 7))
    sns.scatterplot(x=pca_result[:, 0], y=pca_result[:, 1], hue=df["cluster"], palette="deep", s=50)
    plt.title("Cluster Visualization with PCA")
    pca_plot_file = os.path.join(base_dir, "pca_visualization.png")
    plt.savefig(pca_plot_file)
    plt.close()  # Close the plot to free up memory

    # t-SNE for a more detailed 2D representation
    tsne = TSNE(n_components=2)
    tsne_result = tsne.fit_transform(feature_matrix)

    # Create and save the t-SNE plot
    plt.figure(figsize=(10, 7))
    sns.scatterplot(x=tsne_result[:, 0], y=tsne_result[:, 1], hue=df["cluster"], palette="deep", s=50)
    plt.title("Cluster Visualization with t-SNE")
    tsne_plot_file = os.path.join(base_dir, "tsne_visualization.png")
    plt.savefig(tsne_plot_file)
    plt.close()  # Close the plot to free up memory

    # Count the number of companies in each cluster
    cluster_counts = df["cluster"].value_counts().sort_index()

    # Create and save the bar plot
    plt.figure(figsize=(10, 7))
    cluster_counts.plot(kind="bar", color="skyblue")
    plt.title("Number of Companies in Each Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Number of Companies")
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    cluster_count_plot_file = os.path.join(base_dir, "cluster_count_plot.png")
    plt.savefig(cluster_count_plot_file)
    plt.close()  # Close the plot to free up memory

    cluster_groups = df.groupby("cluster")
    # Collect data for each cluster
    cluster_data = {}

    for cluster, group in cluster_groups:
        # Extract key characteristics for the cluster
        description = group[["name", "description", "hq_city", "hq_country", "startup_friendly_badge", "startup_partners_count"]]
        
        # Store the data for the cluster
        cluster_data[cluster] = {
            "summary": description.describe(),  # Summarize the cluster's characteristics
            "examples": description.head(3).to_dict(orient="records"),  # Provide some examples from the cluster
        }

       

    # Define the Google Gemini API endpoint and your Google API key
    api_url = config.API_URL
    api_key = config.API_KEY  # Replace with your actual Google API key

    # Define the prompt template to ask for a title and a description
    prompt_template = """
    Please create a title and a description for the following cluster of companies.

    The title should be a single line that summarizes the main theme of the cluster.

    The description should be a detailed explanation of the cluster's characteristics.
    Explore and compare the characteristics of companies within each cluster. 
    Identify common traits, such as industry focus, geographic location, startup friendliness, and partnership count. 

    Cluster Information:
    {cluster_summary}

    Example Companies:
    {example_companies}
    """

    # Dictionary to store titles and descriptions for each cluster
    cluster_descriptions = {}

    # Loop through each cluster to generate titles and descriptions
    for cluster, data in cluster_data.items():
        print("Generating title and description for cluster", cluster)
        # Format the prompt with the cluster data
        prompt = prompt_template.format(
            cluster_summary=data["summary"],  # Cluster summary statistics
            example_companies="\n".join([f"{item['name']}: {item['description']}" for item in data["examples"]]),  # Example companies
        )

        # Construct the JSON payload for the request
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}  # Insert the prompt into the request
                    ]
                }
            ]
        }

        # Send the POST request to the Google Gemini API
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},  # Set the content type to JSON
            params={"key": api_key},  # Include your API key
            json=payload  # Send the payload as JSON
        )

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the generated content from the response
            llm_output = response.json()
            title, description = supplementary_functions.extract_title_and_description(llm_output)

            # Store the generated title and description in the dictionary
            cluster_descriptions[cluster] = {
                "title": title,
                "description": description,
                "example_companies": data["examples"]
            }
        
        else:
            print(f"Failed to generate title and description for cluster {cluster}: {response.status_code}")
        
    
    # Save data in multiple formats
    csv_filename, txt_filename = supplementary_functions.save_cluster_summary_to_csv_and_txt(cluster_descriptions, base_dir)
    pdf_filename = supplementary_functions.save_data_to_pdf(cluster_descriptions, os.path.join(base_dir, "cluster_summary.pdf"))
    html_filename = supplementary_functions.save_data_to_html(cluster_descriptions, os.path.join(base_dir, "cluster_summary.html"))

    return {"message": "Analysis completed!", "files": [csv_filename, txt_filename, pdf_filename, html_filename, pca_plot_file, tsne_plot_file]}
