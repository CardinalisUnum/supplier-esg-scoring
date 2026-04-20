# supplier-esg-scoring

Synthetic ESG data generation engine for procurement use cases. The project simulates both:

- True values (latent ground truth)
- Reported values (distorted survey submissions)

using a three-tier generation architecture plus a bias/noise engine.

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

## Quickstart (Local)

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m src.run_pipeline --n-suppliers 200 --db-path data/esg_simulation.db --seed 42
streamlit run app/main.py
```

## Docker

```bash
docker compose up --build
```

This starts:
- `generator`: creates synthetic records in SQLite
- `streamlit`: dashboard at `http://localhost:8501`