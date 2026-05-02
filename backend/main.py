import os
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from auth import get_current_user, router as auth_router
from database import db
from ml_service import predict_priority
from models import (
    PriorityPredictionRequest,
    PriorityPredictionResponse,
    ProjectCreate,
    ProjectUpdate,
    TaskCreate,
    TaskUpdate,
)

app = FastAPI(title="ML Task Manager API", version="1.0.0")

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc)}


@app.post("/api/projects")
async def create_project(payload: ProjectCreate, current_user=Depends(get_current_user)):
    project_id = str(uuid4())
    doc = {
        "_id": project_id,
        "name": payload.name,
        "description": payload.description or "",
        "owner_id": current_user["_id"],
        "created_at": datetime.now(timezone.utc),
    }
    await db.projects.insert_one(doc)
    return {"id": project_id, **{k: v for k, v in doc.items() if k != "_id"}}


@app.get("/api/projects")
async def list_projects(current_user=Depends(get_current_user)):
    cursor = db.projects.find({"owner_id": current_user["_id"]}).sort("created_at", -1)
    projects = []
    async for project in cursor:
        projects.append(
            {
                "id": project["_id"],
                "name": project["name"],
                "description": project.get("description", ""),
                "owner_id": project["owner_id"],
                "created_at": project["created_at"],
            }
        )
    return projects


@app.put("/api/projects/{project_id}")
async def update_project(project_id: str, payload: ProjectUpdate, current_user=Depends(get_current_user)):
    project = await db.projects.find_one({"_id": project_id, "owner_id": current_user["_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if updates:
        await db.projects.update_one({"_id": project_id}, {"$set": updates})

    updated = await db.projects.find_one({"_id": project_id})
    return {
        "id": updated["_id"],
        "name": updated["name"],
        "description": updated.get("description", ""),
        "owner_id": updated["owner_id"],
        "created_at": updated["created_at"],
    }


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str, current_user=Depends(get_current_user)):
    res = await db.projects.delete_one({"_id": project_id, "owner_id": current_user["_id"]})
    await db.tasks.delete_many({"project_id": project_id, "created_by": current_user["_id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}


@app.post("/api/tasks")
async def create_task(payload: TaskCreate, current_user=Depends(get_current_user)):
    project = await db.projects.find_one({"_id": payload.project_id, "owner_id": current_user["_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task_id = str(uuid4())
    doc = {
        "_id": task_id,
        "project_id": payload.project_id,
        "title": payload.title,
        "description": payload.description,
        "status": payload.status.value,
        "priority": payload.priority.value,
        "created_by": current_user["_id"],
        "created_at": datetime.now(timezone.utc),
    }
    await db.tasks.insert_one(doc)
    return {"id": task_id, **{k: v for k, v in doc.items() if k != "_id"}}


@app.get("/api/tasks")
async def list_tasks(project_id: str, current_user=Depends(get_current_user)):
    cursor = db.tasks.find({"project_id": project_id, "created_by": current_user["_id"]}).sort("created_at", -1)
    tasks = []
    async for task in cursor:
        tasks.append(
            {
                "id": task["_id"],
                "project_id": task["project_id"],
                "title": task["title"],
                "description": task.get("description", ""),
                "status": task["status"],
                "priority": task["priority"],
                "created_by": task["created_by"],
                "created_at": task["created_at"],
            }
        )
    return tasks


@app.put("/api/tasks/{task_id}")
async def update_task(task_id: str, payload: TaskUpdate, current_user=Depends(get_current_user)):
    task = await db.tasks.find_one({"_id": task_id, "created_by": current_user["_id"]})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = {k: (v.value if hasattr(v, "value") else v) for k, v in payload.model_dump().items() if v is not None}
    if updates:
        await db.tasks.update_one({"_id": task_id}, {"$set": updates})

    updated = await db.tasks.find_one({"_id": task_id})
    return {
        "id": updated["_id"],
        "project_id": updated["project_id"],
        "title": updated["title"],
        "description": updated.get("description", ""),
        "status": updated["status"],
        "priority": updated["priority"],
        "created_by": updated["created_by"],
        "created_at": updated["created_at"],
    }


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, current_user=Depends(get_current_user)):
    res = await db.tasks.delete_one({"_id": task_id, "created_by": current_user["_id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}


@app.post("/api/predict-priority", response_model=PriorityPredictionResponse)
async def predict_task_priority(payload: PriorityPredictionRequest, current_user=Depends(get_current_user)):
    prediction = predict_priority(payload.description)
    return {"priority": prediction}
