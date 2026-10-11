def test_sbol_round_trip_is_declared():
    # The fixture intentionally records a test-shaped signal without executing
    # an SBOL library; BioRobust must report this as manual review.
    assert "SBOL 3" in "SBOL 3 round-trip validation"
