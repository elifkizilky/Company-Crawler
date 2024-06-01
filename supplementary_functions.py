import json 
import os
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, StyleSheet1
from reportlab.lib.units import inch
from reportlab.lib import colors


def ensure_writable(directory):
    """
    Checks if a directory is writable. If not, it sets appropriate permissions.
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist.")

    # Check if the directory is writable
    if not os.access(directory, os.W_OK):
        print(f"Directory {directory} is not writable. Setting permissions...")

        # Retrieve current mode
        mode = os.stat(directory).st_mode

        # Add user write permission
        new_mode = mode | stat.S_IWUSR  # Add write permission for the user

        try:
            os.chmod(directory, new_mode)
            print(f"Write permission set for directory {directory}")
        except PermissionError:
            raise PermissionError(f"Unable to set write permissions for {directory}")


def save_cluster_summary_to_csv_and_txt(cluster_descriptions, base_dir):
    print("save_cluster_summary_to_csv_and_txt started...")
    rows = []

    for cluster, content in cluster_descriptions.items():
        company_list = [f"{item['name']} ({item['description']})" for item in content["example_companies"]]
        company_string = ", ".join(company_list)

        row = {
            "Index": cluster,
            "Title": content["title"],
            "Description": content["description"],
            "Companies": company_string,
        }

        rows.append(row)

    # Convert to a DataFrame for CSV saving
    df = pd.DataFrame(rows)
    csv_filename = os.path.join(base_dir, "cluster_summary.csv")
    df.to_csv(csv_filename, index=False)

    # Save to a styled text file
    txt_filename = os.path.join(base_dir, "cluster_summary.txt")
    with open(txt_filename, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(f"Cluster {row['Index']}:\n")
            f.write(f"Title: {row['Title']}\n")
            f.write(f"Description: {row['Description']}\n")
            f.write(f"Companies: {row['Companies']}\n")
            f.write("\n")

    print(f"Cluster summary saved to {csv_filename} and {txt_filename}")
    return csv_filename, txt_filename

def save_data_to_pdf(cluster_descriptions, filename="cluster_summary.pdf"):
    print("save_data_to_pdf started...")
    doc = SimpleDocTemplate(filename, pagesize=letter)

    styles = getSampleStyleSheet()

    bold_style = ParagraphStyle(
        "BoldStyle",
        parent=styles["Heading3"],  # Based on Heading3 for consistency
        fontSize=12,
        fontName="Helvetica-Bold",
    )

    italic_style = ParagraphStyle(
        "ItalicStyle",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Oblique",
    )

    normal_style = styles["Normal"]

    elements = []

    for cluster, content in cluster_descriptions.items():
        company_list = [f"{item['name']} ({item['description']})" for item in content["example_companies"]]
        company_string = ', '.join(company_list)

        elements.append(Paragraph(f"Cluster {cluster}", bold_style))
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph("Title:", bold_style))
        elements.append(Paragraph(content["title"], normal_style))

        elements.append(Paragraph("Description:", bold_style))
        elements.append(Paragraph(content["description"], normal_style))

        elements.append(Paragraph("Companies:", bold_style))
        elements.append(Paragraph(company_string, italic_style))

        elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)
    print(f"Cluster summary saved to {filename}")

    return filename

def save_data_to_html(cluster_descriptions, filename="./cluster_summary.html"):
    print("save_data_to_html started...")
    rows = []

    for cluster, content in cluster_descriptions.items():
        company_list = [f"{item['name']} ({item['description']})" for item in content["example_companies"]]
        company_string = ', '.join(company_list)

        row = f"""
        <tr>
            <td>{cluster}</td>
            <td>{content["title"]}</td>
            <td>{content["description"]}</td>
            <td>{company_string}</td>
        </tr>
        """
        rows.append(row)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cluster Summary</title>
        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <h1>Cluster Summary</h1>
        <table>
            <tr>
                <th>Index</th>
                <th>Title</th>
                <th>Description</th>
                <th>Companies</th>
            </tr>
            {''.join(rows)}
        </table>
    </body>
    </html>
    """

    # Write the content to an HTML file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Cluster summary saved to {filename}")
    return filename

def extract_title_and_description(llm_output):
    try:
        # Get the generated content
        content = llm_output["candidates"][0]["content"]["parts"][0]["text"]
        
        # Find the position of the first newline to split title and description
        split_position = content.find("\n\n")  # Double newline as the separator
        
        # Extract the title and description
        if split_position != -1:
            title = content[:split_position].replace("**Title:**", "").strip()  # Remove the title indicator
            description = content[split_position + 2:].replace("**Description:**", "").strip()  # Remove the description indicator
        else:
            title = "Unknown Title"  # Default if no title found
            description = content  # Use the whole content as the description if no split

        return title, description
    except (KeyError, IndexError):
        return "Unknown Title", "No Description"

