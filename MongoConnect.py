from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import uvicorn

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["mandarin"]
collection = db["employee"]

@app.post("/signup")
def create_employee(employee_data: dict):
    result = collection.insert_one(employee_data)
    return {"message": "Employee created successfully", "inserted_id": str(result.inserted_id)}

@app.post("/login")
def login_employee(login_data: dict):
    # Extract email and password from login_data
    email = login_data.get("email")
    password = login_data.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required for login.")

    # Query the database for the email
    employee = collection.find_one({"email": email})

    if not employee:
        # Email not found in the database
        return {"message": "Email not found", "login_successful": False}

    # Check if the password matches
    if employee.get("password") == password:
        # Password matches
        return {"message": "Login successful", "login_successful": True,  "empid": employee.get("eid")}
    else:
        # Password doesn't match
        return {"message": "Incorrect password", "login_successful": False}

@app.post("/update_curriculum/")
def update_curriculum(curriculum: dict):
    # Check if the employee exists
    # print(curriculum.eid)
    eid =  curriculum.get("eid")
    employee = collection.find_one({"eid": eid})
    total = curriculum.get("curriculum")
    field = list(total.keys())[0]
    key = list(total[field].keys())[0]
    targets = list(total[field][key].keys())
    print(targets)
    for target in targets:
        print(target)
        value = total[field][key][target]
        print(value)

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Update the curriculum for the employee
        result = collection.update_one({"eid": eid}, {"$set": {f"curriculum.{field}.{key}.{target}": value}})

    if result.modified_count == 1:
        return {"message": "Curriculum updated successfully"}
    else:
        return {"message": "Curriculum update failed"}
@app.post("/get_curriculum/")
def get_curriculum_by_eid(eid: dict):
    # Check if the employee exists
    employee = collection.find_one({"eid": eid.get("eid")})

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Extract the curriculum object from the employee document
    curriculum = employee.get("curriculum", {})

    return curriculum
from fastapi import HTTPException

@app.post("/get_employees_by_branch/")
def get_employees_by_branch(eid: dict):
    # Check if the employee exists
    employee = collection.find_one({"eid": eid.get("eid")})

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Extract the branch from the employee document
    branch = employee.get("department")
    print(branch)

    # Query the database to find all employees with the same branch
    employees_with_branch = collection.find({"department": branch}, {"_id": 0, "eid": 1})
    # print(list(employees_with_branch))
    # Extract names and eids from the query result
    final = {
        "name" : [],
        "eid" : []
    }
    for emp in list(employees_with_branch):
        id = emp["eid"]
        e = collection.find_one({"eid": id})
        final["name"].append(e.get("name"))
        final["eid"].append(id)

    return final

@app.post("/get_total_achieved_score/")
def get_total_achieved_score(eid: dict):
    # Check if the employee exists
    employee = collection.find_one({"eid": eid.get("eid")})

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Extract the curriculum object from the employee document
    curriculum = employee.get("curriculum", {})
    divisions = list(curriculum.keys())
    total_score = 0
    final = {}
    for division in divisions:
        division_score = 0
        units = list(curriculum[division].keys())
        final[division] = {"division_score" : ""}
        for unit in units:
            unit_score = 0
            keys = list(curriculum[division][unit].keys())
            if "acheived_score" in keys:
                if curriculum[division][unit]["acheived_score"] != '':
                    total_score = total_score + int(curriculum[division][unit]["acheived_score"])
                    division_score = division_score + int(curriculum[division][unit]["acheived_score"])
                    unit_score = unit_score + int(curriculum[division][unit]["acheived_score"])
            final[division][unit] = {"score" : ""}
            final[division][unit]["score"] = unit_score
        final[division]["division_score"] = division_score
    final["total_score"] = total_score

    return final

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)