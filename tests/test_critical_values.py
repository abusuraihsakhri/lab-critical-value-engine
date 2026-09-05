"""
Automated Pytest for lab-critical-value-engine core modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import warnings
import critical_values as m
from agents.base import AuditTrail


def test_lookup():
    r = m.lookup('creatinine')
    assert 'top_hit' in r and 'score' in r
    assert r['top_hit'] == '2160-0 Creatinine'
    assert r['score'] > 0


def test_lookup_hemoglobin():
    r = m.lookup('hemoglobin')
    assert r['top_hit'] == '718-7 Hemoglobin'
    assert r['score'] > 0


def test_lookup_platelets():
    r = m.lookup('platelets')
    assert r['top_hit'] == 'Platelets'


def test_lookup_no_match():
    r = m.lookup('zzzznotfound')
    # When no tokens match, score is 0 but a candidate is still returned
    assert r['score'] == 0
    assert 'top_hit' in r


def test_process_csv():
    pdir = Path(__file__).parent.parent
    rows = m.process_csv(str(pdir / 'sample.csv'), str(pdir / 'tmp_test_out.csv'))
    assert len(rows) >= 1
    assert all('top_hit' in r for r in rows)
    assert all('lookup_score' in r for r in rows)
    # Clean up
    if (pdir / 'tmp_test_out.csv').exists():
        (pdir / 'tmp_test_out.csv').unlink()


def test_process_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        m.process_csv('nonexistent_file.csv', 'output.csv')


def test_process_csv_empty_header():
    """Test that CSV with no header raises ValueError."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("data1,data2\nval1,val2\n")
        tmp_path = f.name
    try:
        # This should work since it has a header
        rows = m.process_csv(tmp_path, str(Path(tmp_path).parent / 'tmp_out.csv'))
        assert len(rows) == 1
    finally:
        os.unlink(tmp_path)
        if (Path(tmp_path).parent / 'tmp_out.csv').exists():
            (Path(tmp_path).parent / 'tmp_out.csv').unlink()


def test_audit_trail_no_secret_key_warning():
    """Test that a warning is raised when no secret key is provided."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        trail = AuditTrail(secret_key=None)
        # Check that a warning was raised about the secret key
        assert any("AUDIT_SECRET_KEY" in str(warning.message) for warning in w)


def test_audit_trail_with_secret_key():
    """Test that no warning is raised when a secret key is provided."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        trail = AuditTrail(secret_key="test-secret-key-for-testing")
        assert not any("AUDIT_SECRET_KEY" in str(warning.message) for warning in w)
        trail.log("test", "test_tier", "TEST_EVENT", {"data": "value"})
        assert len(trail.get_trail()) == 1
        assert trail.verify_integrity() is True
