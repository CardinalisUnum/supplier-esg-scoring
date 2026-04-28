query = """
    SELECT 
        s.id AS supplier_id,
        s.industry,
        s.region,
        s.size,
        s.esg_maturity,
        t.true_emissions, 
        r.reported_emissions,
        (t.true_emissions - r.reported_emissions) AS emissions_bias_gap
    FROM suppliers s
    JOIN true_esg_metrics t ON s.id = t.supplier_id
    JOIN reported_esg_metrics r ON s.id = r.supplier_id;
    """