from ..read_database import ReadDatabaseMicropyro
import pytest

test_data = (
    ('C15H10', 'C', 15),
    ('C15H10', 'H', 10),
    ('C15H10', 'N', 0),
    ('CH', 'C', 1),
    ('CHO2','O', 2),
    ('C', 'H', 0)
)

@pytest.mark.parametrize("formula,atom,expected",test_data)
def test_extract_atoms(formula,atom,expected):
    computed = ReadDatabaseMicropyro.extract_atoms(formula, atom)
    assert computed == expected

