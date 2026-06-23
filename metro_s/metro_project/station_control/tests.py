from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import User, Train, RFIDTag, Station, PassEvent

class TrainModelTest(TestCase):
    """Тесты для модели Train"""

    def setUp(self):
        self.user = User.objects.create(
            username='admin',
            password='admin123',
            role='Администратор'
        )

    def test_create_train(self):
        train = Train.objects.create(
            route_number=27026,
            numbers_wagons=5,
            departure_point="Автозаводская",
            arrival_point="Стрелка",
            user=self.user
        )
        self.assertEqual(train.route_number, 27026)
        self.assertEqual(train.numbers_wagons, 5)
        self.assertEqual(str(train), "Поезд 27026 (маршрут 27026)")

class RFIDTagModelTest(TestCase):
    """Тесты для модели RFIDTag"""

    def setUp(self):
        self.user = User.objects.create(
            username='admin',
            password='admin123',
            role='Администратор'
        )
        self.train = Train.objects.create(
            route_number=27026,
            numbers_wagons=5,
            departure_point="Автозаводская",
            arrival_point="Стрелка",
            user=self.user
        )

    def test_create_rfid_tag(self):
        tag = RFIDTag.objects.create(
            tag_uid="RFID_001",
            train=self.train,
            user=self.user
        )
        self.assertEqual(tag.tag_uid, "RFID_001")
        self.assertEqual(tag.train.route_number, 27026)

class StationModelTest(TestCase):
    """Тесты для модели Station"""

    def setUp(self):
        self.user = User.objects.create(
            username='admin',
            password='admin123',
            role='Администратор'
        )

    def test_create_station(self):
        station = Station.objects.create(
            name="Стрелка",
            user=self.user
        )
        self.assertEqual(station.name, "Стрелка")
        self.assertEqual(str(station), "Стрелка")

class PassEventModelTest(TestCase):
    """Тесты для модели PassEvent"""

    def setUp(self):
        self.user = User.objects.create(
            username='admin',
            password='admin123',
            role='Администратор'
        )
        self.train = Train.objects.create(
            route_number=27026,
            numbers_wagons=5,
            departure_point="Автозаводская",
            arrival_point="Стрелка",
            user=self.user
        )
        self.tag = RFIDTag.objects.create(
            tag_uid="RFID_001",
            train=self.train,
            user=self.user
        )
        self.station = Station.objects.create(
            name="Стрелка",
            user=self.user
        )

    def test_create_ok_event(self):
        """Тест создания штатного события"""
        event = PassEvent.objects.create(
            station=self.station,
            train=self.train,
            rfid_tag=self.tag,
            status=PassEvent.Status.OK
        )
        self.assertEqual(event.status, PassEvent.Status.OK)
        self.assertEqual(event.train.route_number, 27026)
        self.assertEqual(event.station.name, "Стрелка")

    def test_create_error_event(self):
        """Тест создания события с ошибкой"""
        event = PassEvent.objects.create(
            station=self.station,
            train=None,
            rfid_tag=None,
            status=PassEvent.Status.ERROR
        )
        self.assertEqual(event.status, PassEvent.Status.ERROR)
        self.assertIsNone(event.train)

class APITest(TestCase):
    """Тесты для API-эндпоинта"""

    def setUp(self):
        self.user = User.objects.create(
            username='admin',
            password='admin123',
            role='Администратор'
        )
        self.train = Train.objects.create(
            route_number=27026,
            numbers_wagons=5,
            departure_point="Автозаводская",
            arrival_point="Стрелка",
            user=self.user
        )
        self.tag = RFIDTag.objects.create(
            tag_uid="RFID_001",
            train=self.train,
            user=self.user
        )
        self.station = Station.objects.create(
            name="Стрелка",
            user=self.user
        )

    def test_register_pass_success(self):
        """Тест успешной регистрации прохода"""
        response = self.client.post(reverse('register_pass'), {
            'tag_id': 'RFID_001',
            'station': 'Стрелка'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertEqual(response.json()['route_number'], 27026)

    def test_register_pass_unknown_tag(self):
        """Тест регистрации с неизвестной меткой"""
        response = self.client.post(reverse('register_pass'), {
            'tag_id': 'RFID_999',
            'station': 'Стрелка'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['status'], 'error')

    def test_register_pass_unknown_station(self):
        """Тест регистрации с неизвестной станцией"""
        response = self.client.post(reverse('register_pass'), {
            'tag_id': 'RFID_001',
            'station': 'Несуществующая станция'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_register_pass_missing_fields(self):
        """Тест регистрации без обязательных полей"""
        response = self.client.post(reverse('register_pass'), {
            'tag_id': 'RFID_001'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

class DuplicateCheckTest(TestCase):
    """Тесты для проверки дубликатов"""

    def setUp(self):
        self.user = User.objects.create(
            username='admin',
            password='admin123',
            role='Администратор'
        )
        self.train = Train.objects.create(
            route_number=27026,
            numbers_wagons=5,
            departure_point="Автозаводская",
            arrival_point="Стрелка",
            user=self.user
        )
        self.tag = RFIDTag.objects.create(
            tag_uid="RFID_001",
            train=self.train,
            user=self.user
        )
        self.station = Station.objects.create(
            name="Стрелка",
            user=self.user
        )

    def test_duplicate_check(self):
        """Тест проверки дубликатов: два одинаковых события подряд"""
        response1 = self.client.post(reverse('register_pass'), {
            'tag_id': 'RFID_001',
            'station': 'Стрелка'
        }, content_type='application/json')
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.post(reverse('register_pass'), {
            'tag_id': 'RFID_001',
            'station': 'Стрелка'
        }, content_type='application/json')
        
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json()['status'], 'duplicate')

class DashboardViewTest(TestCase):
    """Тесты для главной страницы диспетчера"""

    def setUp(self):
        self.user = User.objects.create(
            username='admin',
            password='admin123',
            role='Администратор'
        )
        # Логинимся через свой метод (если он есть)
        # Или просто создаём сессию
        session = self.client.session
        session['user_id'] = self.user.user_id
        session.save()

    def test_dashboard_accessible(self):
     response = self.client.get(reverse('dashboard'))
    # Страница требует авторизации, редирект на логин
     self.assertEqual(response.status_code, 302)
     self.assertIn('/login/', response.url)