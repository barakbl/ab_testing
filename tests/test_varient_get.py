from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.database import Base
from ..main import app, get_db
from sqlalchemy.orm import Session
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"
from application.models import Experiment, Variant
from sqlalchemy_utils import database_exists

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    connection = engine.connect()

    # begin a non-ORM transaction
    transaction = connection.begin()

    # bind an individual Session to the connection
    db = Session(bind=connection)
    # db = Session(engine)
    yield db
    db.close()
    transaction.rollback()
    connection.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    if not database_exists:
        create_database(engine.url)

    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()

    transaction = connection.begin()
    db = Session(bind=connection)
    yield db
    db.rollback()
    connection.close()


#
@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as c:
        yield c


def get_header(deviceID="device1"):
    return {"deviceID": deviceID}


def test_missing_experiment(client):
    header = get_header()

    response = client.get("/experiment/not_in_db", headers=header)
    assert response.status_code == 404, response.text


def test_missing_header_device_id(client):
    response = client.get(
        "/experiment/test",
    )
    assert response.status_code == 422, response.text


@pytest.fixture
def two_equal_variants(db, client):
    _experiment = Experiment(name="test_eq")
    db.add(_experiment)
    db.commit()
    experiment_id = _experiment.id

    v = Variant(name="first_50", ratio=50, experiment_id=experiment_id)
    v2 = Variant(name="second_50", ratio=50, experiment_id=experiment_id)
    db.add_all([v, v2])
    db.commit()


def test_two_eq(client, two_equal_variants):
    devices = [f"device_{a}" for a in range(200)]
    cnt_result = {"first_50": 0, "second_50": 0}
    for device in devices:
        header = get_header(device)
        response = client.get(f"/experiment/test_eq", headers=header)
        name = response.json()["variant_name"]
        cnt_result[name] = cnt_result[name] + 1
    assert cnt_result["first_50"] == 100
    assert cnt_result["second_50"] == 100


def test_device_send_multiple_requests(client, two_equal_variants):
    device_1 = "device_1"
    device_2 = "device_2"

    header = get_header(device_1)
    response = client.get(f"/experiment/test_eq", headers=header)
    name_for_device_1 = response.json()["variant_name"]

    header = get_header(device_2)
    response = client.get(f"/experiment/test_eq", headers=header)
    name_for_device_2 = response.json()["variant_name"]

    header = get_header(device_1)
    response = client.get(f"/experiment/test_eq", headers=header)
    name_for_device_1_again = response.json()["variant_name"]
    assert name_for_device_1_again == name_for_device_1
    assert name_for_device_2 != name_for_device_1


@pytest.fixture
def three_variants(db, client):
    _experiment = Experiment(name="test_3")
    db.add(_experiment)
    db.commit()
    experiment_id = _experiment.id

    v = Variant(name="first_30", ratio=30, experiment_id=experiment_id)
    v2 = Variant(name="second_30", ratio=30, experiment_id=experiment_id)
    v3 = Variant(name="third_40", ratio=40, experiment_id=experiment_id)
    db.add_all([v, v2, v3])
    db.commit()


def test_experiment_with_3_variants(client, three_variants):
    devices = [f"device_{a}" for a in range(1000)]
    variants_expected = {"first_30": 300, "second_30": 300, "third_40": 400}

    for device in devices:
        header = get_header(device)
        response = client.get(f"/experiment/test_3", headers=header)
        name = response.json()["variant_name"]
        variants_expected[name] = variants_expected[name] - 1
    assert variants_expected["first_30"] == 0
    assert variants_expected["second_30"] == 0
    assert variants_expected["third_40"] == 0
