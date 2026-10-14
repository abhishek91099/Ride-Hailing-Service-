def test_api_booking_completion_and_histories(client):
    user_response = client.post(
        "/api/v1/users",
        json={"name": "Rider", "phone": "9000000001", "roles": ["rider"]},
    )
    assert user_response.status_code == 201
    rider_id = user_response.json()["id"]

    driver_response = client.post(
        "/api/v1/drivers",
        json={
            "name": "Driver",
            "phone": "9000000002",
            "vehicle_type": "SEDAN",
            "latitude": 12.9700,
            "longitude": 77.5900,
        },
    )
    assert driver_response.status_code == 201
    driver_id = driver_response.json()["id"]

    coupon_response = client.post(
        "/api/v1/coupons",
        json={"code": "SAVE10", "discount_percentage": 10},
    )
    assert coupon_response.status_code == 201

    booking_response = client.post(
        "/api/v1/rides",
        headers={"X-Request-ID": "assignment-demo-request"},
        json={
            "rider_id": rider_id,
            "pickup": {"latitude": 12.9700, "longitude": 77.5900},
            "destination": {"latitude": 12.9800, "longitude": 77.6000},
            "requested_vehicle_type": "SEDAN",
            "coupon_code": "save10",
        },
    )
    assert booking_response.status_code == 201
    assert booking_response.headers["X-Request-ID"] == "assignment-demo-request"
    ride = booking_response.json()
    assert ride["status"] == "ONGOING"
    assert ride["driver_id"] == driver_id
    assert ride["final_fare"] == "45.00"

    rider_history = client.get(f"/api/v1/rides/users/{rider_id}")
    assert rider_history.status_code == 200
    assert rider_history.json()[0]["id"] == ride["id"]

    completion_response = client.patch(f"/api/v1/rides/{ride['id']}/complete")
    assert completion_response.status_code == 200
    assert completion_response.json()["status"] == "COMPLETED"
    assert completion_response.json()["final_fare"] == "45.00"

    complete_again_response = client.patch(f"/api/v1/rides/{ride['id']}/complete")
    assert complete_again_response.status_code == 409
    cancel_completed_response = client.patch(f"/api/v1/rides/{ride['id']}/cancel")
    assert cancel_completed_response.status_code == 409

    driver_history = client.get(f"/api/v1/rides/drivers/{driver_id}")
    assert driver_history.status_code == 200
    assert driver_history.json()[0]["status"] == "COMPLETED"
