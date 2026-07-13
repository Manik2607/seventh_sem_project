import sys
import os
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

client = TestClient(app)

def cleanup_db():
    print("Pre-test database cleanup...")
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.department import Department
    from app.models.complaint import Complaint
    from app.models.assignment import Assignment
    from app.models.feedback import Feedback
    from app.models.notification import Notification
    from app.models.status_history import StatusHistory
    
    db = SessionLocal()
    try:
        test_emails = [
            "test_citizen@civicplatform.com",
            "test_official@civicplatform.com",
            "test_staff@civicplatform.com",
            "test_engineer@civicplatform.com",
            "invalid_staff@civicplatform.com"
        ]
        # Clean up related tables
        test_users = db.query(User).filter(User.email.in_(test_emails)).all()
        user_ids = [u.user_id for u in test_users]
        if user_ids:
            db.query(Feedback).filter(Feedback.citizen_id.in_(user_ids)).delete(synchronize_session=False)
            db.query(Notification).filter(Notification.user_id.in_(user_ids)).delete(synchronize_session=False)
            db.query(Assignment).filter(
                (Assignment.official_id.in_(user_ids)) | (Assignment.engineer_id.in_(user_ids))
            ).delete(synchronize_session=False)
            db.query(StatusHistory).filter(StatusHistory.updated_by.in_(user_ids)).delete(synchronize_session=False)
            
            # Find complaints to clean up
            complaints = db.query(Complaint).filter(Complaint.citizen_id.in_(user_ids)).all()
            comp_ids = [c.complaint_id for c in complaints]
            if comp_ids:
                db.query(Assignment).filter(Assignment.complaint_id.in_(comp_ids)).delete(synchronize_session=False)
                db.query(StatusHistory).filter(StatusHistory.complaint_id.in_(comp_ids)).delete(synchronize_session=False)
                db.query(Feedback).filter(Feedback.complaint_id.in_(comp_ids)).delete(synchronize_session=False)
                db.query(Notification).filter(Notification.complaint_id.in_(comp_ids)).delete(synchronize_session=False)
                db.query(Complaint).filter(Complaint.citizen_id.in_(user_ids)).delete(synchronize_session=False)

        # Delete test users
        db.query(User).filter(User.email.in_(test_emails)).delete(synchronize_session=False)
        
        # Delete test departments
        db.query(Department).filter(Department.department_name.in_([
            "Test Municipal Sanitation Dept",
            "Test Sanitation Dept (Updated)"
        ])).delete(synchronize_session=False)
        
        db.commit()
        print("-> Cleaned up existing test records.")
    except Exception as e:
        db.rollback()
        print(f"-> Warning during cleanup: {e}")
    finally:
        db.close()

def test_flow():
    cleanup_db()
    print("Starting integration test suite...")
    
    # -----------------------------
    # 1. Test Departments API
    # -----------------------------
    print("\n1. Testing Department creation...")
    dept_payload = {
        "department_name": "Test Municipal Sanitation Dept",
        "description": "Handles garbage collection and street cleaning in test areas."
    }
    
    response = client.post("/departments", json=dept_payload)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    dept_res = response.json()
    assert dept_res["success"] is True
    assert dept_res["data"]["department_name"] == dept_payload["department_name"]
    dept_id = dept_res["data"]["department_id"]
    print(f"-> Successfully created department with ID: {dept_id}")
    
    # Test Duplicate Department Name (Expect 400)
    print("-> Testing duplicate department name...")
    dup_dept_response = client.post("/departments", json=dept_payload)
    assert dup_dept_response.status_code == 400
    assert dup_dept_response.json()["success"] is False
    print("-> Duplicate department name handled correctly.")
    
    # Test GET Departments List
    print("-> Testing department list...")
    list_response = client.get("/departments")
    assert list_response.status_code == 200
    assert list_response.json()["success"] is True
    assert len(list_response.json()["data"]) >= 1
    
    # Test GET Department Detail
    print("-> Testing department details...")
    detail_response = client.get(f"/departments/{dept_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["success"] is True
    assert detail_response.json()["data"]["department_name"] == dept_payload["department_name"]
    
    # Test PUT Department Update
    print("-> Testing department update...")
    update_payload = {
        "department_name": "Test Sanitation Dept (Updated)",
        "description": "Updated description for test department."
    }
    update_response = client.put(f"/departments/{dept_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["success"] is True
    assert update_response.json()["data"]["department_name"] == update_payload["department_name"]
    
    # -----------------------------
    # 2. Test Users API
    # -----------------------------
    print("\n2. Testing User registration...")
    user_payload = {
        "email": "test_citizen@civicplatform.com",
        "password": "supersecurepassword123",
        "name": "Test Citizen User",
        "phone": "+1234567890",
        "role": "Citizen",
        "department_id": None
    }
    
    # Register Citizen User
    reg_response = client.post("/users/register", json=user_payload)
    assert reg_response.status_code == 201, f"Expected 201, got {reg_response.status_code}. Response: {response.text}"
    user_res = reg_response.json()
    assert user_res["success"] is True
    assert user_res["data"]["email"] == user_payload["email"]
    user_id = user_res["data"]["user_id"]
    print(f"-> Successfully registered citizen user with ID: {user_id}")
    
    # Test Register Duplicate Email (Expect 400)
    print("-> Testing duplicate email registration...")
    dup_user_response = client.post("/users/register", json=user_payload)
    assert dup_user_response.status_code == 400
    assert dup_user_response.json()["success"] is False
    print("-> Duplicate email registration handled correctly.")
    
    # Register Staff User (Official) with Department
    print("-> Registering official staff user with department...")
    staff_payload = {
        "email": "test_official@civicplatform.com",
        "password": "officialpassword456",
        "name": "Test Official Officer",
        "phone": "+0987654321",
        "role": "Official",
        "department_id": dept_id
    }
    staff_reg_response = client.post("/users/register", json=staff_payload)
    assert staff_reg_response.status_code == 201
    staff_res = staff_reg_response.json()
    staff_id = staff_res["data"]["user_id"]
    assert staff_res["data"]["department_id"] == dept_id
    print(f"-> Successfully registered official staff user with ID: {staff_id}")
    
    # Register with non-existing department (Expect 400)
    print("-> Testing registration with non-existing department ID...")
    invalid_staff_payload = {
        "email": "invalid_staff@civicplatform.com",
        "password": "staffpassword456",
        "name": "Invalid Staff Officer",
        "role": "Official",
        "department_id": 999999
    }
    invalid_staff_response = client.post("/users/register", json=invalid_staff_payload)
    assert invalid_staff_response.status_code == 400
    assert invalid_staff_response.json()["success"] is False
    print("-> Non-existing department ID registration handled correctly.")

    # Test User Login (Valid credentials)
    print("\n3. Testing User Login...")
    login_payload = {
        "email": "test_citizen@civicplatform.com",
        "password": "supersecurepassword123"
    }
    login_response = client.post("/users/login", json=login_payload)
    assert login_response.status_code == 200
    assert login_response.json()["success"] is True
    assert login_response.json()["data"]["email"] == user_payload["email"]
    print("-> Successful login verification passed.")
    
    # Test User Login (Invalid credentials)
    print("-> Testing login with invalid password...")
    invalid_login_payload = {
        "email": "test_citizen@civicplatform.com",
        "password": "wrongpassword"
    }
    invalid_login_response = client.post("/users/login", json=invalid_login_payload)
    assert invalid_login_response.status_code == 401
    assert invalid_login_response.json()["success"] is False
    print("-> Invalid login handled correctly.")
    
    # Test GET Users List
    print("\n4. Testing User operations...")
    users_list_response = client.get("/users")
    assert users_list_response.status_code == 200
    assert len(users_list_response.json()["data"]) >= 2
    
    # Test GET User Detail
    user_detail_response = client.get(f"/users/{user_id}")
    assert user_detail_response.status_code == 200
    assert user_detail_response.json()["success"] is True
    assert user_detail_response.json()["data"]["name"] == user_payload["name"]
    
    # Test PUT User Update
    user_update_payload = {
        "name": "Test Citizen User (Updated)",
        "role": "Admin"  # promote to admin
    }
    user_update_response = client.put(f"/users/{user_id}", json=user_update_payload)
    assert user_update_response.status_code == 200
    assert user_update_response.json()["data"]["name"] == user_update_payload["name"]
    assert user_update_response.json()["data"]["role"] == "Admin"
    print("-> User updates verified successfully.")
    
    # -----------------------------
    # 3. Test Complaints API
    # -----------------------------
    print("\n3. Testing Complaints API...")
    complaint_payload = {
        "citizen_id": user_id,
        "title": "Water leakage in main street",
        "description": "A pipe is burst and water is leaking everywhere.",
        "category": "Water supply",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "address": "123 Main St, Bengaluru",
        "image_url": "http://example.com/leakage.jpg",
        "image_type": "image/jpeg",
        "priority": "Medium",
        "department_id": dept_id
    }
    
    # Test Create Complaint
    print("-> Testing create complaint...")
    comp_response = client.post("/complaints", json=complaint_payload)
    assert comp_response.status_code == 201, f"Response: {comp_response.text}"
    comp_res = comp_response.json()
    assert comp_res["success"] is True
    assert comp_res["data"]["title"] == complaint_payload["title"]
    assert comp_res["data"]["status"] == "Submitted"
    assert len(comp_res["data"]["images"]) == 1
    assert comp_res["data"]["images"][0]["image_url"] == complaint_payload["image_url"]
    assert len(comp_res["data"]["status_histories"]) == 1
    assert comp_res["data"]["status_histories"][0]["status"] == "Submitted"
    complaint_id = comp_res["data"]["complaint_id"]
    print(f"-> Successfully created complaint with ID: {complaint_id}")
    
    # Test Create Complaint with non-existing user (Expect 400)
    print("-> Testing create complaint with invalid user ID...")
    invalid_comp_payload = complaint_payload.copy()
    invalid_comp_payload["citizen_id"] = 999999
    invalid_user_response = client.post("/complaints", json=invalid_comp_payload)
    assert invalid_user_response.status_code == 400
    assert invalid_user_response.json()["success"] is False
    
    # Test Create Complaint with non-existing department (Expect 400)
    print("-> Testing create complaint with invalid department ID...")
    invalid_comp_payload = complaint_payload.copy()
    invalid_comp_payload["department_id"] = 999999
    invalid_dept_response = client.post("/complaints", json=invalid_comp_payload)
    assert invalid_dept_response.status_code == 400
    assert invalid_dept_response.json()["success"] is False
    
    # Test GET Complaints List
    print("-> Testing get complaints list...")
    list_comp_res = client.get("/complaints")
    assert list_comp_res.status_code == 200
    assert list_comp_res.json()["success"] is True
    assert len(list_comp_res.json()["data"]) >= 1
    
    # Test GET Complaint Detail
    print("-> Testing get complaint detail...")
    detail_comp_res = client.get(f"/complaints/{complaint_id}")
    assert detail_comp_res.status_code == 200
    assert detail_comp_res.json()["success"] is True
    assert detail_comp_res.json()["data"]["title"] == complaint_payload["title"]
    
    # Test GET Complaints by Citizen ID
    print("-> Testing get complaints by citizen ID...")
    citizen_comp_res = client.get(f"/complaints/citizen/{user_id}")
    assert citizen_comp_res.status_code == 200
    assert citizen_comp_res.json()["success"] is True
    assert len(citizen_comp_res.json()["data"]) >= 1
    
    # Test GET Complaints by Citizen ID (invalid user, expect 404)
    print("-> Testing get complaints by invalid citizen ID...")
    invalid_citizen_res = client.get("/complaints/citizen/999999")
    assert invalid_citizen_res.status_code == 404
    
    # Test GET Complaints by Status
    print("-> Testing get complaints by status...")
    status_comp_res = client.get("/complaints/status/Submitted")
    assert status_comp_res.status_code == 200
    assert status_comp_res.json()["success"] is True
    assert len(status_comp_res.json()["data"]) >= 1
    
    # Test GET Complaints by Status (invalid status enum, expect 400)
    print("-> Testing get complaints by invalid status...")
    invalid_status_res = client.get("/complaints/status/InvalidStatus")
    assert invalid_status_res.status_code == 400
    assert invalid_status_res.json()["success"] is False
    
    # Test GET Complaints by Department ID
    print("-> Testing get complaints by department ID...")
    dept_comp_res = client.get(f"/complaints/department/{dept_id}")
    assert dept_comp_res.status_code == 200
    assert dept_comp_res.json()["success"] is True
    assert len(dept_comp_res.json()["data"]) >= 1
    
    # Test GET Complaints by Department ID (invalid department, expect 404)
    print("-> Testing get complaints by invalid department ID...")
    invalid_dept_res = client.get("/complaints/department/999999")
    assert invalid_dept_res.status_code == 404
    
    # Test Update Complaint Status
    print("-> Testing update complaint status...")
    update_payload = {
        "status": "In Progress",
        "updated_by": staff_id,
        "remarks": "Assigned to staff officer."
    }
    update_comp_res = client.put(f"/complaints/{complaint_id}", json=update_payload)
    assert update_comp_res.status_code == 200
    assert update_comp_res.json()["success"] is True
    assert update_comp_res.json()["data"]["status"] == "In Progress"
    assert len(update_comp_res.json()["data"]["status_histories"]) == 2
    assert update_comp_res.json()["data"]["status_histories"][1]["status"] == "In Progress"
    assert update_comp_res.json()["data"]["status_histories"][1]["remarks"] == "Assigned to staff officer."
    assert update_comp_res.json()["data"]["status_histories"][1]["updated_by"] == staff_id
    
    # Test Update Complaint with non-existing updater (Expect 400)
    print("-> Testing update complaint status with invalid updater ID...")
    invalid_update_payload = {
        "status": "Resolved",
        "updated_by": 999999
    }
    invalid_updater_res = client.put(f"/complaints/{complaint_id}", json=invalid_update_payload)
    assert invalid_updater_res.status_code == 400
    # ----------------------------------------------------
    # 3.5. Testing Remaining Modules (Assignment, Status, Notification, Feedback)
    # ----------------------------------------------------
    print("\n3.5. Testing Remaining Modules...")

    # Register Engineer User
    print("-> Registering test engineer user...")
    engineer_payload = {
        "email": "test_engineer@civicplatform.com",
        "password": "engineerpassword789",
        "name": "Test Engineer Staff",
        "phone": "+1122334455",
        "role": "Engineer",
        "department_id": dept_id
    }
    eng_reg_response = client.post("/users/register", json=engineer_payload)
    assert eng_reg_response.status_code == 201
    eng_res = eng_reg_response.json()
    engineer_id = eng_res["data"]["user_id"]
    print(f"-> Registered engineer with ID: {engineer_id}")

    # A. Test Assignments API
    print("-> Testing Assignment creation...")
    assignment_payload = {
        "complaint_id": complaint_id,
        "official_id": staff_id,
        "engineer_id": engineer_id,
        "remarks": "Assigning to official and engineer for resolution."
    }
    assign_res = client.post("/assignments", json=assignment_payload)
    assert assign_res.status_code == 201, assign_res.text
    assign_data = assign_res.json()["data"]
    assignment_id = assign_data["assignment_id"]
    assert assign_data["assignment_status"] == "Assigned"

    # Verify that complaint status was updated to "Assigned"
    comp_detail_res = client.get(f"/complaints/{complaint_id}")
    assert comp_detail_res.status_code == 200
    assert comp_detail_res.json()["data"]["status"] == "Assigned"

    # GET /assignments
    get_assign_res = client.get("/assignments")
    assert get_assign_res.status_code == 200
    assert len(get_assign_res.json()["data"]) >= 1

    # GET /assignments/{id}
    get_assign_by_id_res = client.get(f"/assignments/{assignment_id}")
    assert get_assign_by_id_res.status_code == 200
    assert get_assign_by_id_res.json()["data"]["remarks"] == assignment_payload["remarks"]

    # GET /assignments/engineer/{engineer_id}
    get_assign_by_eng_res = client.get(f"/assignments/engineer/{engineer_id}")
    assert get_assign_by_eng_res.status_code == 200
    assert len(get_assign_by_eng_res.json()["data"]) >= 1

    # GET /assignments/official/{official_id}
    get_assign_by_off_res = client.get(f"/assignments/official/{staff_id}")
    assert get_assign_by_off_res.status_code == 200
    assert len(get_assign_by_off_res.json()["data"]) >= 1

    # PUT /assignments/{id}
    update_assign_payload = {
        "remarks": "Updated assignment remarks."
    }
    put_assign_res = client.put(f"/assignments/{assignment_id}", json=update_assign_payload)
    assert put_assign_res.status_code == 200
    assert put_assign_res.json()["data"]["remarks"] == "Updated assignment remarks."

    # B. Test Status APIs
    print("-> Testing Status APIs...")
    # POST /status
    status_payload = {
        "complaint_id": complaint_id,
        "status": "In Progress",
        "remarks": "Work started on site.",
        "updated_by": staff_id
    }
    status_post_res = client.post("/status", json=status_payload)
    assert status_post_res.status_code == 201, status_post_res.text
    status_id = status_post_res.json()["data"]["status_id"]

    # GET /status/{complaint_id}
    status_get_res = client.get(f"/status/{complaint_id}")
    assert status_get_res.status_code == 200
    # There should be 3 status histories: Submitted (initial), Assigned (via assignment), In Progress (manual status update)
    assert len(status_get_res.json()["data"]) >= 3

    # PUT /status/{status_id}
    status_put_payload = {
        "remarks": "Corrected: Work started on site yesterday."
    }
    status_put_res = client.put(f"/status/{status_id}", json=status_put_payload)
    assert status_put_res.status_code == 200
    assert status_put_res.json()["data"]["remarks"] == "Corrected: Work started on site yesterday."

    # C. Test Notification APIs
    print("-> Testing Notification APIs...")
    # POST /notifications
    notif_payload = {
        "user_id": user_id,
        "complaint_id": complaint_id,
        "title": "Complaint Status Update",
        "message": "Your complaint status has changed to In Progress."
    }
    notif_post_res = client.post("/notifications", json=notif_payload)
    assert notif_post_res.status_code == 201, notif_post_res.text
    notification_id = notif_post_res.json()["data"]["notification_id"]

    # GET /notifications
    notif_get_all = client.get("/notifications")
    assert notif_get_all.status_code == 200
    assert len(notif_get_all.json()["data"]) >= 1

    # GET /notifications/{user_id}
    notif_get_user = client.get(f"/notifications/{user_id}")
    assert notif_get_user.status_code == 200
    assert len(notif_get_user.json()["data"]) >= 1

    # PUT /notifications/{id}
    notif_put_payload = {
        "status": "Read"
    }
    notif_put_res = client.put(f"/notifications/{notification_id}", json=notif_put_payload)
    assert notif_put_res.status_code == 200
    assert notif_put_res.json()["data"]["status"] == "Read"

    # D. Test Feedback APIs
    print("-> Testing Feedback APIs...")
    # Attempt feedback on In Progress complaint (Expect 400 because not Resolved)
    feedback_payload = {
        "complaint_id": complaint_id,
        "citizen_id": user_id,
        "rating": 5,
        "comments": "Great service!"
    }
    fail_feedback_res = client.post("/feedback", json=feedback_payload)
    assert fail_feedback_res.status_code == 400
    print("-> Correctly rejected feedback for non-resolved complaint.")

    # Resolve the complaint first via status update
    resolve_status_payload = {
        "complaint_id": complaint_id,
        "status": "Resolved",
        "remarks": "Problem resolved completely.",
        "updated_by": staff_id
    }
    client.post("/status", json=resolve_status_payload)

    # Now create feedback (Expect 201)
    feedback_res = client.post("/feedback", json=feedback_payload)
    assert feedback_res.status_code == 201, feedback_res.text
    feedback_id = feedback_res.json()["data"]["feedback_id"]

    # GET /feedback
    feedbacks_res = client.get("/feedback")
    assert feedbacks_res.status_code == 200
    assert len(feedbacks_res.json()["data"]) >= 1

    # GET /feedback/{complaint_id}
    feedback_by_comp_res = client.get(f"/feedback/{complaint_id}")
    assert feedback_by_comp_res.status_code == 200
    assert len(feedback_by_comp_res.json()["data"]) >= 1

    # PUT /feedback/{id}
    feedback_update_payload = {
        "comments": "Actually, it was absolutely fantastic!"
    }
    feedback_put_res = client.put(f"/feedback/{feedback_id}", json=feedback_update_payload)
    assert feedback_put_res.status_code == 200
    assert feedback_put_res.json()["data"]["comments"] == "Actually, it was absolutely fantastic!"

    # Clean up created entries before finishing tests
    print("-> Cleaning up module entries...")
    # Delete feedback
    del_feedback_res = client.delete(f"/feedback/{feedback_id}")
    assert del_feedback_res.status_code == 200

    # Delete notifications
    del_notif_res = client.delete(f"/notifications/{notification_id}")
    assert del_notif_res.status_code == 200

    # Delete assignments
    del_assign_res = client.delete(f"/assignments/{assignment_id}")
    assert del_assign_res.status_code == 200

    # Delete engineer user
    del_eng_res = client.delete(f"/users/{engineer_id}")
    assert del_eng_res.status_code == 200

    # Test Delete Complaint
    print("-> Testing delete complaint...")
    del_comp_res = client.delete(f"/complaints/{complaint_id}")
    assert del_comp_res.status_code == 200
    assert del_comp_res.json()["success"] is True
    
    # Verify complaint is deleted (GET returns 404)
    get_del_comp_res = client.get(f"/complaints/{complaint_id}")
    assert get_del_comp_res.status_code == 404
    print("-> Complaint CRUD and query operations verified successfully.")

    # -----------------------------
    # 4. Clean up Test Data (DELETE)
    # -----------------------------
    print("\n5. Cleaning up test data...")
    # Delete users
    del_user_response = client.delete(f"/users/{user_id}")
    assert del_user_response.status_code == 200
    assert del_user_response.json()["success"] is True
    
    del_staff_response = client.delete(f"/users/{staff_id}")
    assert del_staff_response.status_code == 200
    
    # Verify user is deleted (GET returns 404)
    get_deleted_user = client.get(f"/users/{user_id}")
    assert get_deleted_user.status_code == 404
    print("-> Citizens/Staff deleted and verified successfully.")
    
    # Delete department
    del_dept_response = client.delete(f"/departments/{dept_id}")
    assert del_dept_response.status_code == 200
    assert del_dept_response.json()["success"] is True
    
    # Verify department is deleted (GET returns 404)
    get_deleted_dept = client.get(f"/departments/{dept_id}")
    assert get_deleted_dept.status_code == 404
    print("-> Departments deleted and verified successfully.")
    
    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        test_flow()
    except AssertionError as e:
        print(f"\nTEST FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
