import allure
import pytest
import requests
from pydantic import ValidationError
from core.models.booking import BookingResponse
from requests.exceptions import HTTPError

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

# тест по уроку за Ромой
@allure.story("Positive: creating booking with custom date")
def test_create_booking_with_custom_date(api_client):
    booking_data = {
        "firstname": "Ivan",
        "lastname": "Ivanovich",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-02-01",
            "checkout": "2025-02-10"
        },
        "additionalneeds": "Dinner"
    }

    response = api_client.create_booking(booking_data)

    try:
        BookingResponse(**response)
    except ValidationError as e:
        raise ValidationError(f"Response validation error: {e}")

    assert response["booking"]["firstname"] == booking_data["firstname"]
    assert response["booking"]["lastname"] == booking_data["lastname"]
    assert response["booking"]["totalprice"] == booking_data["totalprice"]
    assert response["booking"]["depositpaid"] == booking_data["depositpaid"]
    assert response["booking"]["bookingdates"]["checkin"] == booking_data["bookingdates"]["checkin"]
    assert response["booking"]["bookingdates"]["checkout"] == booking_data["bookingdates"]["checkout"]
    assert response["booking"]["additionalneeds"] == booking_data["additionalneeds"]

    assert response["bookingid"] == response["bookingid"]
    assert isinstance(response["bookingid"], int), "ID бронирования должен быть числом"
    assert response["booking"]["bookingdates"]["checkin"] <= response["booking"]["bookingdates"]["checkout"]
    assert response["booking"]["totalprice"] > 0


@allure.story("Позитив, проверка на опциональность поля additionalneeds")
def test_create_booking_without_additionalneeds(api_client):
    booking_data = {
        "firstname": "Ivan",
        "lastname": "Ivanovich",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-02-01",
            "checkout": "2025-02-10"
        }
        # additionalneeds отсутствует!
    }

    response = api_client.create_booking(booking_data)

    try:
        validated = BookingResponse(**response)
    except ValidationError as e:
        pytest.fail(f"Тест не должен падать без additionalneeds: {e}")

    assert validated.booking.additionalneeds is None, \
        f"additionalneeds должен быть None, получен {validated.booking.additionalneeds}"

@allure.story("Негативный кейс: отсутствует обязательное поле")
def test_create_booking_missing_firstname(api_client):
    """Негативный тест: отсутствует обязательное поле firstname"""
    booking_data = {
        # "firstname": "Ivan",  # поле отсутствует
        "lastname": "Ivanovich",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-02-01",
            "checkout": "2025-02-10"
        },
        "additionalneeds": "Dinner"
    }

    with pytest.raises(HTTPError) as exception_info:
        api_client.create_booking(booking_data)

        # Проверяем что это 500 ошибка
    error_message = str(exception_info.value)
    assert "500" in error_message, f"Ожидалась 500 ошибка, получена: {error_message}"


@allure.story("Negative: invalid data type for totalprice")
def test_create_booking_totalprice_as_string(api_client):
    """
    Негативный тест: totalprice передан строкой вместо числа
    """
    booking_data = {
        "firstname": "Ivan",
        "lastname": "Ivanovich",
        "totalprice": "сто пятьдесят",  # строка вместо числа!
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-02-01",
            "checkout": "2025-02-10"
        },
        "additionalneeds": "Dinner"
    }

    response = api_client.create_booking(booking_data)

    with pytest.raises(ValidationError) as exception_info:
        BookingResponse(**response)

    # Проверяем что ошибка связана с totalprice
    error_message = str(exception_info.value)
    assert "totalprice" in error_message.lower()
    assert "type" in error_message.lower()
















