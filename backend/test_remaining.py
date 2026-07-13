import sys
import os
from fastapi.testclient import TestClient

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

client = TestClient(app)

def cleanup_db():
    print("Database cleanup...")
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.department import Department
    from app.models.complaint import Complaint
    from app.models.assignment import Assignment
    from app.models.status_history import StatusHistory
    from app.models.notification import Notification
    from app.models.feedback import Feedback
    
    db = SessionLocal()
    try:
        test_emails = [
            "test_remaining_citizen@civicplatform.com",
            "test_remaining_official@civicplatform.com",
            "test_remaining_engineer@civicplatform.com"
        ]
        
        # Get test user IDs
        test_users = db.query(User).filter(User.email.in_(test_emails)).all()
        user_ids = [u.user_id for u in test_users]
        
        if user_ids:
            # Delete related feedback
            db.query(Feedback).filter(Feedback.citizen_id.in_(user_ids)).delete(synchronize_session=False)
            # Delete related notifications
            db.query(Notification).filter(Notification.user_id.in_(user_ids)).delete(synchronize_session=False)
            # Delete assignments
            db.query(Assignment).filter((Assignment.official_id.in_(user_ids)) | (Assignment.engineer_id.in_(user_ids))).delete(synchronize_session=False)
            
            # Delete complaints reported by test users
            db.query(Complaint).filter(Complaint.citizen_id.in_(user_ids)).delete(synchronize_session=False)
            
            # Delete users
            db.query(User).filter(User.user_id.in_(user_ids)).delete(synchronize_session=False)
            
        # Delete test departments
        db.query(Department).filter(Department.department_name.in_([
            "Remaining Test Sanitation Dept"
        ])).delete(synchronize_session=False)
        
        db.commit()
        print("-> Database cleanup completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"-> Warning during cleanup: {e}")
    finally:
        db.close()

def test_all_modules():
    cleanup_db()
    print("\nStarting remaining backend modules integration tests...")

    # 1. Setup Department & Users
    print("\nSetting up test departments and users...")
    dept_res = client.post("/departments", json={
        "department_name": "Remaining Test Sanitation Dept",
        "description": "Department for remaining integration tests."
    }).json()
    assert dept_res["success"] is True
    dept_id = dept_res["data"]["department_id"]

    citizen_res = client.post("/users/register", json={
        "email": "test_remaining_citizen@civicplatform.com",
        "password": "password123",
        "name": "Test Citizen",
        "role": "Citizen"
    }).json()
    assert citizen_res["success"] is True
    citizen_id = citizen_res["data"]["user_id"]

    official_res = client.post("/users/register", json={
        "email": "test_remaining_official@civicplatform.com",
        "password": "password123",
        "name": "Test Official",
        "role": "Official",
        "department_id": dept_id
    }).json()
    assert official_res["success"] is True
    official_id = official_res["data"]["user_id"]

    engineer_res = client.post("/users/register", json={
        "email": "test_remaining_engineer@civicplatform.com",
        "password": "password123",
        "name": "Test Engineer",
        "role": "Engineer",
        "department_id": dept_id
    }).json()
    assert engineer_res["success"] is True
    engineer_id = engineer_res["data"]["user_id"]

    # Create a baseline complaint
    comp_res = client.post("/complaints", json={
        "citizen_id": citizen_id,
        "title": "Broken street lamp",
        "description": "The street lamp at 5th block is broken and dark.",
        "category": "Electricity",
        "priority": "Medium",
        "department_id": dept_id
    }).json()
    assert comp_res["success"] is True
    complaint_id = comp_res["data"]["complaint_id"]
    print(f"-> Test complaint created with ID: {complaint_id}")

    # ==========================================
    # 2. Test Assignment APIs
    # ==========================================
    print("\n2. Testing Assignment APIs...")
    assign_payload = {
        "complaint_id": complaint_id,
        "official_id": official_id,
        "engineer_id": engineer_id,
        "remarks": "Please resolve this lamp issue ASAP."
    }
    
    # POST /assignments
    assign_res = client.post("/assignments", json=assign_payload)
    assert assign_res.status_code == 201, f"Expected 201, got {assign_res.status_code}. Response: {assign_res.text}"
    assign_data = assign_res.json()["data"]
    assignment_id = assign_data["assignment_id"]
    assert assign_data["assignment_status"] == "Assigned"
    print(f"-> Assignment created successfully with ID: {assignment_id}")

    # Verify complaint status updated to "Assigned"
    comp_check = client.get(f"/complaints/{complaint_id}").json()["data"]
    assert comp_check["status"] == "Assigned"
    # Verify status history has two items (Submitted, Assigned)
    assert len(comp_check["status_histories"]) == 2
    assert comp_check["status_histories"][1]["status"] == "Assigned"
    print("-> Verification passed: Complaint status changed to 'Assigned' and logged in status history.")

    # GET /assignments/engineer/{engineer_id}
    eng_assigns = client.get(f"/assignments/engineer/{engineer_id}").json()
    assert eng_assigns["success"] is True
    assert len(eng_assigns["data"]) >= 1

    # GET /assignments/official/{official_id}
    off_assigns = client.get(f"/assignments/official/{official_id}").json()
    assert off_assigns["success"] is True
    assert len(off_assigns["data"]) >= 1

    # GET /assignments/{id}
    get_assign = client.get(f"/assignments/{assignment_id}").json()
    assert get_assign["success"] is True
    assert get_assign["data"]["remarks"] == "Please resolve this lamp issue ASAP."

    # PUT /assignments/{id}
    update_assign_res = client.put(f"/assignments/{assignment_id}", json={
        "assignment_status": "Accepted",
        "remarks": "Under evaluation."
    })
    assert update_assign_res.status_code == 200
    assert update_assign_res.json()["data"]["assignment_status"] == "Accepted"
    print("-> Assignment status update accepted.")

    # DELETE /assignments/{id}
    del_assign_res = client.delete(f"/assignments/{assignment_id}")
    assert del_assign_res.status_code == 200
    # Verify deleted
    assert client.get(f"/assignments/{assignment_id}").status_code == 404
    print("-> Assignment deletion verified.")

    # ==========================================
    # 3. Test Status APIs
    # ==========================================
    print("\n3. Testing Status APIs...")
    # POST /status (to update complaint status to In Progress)
    status_payload = {
        "complaint_id": complaint_id,
        "status": "In Progress",
        "remarks": "Crew dispatched to site.",
        "updated_by": official_id
    }
    post_status_res = client.post("/status", json=status_payload)
    assert post_status_res.status_code == 201
    status_id = post_status_res.json()["data"]["status_id"]
    
    # Verify complaint status synced
    comp_check2 = client.get(f"/complaints/{complaint_id}").json()["data"]
    assert comp_check2["status"] == "In Progress"
    print("-> POST /status successfully updated complaints table status.")

    # GET /status/{complaint_id}
    get_status_res = client.get(f"/status/{complaint_id}")
    assert get_status_res.status_code == 200
    assert len(get_status_res.json()["data"]) >= 1

    # PUT /status/{status_id}
    put_status_res = client.put(f"/status/{status_id}", json={
        "status": "Closed",
        "remarks": "Problem solved completely."
    })
    assert put_status_res.status_code == 200
    assert put_status_res.json()["data"]["status"] == "Closed"
    # Verify complaint status updated to Closed
    comp_check3 = client.get(f"/complaints/{complaint_id}").json()["data"]
    assert comp_check3["status"] == "Closed"
    print("-> PUT /status/{status_id} successfully synced back to complaints table status.")

    # ==========================================
    # 4. Test Notification APIs
    # ==========================================
    print("\n4. Testing Notification APIs...")
    notif_payload = {
        "user_id": citizen_id,
        "complaint_id": complaint_id,
        "title": "Complaint Status Update",
        "message": "Your complaint status has been changed to Closed."
    }
    
    # POST /notifications
    post_notif_res = client.post("/notifications", json=notif_payload)
    assert post_notif_res.status_code == 201
    notif_id = post_notif_res.json()["data"]["notification_id"]
    assert post_notif_res.json()["data"]["status"] == "Unread"
    print(f"-> Notification created successfully with ID: {notif_id}")

    # GET /notifications
    list_notif = client.get("/notifications").json()
    assert len(list_notif["data"]) >= 1

    # GET /notifications/{user_id}
    user_notif = client.get(f"/notifications/{citizen_id}").json()
    assert len(user_notif["data"]) >= 1
    assert user_notif["data"][0]["notification_id"] == notif_id

    # PUT /notifications/{id}
    put_notif = client.put(f"/notifications/{notif_id}", json={
        "status": "Read"
    })
    assert put_notif.status_code == 200
    assert put_notif.json()["data"]["status"] == "Read"
    print("-> Notification marked as read.")

    # DELETE /notifications/{id}
    del_notif = client.delete(f"/notifications/{notif_id}")
    assert del_notif.status_code == 200
    assert client.get(f"/notifications/{citizen_id}").json()["data"] == []
    print("-> Notification deletion verified.")

    # ==========================================
    # 5. Test Feedback APIs
    # ==========================================
    print("\n5. Testing Feedback APIs...")
    # Create another complaint that is NOT resolved (starts as Submitted)
    unresolved_comp_res = client.post("/complaints", json={
        "citizen_id": citizen_id,
        "title": "Garbage pile up",
        "description": "Garbage has not been collected this week.",
        "category": "Sanitation",
        "priority": "Low",
        "department_id": dept_id
    }).json()
    unresolved_id = unresolved_comp_res["data"]["complaint_id"]

    # Try to POST feedback for unresolved complaint (Expect 400 Bad Request)
    fail_feedback_res = client.post("/feedback", json={
        "complaint_id": unresolved_id,
        "citizen_id": citizen_id,
        "rating": 5,
        "comments": "Great service!"
    })
    assert fail_feedback_res.status_code == 400
    assert "Feedback is only allowed for resolved complaints." in fail_feedback_res.json()["message"]
    print("-> Validation passed: Feedback on non-resolved complaint rejected with 400 Bad Request.")

    # Update unresolved complaint to Resolved
    client.post("/status", json={
        "complaint_id": unresolved_id,
        "status": "Resolved",
        "remarks": "Garbage cleared.",
        "updated_by": official_id
    })

    # Now POST feedback on resolved complaint (Should succeed)
    success_feedback_res = client.post("/feedback", json={
        "complaint_id": unresolved_id,
        "citizen_id": citizen_id,
        "rating": 5,
        "comments": "Excellent job clearing the garbage pile!"
    })
    assert success_feedback_res.status_code == 201
    feedback_id = success_feedback_res.json()["data"]["feedback_id"]
    print(f"-> Feedback created successfully on resolved complaint with ID: {feedback_id}")

    # GET /feedback
    feedbacks_list = client.get("/feedback").json()
    assert len(feedbacks_list["data"]) >= 1

    # GET /feedback/{complaint_id}
    comp_feedback = client.get(f"/feedback/{unresolved_id}").json()
    assert len(comp_feedback["data"]) == 1
    assert comp_feedback["data"][0]["feedback_id"] == feedback_id

    # PUT /feedback/{id}
    put_feedback = client.put(f"/feedback/{feedback_id}", json={
        "rating": 4,
        "comments": "Good job but could be faster next time."
    })
    assert put_feedback.status_code == 200
    assert put_feedback.json()["data"]["rating"] == 4
    print("-> Feedback updated successfully.")

    # DELETE /feedback/{id}
    del_feedback = client.delete(f"/feedback/{feedback_id}")
    assert del_feedback.status_code == 200
    assert len(client.get(f"/feedback/{unresolved_id}").json()["data"]) == 0
    print("-> Feedback deletion verified.")

    # Cleanup unresolved test complaints to keep db clean
    cleanup_db()

    print("\nALL INTEGRATION TESTS PASSED SUCCESSFULLY FOR THE REMAINING MODULES!")

if __name__ == "__main__":
    try:
        test_all_modules()
    except AssertionError as e:
        print(f"\nTEST FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
