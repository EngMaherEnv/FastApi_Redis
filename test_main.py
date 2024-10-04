import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "pong"}

def test_post_job():
    csv_file_path = "test_file.csv"
    with open(csv_file_path, "w") as f:
        f.write("Song,Date,Number of Plays\n")
        f.write("Song A,2023-01-01,10\n")
        f.write("Song B,2023-01-01,20\n")

    with open(csv_file_path, "rb") as f:
        response = client.post("/job", files={"csv_file": f})
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert "output_file_path" in response.json()

def test_get_job_status():
    csv_file_path = "test_file.csv"
    with open(csv_file_path, "w") as f:
        f.write("Song,Date,Number of Plays\n")
        f.write("Song A,2023-01-01,10\n")
        f.write("Song B,2023-01-01,20\n")

    with open(csv_file_path, "rb") as f:
        response = client.post("/job", files={"csv_file": f})
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    response = client.get(f"/job_status/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id
    assert "status" in response.json()

def test_get_result():
    csv_file_path = "test_file.csv"
    result_file_path = "test_file.csv_result"

    with open(csv_file_path, "w") as f:
        f.write("Song,Date,Number of Plays\n")
        f.write("Song A,2023-01-01,10\n")
        f.write("Song B,2023-01-01,20\n")

    with open(csv_file_path, "rb") as f:
        response = client.post("/job", files={"csv_file": f})
    assert response.status_code == 200
    output_file_path = response.json()["output_file_path"]

    with open(f"/tmp/{output_file_path}", "w") as f:
        f.write("Song,Date,Total Number of Plays for Date\n")
        f.write("Song A,2023-01-01,10\n")
        f.write("Song B,2023-01-01,20\n")

    response = client.get(f"/result/{output_file_path}")
    assert response.status_code == 200
    assert response.headers["content-disposition"] == f'attachment; filename="{output_file_path}"'
