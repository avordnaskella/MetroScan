from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Django хранит хеш
    role = models.CharField(max_length=50)  # Администратор, Диспетчер, Аналитик

    def __str__(self):
        return self.username


class Train(models.Model):
    train_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    route_number = models.IntegerField(verbose_name="Номер маршрута")
    numbers_wagons = models.IntegerField(verbose_name="Количество вагонов")
    departure_point = models.CharField(max_length=100, verbose_name="Пункт отправки")
    arrival_point = models.CharField(max_length=100, verbose_name="Пункт конечного прибытия")

    def __str__(self):
     return f"Поезд {self.route_number} (маршрут {self.route_number})"


class RFIDTag(models.Model):
    rfid_tag_id = models.AutoField(primary_key=True)
    train = models.OneToOneField(Train, on_delete=models.CASCADE, verbose_name="Поезд")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    tag_uid = models.CharField(max_length=50, unique=True, verbose_name="Идентификатор метки")

    def __str__(self):
        return self.tag_uid


class Station(models.Model):
    station_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    name = models.CharField(max_length=100, unique=True, verbose_name="Название станции")

    def __str__(self):
        return self.name


class PassEvent(models.Model):
    class Status(models.TextChoices):
        OK = 'OK', 'Штатное прибытие'
        ERROR = 'ERROR', 'Ошибка идентификации'
        DUPLICATE = 'DUPLICATE', 'Дубликат'

    pass_event_id = models.AutoField(primary_key=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, verbose_name="Станция")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Поезд")
    rfid_tag = models.ForeignKey(
        RFIDTag, 
        on_delete=models.CASCADE, 
        null=True,   # теперь можно оставить пустым
        blank=True,  # при создании через формы можно не заполнять
        verbose_name="RFID-метка"
    )
    occurred_at = models.DateTimeField(auto_now_add=True, verbose_name="Время прохождения")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OK, verbose_name="Статус события")

    def __str__(self):
        return f"Событие {self.pass_event_id} на станции {self.station.name} в {self.occurred_at}"