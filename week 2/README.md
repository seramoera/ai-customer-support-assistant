 # Week 2 — AI System Development Checkpoint

Overview

This week, we focused on preparing the dataset, performing exploratory analysis, and implementing baseline models.  
All files and scripts are organized to make it easy to run experiments and reproduce results.

## Project Structure

roject-root/
│
├─ data/
│ ├─ raw/ # Raw datasets
│ └─ processed/ # Train, Validation, Test CSV files
│
├─ notebooks/
│ └─ 01_eda.ipynb # Exploratory Data Analysis
│
├─ src/
│ ├─ data_pipeline.py # Scripts for data cleaning and preprocessing
│ ├─ baselines.py # ML & DL baseline models (Logistic Regression, Decision Tree, Feedforward NN)
│ ├─ cnn_model.py # Text-CNN scaffold for experiments
│ ├─ nlp_scaffold.py # Intent classifier stub
│ └─ rl_stub.py # Reinforcement learning agent stub
│
└─ docs/
├─ model_card.md # Model overview, metrics, limitations
└─ ethics_statement.md # Ethics considerations


---

## Deliverables Completed

### 1. Data Preparation
- Created training, validation, and test splits.
- Cleaned data and verified using Pandas (`info()`, `isnull().sum()`, sample rows).

### 2. Exploratory Data Analysis (EDA)
- Visualized **class distribution**.
- Checked for missing values and summarized dataset info.
- Reviewed **sample messages** to understand the data.
- Investigated basic feature relationships (e.g., `inbound` column).

### 3. Baseline Models
- Implemented **Logistic Regression** and **Decision Tree** as simple ML baselines.
- Implemented **Feedforward Neural Network** as a DL baseline.
- Training and evaluation metrics printed for each model.

### 4. CNN Experiment
- Built a **Text-CNN scaffold** for text classification.
- Prepared for training with initial hyperparameters.
- Validation metrics can be logged.

### 5. NLP Component
- Created an **intent classifier stub** (text → predicted intent).
- Ensures compatibility with RL agent environment.

### 6. RL Agent Stub
- Defined the environment: states = messages, actions = response choices.
- Defined a simple reward function.
- Ran sample episodes to generate early learning curves.

### 7. Ethics & Model Card
- `model_card.md` and `ethics_statement.md` document dataset, metrics, risks, and ethical considerations.
- Covered privacy, bias, and transparency.

---

## Next Steps
- Fine-tune CNN with optimized hyperparameters.
- Expand NLP component with embeddings for better predictions.
- Integrate RL agent with NLP predictions.
- Continue drafting final Model Card and Ethics Statement.

---

## How to Run
1. Make sure **Python 3.11** is installed with required packages:
2. Run baseline models:
3. Open the EDA notebook:
4. Explore CNN experiments, NLP scaffold, and RL stub as needed.

