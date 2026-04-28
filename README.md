# supplier-esg-scoring

Synthetic ESG data generation engine for procurement use cases. The project simulates both:

- True values (latent ground truth)
- Reported values (distorted survey submissions)

using a three-tier generation architecture plus a bias/noise engine.

## What This Project Does

The repository has two execution paths:

1. A generator pipeline that creates synthetic suppliers, surveys, audits, and ESG scores in SQLite.
2. A Streamlit dashboard that reads the generated SQLite database and visualizes the output.

The default database file is `data/esg_simulation.db`.

## Requirements

Install Python 3.11 or newer, then install the dependencies from `requirements.txt`.

## How To Run Locally

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Generate the synthetic ESG dataset

Run the generator before opening the dashboard so the SQLite database exists:

```bash
python -m src.run_pipeline --n-suppliers 100 --alpha 0.15 --beta 1.5
```

This command:

1. Drops and recreates the schema in `data/esg_simulation.db`.
2. Seeds indicator definitions.
3. Generates supplier records.
4. Creates survey responses, audit events, and ESG scores.
5. Commits the final dataset to SQLite.

The current runner accepts these options:

- `--n-suppliers`: number of synthetic suppliers to generate. Default: `100`.
- `--alpha`: reporting bias strength. Default: `0.15`.
- `--beta`: bias maturity curve. Default: `1.5`.

### 4. Start the Streamlit dashboard

```bash
streamlit run app/main.py
```

The dashboard should be available at `http://localhost:8501`.

### 5. Regenerate data from the UI

After the dashboard opens, use the sidebar controls to adjust the simulation parameters and click `Re-Run Simulation` to rebuild the database with new values.

## Docker

If you prefer containers, the repository provides a two-service Compose setup.

```bash
docker compose up --build
```

This starts:

1. `generator`: runs the pipeline and writes `data/esg_simulation.db`.
2. `streamlit`: serves the dashboard on port `8501`.

Open `http://localhost:8501` after the stack finishes starting.

## Recommended Structure

```text
supplier-esg-scoring/
|- app/
|  |- main.py
|- data/
|- notebooks/
|- src/
|  |- db/
|  |  |- base.py
|  |  |- models.py
|  |- generators/
|  |  |- bias_engine.py
|  |  |- tiers.py
|  |- pipeline.py
|  |- run_pipeline.py
|- tests/
|  |- test_pipeline_smoke.py
|- .gitignore
|- docker-compose.yml
|- Dockerfile
|- requirements.txt
|- README.md
```

## Core Mathematical Design

1. Tier 1 Mechanistic:
	- `true_emissions = spend_or_output * industry_emission_factor * grid_intensity * (1 / efficiency)`
2. Tier 2 Behavioral:
	- `lambda = base_rate * size_factor * (1 - esg_maturity)`
	- Violations sampled from Poisson(lambda)
3. Tier 3 Declarative:
	- `P(policy_exists) = sigmoid(esg_maturity + size_effect)`
4. Bias and Noise Engine:
	- `reported_value = true_value * (1 + (bias_direction * alpha_factor * (1 - esg_maturity)) + noise)`
