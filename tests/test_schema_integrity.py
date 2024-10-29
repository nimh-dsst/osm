import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from osm.schemas import RtransparentMetrics, Work, schema_helpers

pytestmark = pytest.mark.skip(
    reason="Schema set up changed substantially. Should likely scrap this module. It is worth thinking about type coercion though."
)


@pytest.fixture
def data():
    data_in = {
        # NA is sufficent for nullable Int64 type
        "pmid": [123, 690, pd.NA, 456, pd.NA],
        "year": [2020, 2019, pd.NA, pd.NA, 2018],
        "score": [10.0, pd.NA, 7.5, 6.0, pd.NA],
        # None is necessary for nullable boolean type
        "is_open_code": [True, False, None, None, False],
        "is_open_data": [True, False, None, None, False],
    }
    df = pd.DataFrame(data_in)
    df["pmid"] = df["pmid"].astype("Int64")
    df["year"] = df["year"].astype("Int64")
    df["score"] = df["score"].astype("object")
    df["is_open_code"] = df["is_open_code"].astype("boolean")
    df["is_open_data"] = df["is_open_data"].astype("boolean")
    # filling na values with np.nan coerces the column to float64
    with pd.option_context("future.no_silent_downcasting", True):
        df.score = df.score.fillna(np.nan).infer_objects(copy=False)
    return df


def test_initial_data_integrity(data):
    # Check that data types are as expected
    assert data["pmid"].dtype == "Int64", "pmid should be Int64"
    assert data["year"].dtype == "Int64", "year should be Int64"
    assert data["score"].dtype == "float64", "score should be float64"
    assert data["is_open_code"].dtype == "boolean", "is_open_data should be bool"
    assert data["is_open_data"].dtype == "boolean", "is_open_data should be bool"


def test_handling_missing_values(data):
    invocations = []
    for _, x in data.iterrows():
        invocations.append(
            schema_helpers.get_invocation(x, metrics_schema=RtransparentMetrics)
        )

    # Ensure that missing values are correctly handled
    assert len(invocations) == 5, "All rows should be processed into Work objects"
    assert (
        invocations[2]["metrics"]["pmid"] is None
    ), "pmid should be None for the third object"
    assert (
        invocations[2]["metrics"]["year"] is None
    ), "year should be None for the third object"
    assert (
        invocations[2]["metrics"]["score"] is None
    ), "score should be None for the third object"
    assert (
        invocations[2]["metrics"]["is_open_code"] is None
    ), "is_open_code should be None for the third object"
    assert (
        invocations[2]["metrics"]["is_open_data"] is None
    ), "is_open_data should be None for the third object"


@pytest.mark.xfail(
    reason="Using pyarrow may be the only way to efficiently instantiate models "
)
def test_work_schema_validation():
    """This test checks that the Work schema can cope with awkward types;
    however, ideally the types coming in wouldn't be awkward in the first place.
    I struggled to find a way to use pandas where nullable types that could then
    be fed into the model. I think nullable pyarrow table types may be more
    friendly for this and makes things more performant. It may be that having a
    model that handles these types so carefully may be the way to go but it
    seems like it will have a lot of performance overhead and boilerplate code.
    """
    # Test a case that should raise a validation error
    with pytest.raises(ValidationError):
        work = Work(
            user_defined_id="test",
            pmid="hello",  # This should raise an error
        )
        work.model_dump(mode="json", exclude="id")

    Work(user_defined_id=pd.NA)
    Work(user_defined_id=None)
    Work(doi=pd.NA)
    Work(funder=["a", "b"])
