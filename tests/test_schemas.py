from osm.schemas.metrics_schemas import RtransparentMetrics


def test_rtransparent_metrics():
    # Test creating a RtransparentMetrics instance
    metrics = RtransparentMetrics(is_open_code=True, is_open_data=False)
    # assert isinstance(metrics.id, ObjectId)
    assert metrics.is_open_code is True
    assert metrics.is_open_data is False

    # Test serialization
    metrics.model_dump(mode="json")
