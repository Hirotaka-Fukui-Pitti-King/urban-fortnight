"""Unit tests for the economic distinction and payment KKT convention."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from contract_branch_diagnostics import is_distinct

def test_economically_identical_triangle_representations():
    assert not is_distinct((1.0,1.5),(1.0,1.5),1.1,1.5)

def test_economically_distinct_contracts():
    assert is_distinct((1.0,1.5),(.98,1.5),1.1,1.5)

def test_near_contract_not_separate_branch():
    assert not is_distinct((1.0,1.5),(1.+1e-8,1.5),1.1,1.5)
