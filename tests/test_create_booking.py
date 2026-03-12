import allure
import pytest
import requests

@allure.feature("Booking")
class TestCreateBooking:
    @allure.story("Создание бронирования")
    def test_create_booking(self, api_client, generate_random_booking_data):
        booking_data = generate_random_booking_data

        with allure.step("Отправка запроса на создание бронирования"):
            response_json = api_client.create_booking(booking_data)

        with allure.step("Проверка созданного бронирования"):
            assert response_json["booking"]["firstname"] == booking_data["firstname"]
            assert response_json["booking"]["lastname"] == booking_data["lastname"]
            assert response_json["booking"]["totalprice"] == booking_data["totalprice"]
            assert response_json["booking"]["depositpaid"] == booking_data["depositpaid"]
            assert response_json["booking"]["bookingdates"] == booking_data["bookingdates"]
            assert response_json["booking"]["additionalneeds"] == booking_data["additionalneeds"]
            assert "bookingid" in response_json, "В ответе отсутствует ID бронирования"
            assert isinstance(response_json["bookingid"], int), "ID бронирования должен быть числом"

        print(f"Создана бронь с ID: {response_json['bookingid']}")
        print(f"Полный ответ: {response_json}") # вывела для себя, чтобы проверить верно ли создается бронь






