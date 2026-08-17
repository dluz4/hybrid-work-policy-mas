import pytest

from hybrid_work_mas.model import HybridWorkModel


def test_model_creates_expected_population():
    model = HybridWorkModel(
        flexibility=0.709,
        collaboration=0.820,
        n_employees=100,
        seed=42,
    )

    assert len(model.employees) == 100


def test_initial_average_engagement():
    model = HybridWorkModel(
        flexibility=0.709,
        collaboration=0.820,
        initial_engagement=0.21,
        seed=42,
    )

    assert model.average_engagement() == pytest.approx(0.21)


def test_model_advances_one_day():
    model = HybridWorkModel(
        flexibility=0.709,
        collaboration=0.820,
        seed=42,
    )

    model.step()

    assert model.day == 1
    assert len(model.engagement_history) == 2


def test_engagement_remains_bounded():
    model = HybridWorkModel(
        flexibility=1.0,
        collaboration=1.0,
        seed=42,
    )

    model.run(days=180)

    for employee in model.employees:
        assert 0.0 <= employee.engagement <= 1.0


def test_same_seed_produces_same_results():
    model_a = HybridWorkModel(
        flexibility=0.709,
        collaboration=0.820,
        seed=42,
    )

    model_b = HybridWorkModel(
        flexibility=0.709,
        collaboration=0.820,
        seed=42,
    )

    model_a.run(days=30)
    model_b.run(days=30)

    assert model_a.engagement_history == pytest.approx(
        model_b.engagement_history
    )