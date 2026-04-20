from src.pipeline import DataPipeline


def test_pipeline_runs_and_creates_records(tmp_path):
    db_path = tmp_path / "test_esg.db"
    pipeline = DataPipeline(db_path=str(db_path), seed=123)
    pipeline.run(n_suppliers=5)

    assert db_path.exists()
