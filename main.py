from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from redis import Redis
from rq import Queue
from rq.job import Job
from csv_processor import process_csv
import os

app = FastAPI()
redis_conn = Redis(host="redis", port=6379)  # Connect to Redis Docker service
task_queue = Queue("task_queue", connection=redis_conn)

@app.get("/")
def index():
    return {
        "success": True,
        "message": "pong"
    }

@app.post("/job")
def post_job(csv_file: UploadFile = File(...)):
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    input_file_path = f"/tmp/{csv_file.filename}"
    original_filename = csv_file.filename
    new_filename = original_filename.replace('.csv', '_result.csv')
    output_file_path = f"/tmp/{new_filename}"

    # Save the uploaded CSV file
    with open(input_file_path, "wb") as file_object:
        file_object.write(csv_file.file.read())

    # Enqueue the job to process the CSV file
    job_instance = task_queue.enqueue(process_csv, input_file_path, output_file_path)

    return {
        "success": True,
        "job_id": job_instance.id,
        "output_file_name": os.path.basename(output_file_path)  
    }

@app.get("/result/{file_name}")
async def get_result(file_name: str):
    file_path = f"/tmp/{file_name}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)

@app.get("/job_status/{job_id}")
def get_job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return {
            "success": True,
            "job_id": job_id,
            "status": job.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")
