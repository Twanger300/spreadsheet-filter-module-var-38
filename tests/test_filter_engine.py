from spreadsheet_filter import FilterCondition, FilterEngine

ROWS = [
    {"id": "1", "region": "Москва", "status": "Оплачено", "amount": "75000"},
    {"id": "2", "region": "Санкт-Петербург", "status": "Новый", "amount": "42000"},
    {"id": "3", "region": "Москва", "status": "Оплачено", "amount": "150000"},
    {"id": "4", "region": "Казань", "status": "Отменено", "amount": "9000"},
]


def test_filter_by_equals_and_gte():
    engine = FilterEngine()
    conditions = [
        FilterCondition("region", "equals", "Москва"),
        FilterCondition("amount", "gte", "50000"),
    ]

    result = engine.apply(ROWS, conditions)

    assert [row["id"] for row in result] == ["1", "3"]


def test_filter_by_contains():
    engine = FilterEngine()

    result = engine.apply(ROWS, [FilterCondition("status", "contains", "плач")])

    assert len(result) == 2


def test_filter_between():
    engine = FilterEngine()

    result = engine.apply(ROWS, [FilterCondition("amount", "between", "10000..80000")])

    assert [row["id"] for row in result] == ["1", "2"]


def test_filter_or_logic():
    engine = FilterEngine()
    conditions = [
        FilterCondition("region", "equals", "Казань"),
        FilterCondition("amount", "gt", "100000"),
    ]

    result = engine.apply(ROWS, conditions, logic="OR")

    assert [row["id"] for row in result] == ["3", "4"]


def test_sort_descending_by_amount():
    engine = FilterEngine()

    result = engine.sort(ROWS, "amount", descending=True)

    assert [row["id"] for row in result] == ["3", "1", "2", "4"]
