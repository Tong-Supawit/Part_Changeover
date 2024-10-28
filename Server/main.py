from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
from io import BytesIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data = {
    "Part No": ["TG11111", "TG22222", "TG33333", "TG44444", "TG55555", "TG66666"],
    "TG11111": [None, 12, 22, 2, 33.43, 22.12],
    "TG22222": [34, None, 12, 3.45, 34, 66.76],
    "TG33333": [2, 8, None, 2, 34, 54.3],
    "TG44444": [3, 8, 34.2, None, 33, 23],
    "TG55555": [4, 9, 7, None, None, 44],
    "TG66666": [5, 7, 8, 32.3, 34, None]
}

def get_dataframe():
    return pd.DataFrame(data)

@app.get("/matrix-data")
def get_matrix_data():
    try:
        parts = data["Part No"]
        matrix = [[data[part][i] if part in data else None for part in parts] for i in range(len(parts))]
        return {"parts": parts, "matrix": matrix}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating matrix data: {e}")

@app.get("/download")
def download_excel():
    df = get_dataframe()
    file_path = "matrix_data.xlsx"
    df.to_excel(file_path, index=False)
    return FileResponse(path=file_path, filename="matrix_data.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    try:
        content = await file.read()
        excel_data = pd.read_excel(BytesIO(content))
        
        if "Part No" not in excel_data.columns:
            raise HTTPException(status_code=400, detail="Uploaded file is missing 'Part No' column")

        global data
        data = excel_data.to_dict(orient="list")
        return {"message": "Data updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

class Part(BaseModel):
    part_no: str

@app.post("/add-part")
def add_part(part: Part):
    global data
    part_no = part.part_no
    
    if part_no in data["Part No"]:
        raise HTTPException(status_code=400, detail="Part already exists")
    
    data["Part No"].append(part_no)
    for key in data.keys():
        if key != "Part No":
            data[key].append(None)
    data[part_no] = [None] * len(data["Part No"])

    return {"message": f"Part {part_no} added successfully", "updated_data": data}

@app.delete("/delete-part")
def delete_part(part_no: str = Query(..., description="The part number to delete")):
    global data
    if part_no not in data["Part No"]:
        raise HTTPException(status_code=404, detail="Part not found")

    part_index = data["Part No"].index(part_no)
    
    data["Part No"].remove(part_no)

    for key in data.keys():
        if key != "Part No" and len(data[key]) > part_index:
            data[key].pop(part_index)
    
    if part_no in data:
        del data[part_no]

    return {"message": f"Part {part_no} deleted successfully", "updated_data": data}

class UpdateTimeRequest(BaseModel):
    part_no: str
    target_part_no: str
    changeover_time: float

@app.put("/update-time")
def update_time(request: UpdateTimeRequest):
    global data
    if request.part_no not in data["Part No"] or request.target_part_no not in data:
        raise HTTPException(status_code=404, detail="Part or target part not found")

    part_index = data["Part No"].index(request.part_no)

    data[request.target_part_no][part_index] = request.changeover_time

    return {"message": f"Time updated successfully for {request.part_no} -> {request.target_part_no}", "updated_data": data}
