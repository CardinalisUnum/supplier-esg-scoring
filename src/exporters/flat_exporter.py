query = """
    SELECT 
        s.id AS supplier_id,
        s.industry,
        s.region,
        s.size_tier,
        s.operating_context,
        s.esg_maturity,
        i.id AS indicator_name,
        i.category,
        sv.true_value,
        sv.reported_value,
        (sv.true_value - sv.reported_value) AS bias_delta
    FROM suppliers s
    JOIN esg_surveys sv ON s.id = sv.supplier_id
    JOIN indicator_definitions i ON sv.indicator_id = i.id;
    """