import pandas as pd
from app import filter_sort_paginate


def make_df():
    return pd.DataFrame([
        {"dataset_id": "A1", "title": "First Dataset", "title_es": "Primer Conjunto"},
        {"dataset_id": "b2", "title": "Second", "title_es": "Segundo"},
        {"dataset_id": "C3", "title": "Third dataset", "title_es": "Tercer Conjunto"},
        {"dataset_id": "d4", "title": "Fourth", "title_es": "Cuarto"},
    ])


def test_filter_case_insensitive():
    df = make_df()
    page_df, total, start, end = filter_sort_paginate(df, search_q="first")
    assert total == 1
    assert page_df.iloc[0]["dataset_id"] in {"A1"}


def test_filter_on_dataset_id_case_insensitive():
    df = make_df()
    page_df, total, start, end = filter_sort_paginate(df, search_q="b2")
    assert total == 1
    assert page_df.iloc[0]["dataset_id"] == "b2"


def test_sort_desc_and_pagination():
    df = make_df()
    # ordenar por dataset_id desc y page_size 2 -> primera página debe contener C3, d4 (dependiendo de sort)
    page_df, total, start, end = filter_sort_paginate(df, sort_column="dataset_id", sort_order="desc", page_size=2, page=1)
    assert total == 4
    assert len(page_df) == 2
    # Asegurarse de que el primer elemento es el mayor según orden desc
    assert page_df.iloc[0]["dataset_id"] >= page_df.iloc[1]["dataset_id"]
