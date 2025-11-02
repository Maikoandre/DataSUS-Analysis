# DataSUS Data Analysis Project (SIH and SINAN)

This project focuses on the Exploratory Data Analysis (EDA) of public health system data in Brazil (DataSUS), specifically covering the **Hospital Information System (SIH)** and the **Notifiable Diseases Information System (SINAN)**, with an emphasis on Dengue cases.

---

## 📝 Index

* [About the Project](#-about-the-project)
* [File Structure](#-file-structure)
* [Technologies Used](#-technologies-used)
* [Getting Started](#-getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
* [How to Use](#-how-to-use)

---

## 📖 About the Project

The goal of this repository is to process, analyze, and extract insights from large volumes of DataSUS records. The main hospital analysis is contained in the `sia.ipynb` notebook and is complemented by a Streamlit Dashboard (`app.py`) focused on Hospital Admissions (SIH) data for the state of Bahia.

The project also includes sample datasets, such as Dengue notification data from SINAN for 2024 and a Brazilian municipalities file, enabling analysis and data merging.

## 🗂️ File Structure

* **`sia.ipynb`**: Primary Jupyter Notebook containing the code for the exploratory data analysis of the Ambulatory Information System (SIA) or Hospital Information System (SIH) data.
* **`app.py`**: Streamlit application for visualizing key metrics and charts from the SIH data for Bahia.
* **`datasets/`**: Directory containing the data used in the analyses.
    * **`RD202401.parquet`**: Likely a "Reduced Ambulatory Production" (SIA) file for January 2024, in Parquet format.
    * **`sinan_dengue_sample_2024.parquet`**: A sample file with Dengue notification data from SINAN for 2024.
    * **`municipios.csv`**: CSV file containing a list of Brazilian municipalities, likely including IBGE codes, names, and UF (State) information.

## 🛠️ Technologies Used

* **Python 3.11**
* **Jupyter Notebook / Jupyter Lab**
* **Pandas**
* **PyArrow**
* **Seaborn**
* **Streamlit** (for the Dashboard)

## 🏁 Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

You will need to have Python 3 and a package manager (like `pip`) installed on your machine.

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/Maikoandre/DataSUS-Analysis.git](https://github.com/Maikoandre/DataSUS-Analysis.git)
    ```
2.  Navigate to the project directory:
    ```bash
    cd DataSUS-Analysis
    ```
3.  Install the required libraries. (It is recommended to create a virtual environment).
    ```bash
    # Create a virtual environment (optional, but recommended)
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    
    # Install the libraries
    pip install jupyterlab pandas pyarrow seaborn streamlit matplotlib
    ```

## 🏃 How to Use

### For Notebook Analysis:

1.  Start Jupyter Lab (or Notebook) from your terminal:
    ```bash
    jupyter lab
    ```
2.  In your browser, open the `sia.ipynb` file.
3.  Execute the notebook cells to view the data analysis.

### For Streamlit Dashboard:

1.  Run the Streamlit application from your terminal:
    ```bash
    streamlit run app.py
    ```
2.  The dashboard will open in your default browser, displaying the analysis of SIH data for Bahia.

---
