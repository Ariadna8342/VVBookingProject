import requests
import os
from dotenv import load_dotenv
from core.settings.enviroments import Environment
import allure
from core.clients.endpoints import Endpoints
from core.settings.config import Users, Timeouts

load_dotenv()

class ApiClient:
    def __init__(self):
        environment_str = os.getenv("ENVIRONMENT")
        try:
            environment = Environment[environment_str]
        except KeyError:
            raise ValueError(f"Unsupported environment value {environment_str}")

        self.base_url = self.get_base_url(environment)
        self.session = requests.Session()
        self.session.headers = {
            "Content-Type": "application/json"
        }

    def get_base_url(self, environment: Environment) -> str:
        if environment == Environment.TEST:
            return os.getenv('TEST_BASE_URL')
        elif environment == Environment.PROD:
            return os.getenv('PROD_BASE_URL')
        else:
            raise ValueError(f"Unsupported environment value {environment}")


    def get(self, endpoint, params=None, status_code = 200):
        url = self.base_url + endpoint
        response = requests.get(url, headers=self.headers, params=params)
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def post(self, endpoint, data=None, status_code = 200):
        url = self.base_url + endpoint
        response = requests.post(url, headers=self.headers, json=data)
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def ping(self):
        with allure.step("Ping api client"):
            url= f'{self.base_url}{Endpoints.PING_ENDPOINT}'
            response = self.session.get(url)
            response.raise_for_status()
        with allure.step("Assert status code"):
            assert response.status_code == 201, f'Expected status 201 but got {response.status_code}'
        return response.status_code

    def auth(self):
        with allure.step("Getting authenticate"):
            url= f'{self.base_url}{Endpoints.AUTH_ENDPOINT}'
            payload = {'username': Users.USERNAME, 'password': Users.PASSWORD}
            response = self.session.post(url, json=payload, timeout = Timeouts.TIMEOUT)
            response.raise_for_status()
        with allure.step("Checking status code"):
            assert response.status_code == 200, f'Expected status 200 but got {response.status_code}'
        token = response.json().get('token')
        with allure.step("Updating header with authorization"):
            self.session.headers.update({'Authorization': f'Bearer {token}'})

    def get_booking_by_id(self, firstname, lastname, checkin, checkout):
        with allure.step("Проверка бронирования по Id"):
            url= f'{self.base_url}{Endpoints.BOOKING_ENDPOINT}'
            parameters = {}
            if firstname:
                parameters['firstname'] = firstname
            if lastname:
                parameters['lastname'] = lastname
            if checkin:
                parameters['checkin'] = checkin
            if checkout:
                parameters['checkout'] = checkout

            response = self.session.get(url, params=parameters)
            response.raise_for_status()

        with allure.step("Проверка статус кода"):
            assert response.status_code == 200, f'Ожидаемый статус 200, но получен {response.status_code}'

        with allure.step("Проверка структуры ответа"):
            bookings = response.json() #Преобразование ответа в json
            assert isinstance(bookings, list), f'Ожидается список, но получен {type(bookings)}'
            if bookings:
                for booking in bookings:
                    assert isinstance(booking, dict), f'Ожидается словарь, но получен {type(booking)}'
            assert isinstance(booking['bookingId'], int), 'bookingId должно быть числом'

        with allure.step(f'Проверка количества полученных bookingId, получено {len(bookings)}'):
            return bookings








