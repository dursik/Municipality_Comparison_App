# Municipal Financial Monitor

This project is an analytical and visualization tool designed to assess the financial health of municipalities in the Czech Republic. It processes municipal accounting data and converts it into understandable financial indicators and visualizations.

## What it does
The application loads raw data from municipal financial statements (balance sheets and profit and loss statements), cleans it, and calculates 12 key financial indicators (e.g., financial independence, current liquidity, debt burden). It then compares the results for a specific municipality against the distribution of other municipalities within the same size category and calculates an overall "Final Score" of the municipality's health. Users can view the data through a clear and intuitive graphical user interface (GUI).

## Assumptions
*Input data from the State Treasury system (FIN and ROZV statements) are in a standardized CSV format.
*To run the source code, the user must have Python 3.10+ installed, along with the libraries listed in the requirements.txt file.
*For regular users, a compiled .exe version is available in the Releases section, which requires no installation.

## Limitations
*The GUI application does not work with live network data. It loads a pre-calculated dataset (points.pkl). To update the data, you must download new CSV files and manually run the respective cleaning scripts again.
*Comparisons are always made strictly within a single municipal size category (based on population) to ensure a fair assessment.

## Potential Upgrades
* **Report Export:** The ability to generate and download a PDF analysis for a selected municipality directly from the GUI.
* **Interactive Charts:** Transitioning from Matplotlib to libraries like Plotly for more dynamic data visualization (e.g., displaying values on hover).

---
Note: The Graphical User Interface (GUI) architecture and this README file were created with the assistance of Artificial Intelligence (AI).
---