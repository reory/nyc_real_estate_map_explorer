import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from src.engine import analyse_properties


def test_empty_input_returns_empty_df():
    """Verify empty input returns an empty DataFrame."""

    df = analyse_properties([])
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_basic_dataframe_pass_through():
    """Verify property data is converted to a DataFrame."""

    props = [{"price": 500000, "bed": 2}]
    df = analyse_properties(props)
    assert len(df) == 1
    assert df.iloc[0]["price"] == 500000


def test_outlier_removal():
    """Verify price outliers are handled during analysis."""

    props = [
        {"price": 500000},
        {"price": 505000},
        {"price": 495000},
        {"price": 50000000},
    ]
    df = analyse_properties(props)

    assert not df.empty
    assert "price" in df.columns


def test_outlier_removed_in_large_dataset():
    """Verify extreme price outliers are removed from large datasets."""

    props = [{"price": 500000 + i * 1000} for i in range(100)]
    props.append({"price": 50000000})  # extreme outlier

    df = analyse_properties(props)

    assert len(df) == 100
    assert 50000000 not in df["price"].values


@settings(deadline=None)
@given(
    st.lists(
        st.fixed_dictionaries(
            {
                "price": st.one_of(
                    st.floats(allow_nan=True, allow_infinity=True),
                    st.integers(min_value=-(10**12), max_value=10**12),
                ),
                "bed": st.integers(min_value=0, max_value=10),
                "bath": st.floats(min_value=0, max_value=10),
            }
        ),
        max_size=50,
    )
)
def test_analyse_properties_property_based(props):
    """Verify analysis handles diverse property inputs safely."""

    df = analyse_properties(props)
    assert isinstance(df, pd.DataFrame)
    if "price" in df.columns:
        assert df["price"].isna().sum() == 0