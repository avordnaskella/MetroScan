from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import RFIDTag, PassEvent, Station
from django.utils import timezone  
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import RFIDTag, PassEvent, Station, Train
import csv
from django.http import HttpResponse 

@api_view(['POST'])
def register_pass(request):
    """Эндпоинт для регистрации прохода поезда"""
    tag_uid = request.data.get('tag_id')
    station_name = request.data.get('station')
    
    if not tag_uid or not station_name:
        return Response({'error': 'tag_id и station обязательны'}, status=400)
    
    # Находим станцию
    try:
        station = Station.objects.get(name=station_name)
    except Station.DoesNotExist:
        return Response({'error': f'Станция "{station_name}" не найдена'}, status=404)
    
    # Ищем RFID-метку
    try:
        tag = RFIDTag.objects.get(tag_uid=tag_uid)
        train = tag.train
        
        # Проверяем дубликат (за последние 10 секунд)
        recent = PassEvent.objects.filter(
            rfid_tag=tag,
            occurred_at__gte=timezone.now() - timedelta(seconds=10)
        ).exists()
        
        if recent:
            return Response({'status': 'duplicate', 'message': 'Дубликат события'}, status=200)
        
        # Создаём штатное событие
        event = PassEvent.objects.create(
            station=station,
            train=train,
            rfid_tag=tag,
            status=PassEvent.Status.OK
        )
        
        return Response({
            'status': 'ok',
            'train_id': train.train_id,
            'route_number': train.route_number,
            'timestamp': event.occurred_at.isoformat()
        })
        
    except RFIDTag.DoesNotExist:
        # Создаём событие с ошибкой
        event = PassEvent.objects.create(
            station=station,
            train=None,
            rfid_tag=None,  # Нельзя, потому что ForeignKey не разрешает NULL
            status=PassEvent.Status.ERROR
        )
        return Response({
            'status': 'error',
            'message': f'Метка {tag_uid} не найдена в системе',
            'timestamp': event.occurred_at.isoformat()
        }, status=404)


def dashboard(request):
    """Главная страница диспетчера с фильтрацией"""
    events = PassEvent.objects.select_related('station', 'train', 'rfid_tag')
    
    # Фильтр по станции
    station_filter = request.GET.get('station', 'all')
    if station_filter != 'all':
        events = events.filter(stationstation_id=station_filter)
    
    # Фильтр по номеру поезда
    train_number = request.GET.get('train_number', '')
    if train_number:
        events = events.filter(trainroute_number=train_number)
    
    # Фильтр по коду метки
    tag_uid = request.GET.get('tag_uid', '')
    if tag_uid:
        events = events.filter(rfid_tagtag_uidicontains=tag_uid)
    
    # Фильтр по статусу
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        events = events.filter(status=status_filter)
    
    events = events.order_by('-occurred_at')[:50]  # показываем до 50 записей
    stations = Station.objects.all()
    
    context = {
        'events': events,
        'stations': stations,
        'selected_station': station_filter,
        'train_number': train_number,
        'tag_uid': tag_uid,
        'selected_status': status_filter,
    }
    return render(request, 'dashboard.html', context)


def export_csv(request):
    """Экспорт всех событий в CSV с учётом текущих фильтров"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="metro_scan_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Время', 'Номер поезда', 'Код метки', 'Станция', 'Статус'])
    
    events = PassEvent.objects.select_related('station', 'train', 'rfid_tag')
    
    # Применяем те же фильтры, что и в dashboard
    station_filter = request.GET.get('station', 'all')
    if station_filter != 'all':
        events = events.filter(stationstation_id=station_filter)
    
    train_number = request.GET.get('train_number', '')
    if train_number:
        events = events.filter(trainroute_number=train_number)
    
    tag_uid = request.GET.get('tag_uid', '')
    if tag_uid:
        events = events.filter(rfid_tagtag_uidicontains=tag_uid)
    
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        events = events.filter(status=status_filter)
    
    events = events.order_by('-occurred_at')
    
    for event in events:
        writer.writerow([
            event.occurred_at.strftime('%Y-%m-%d %H:%M:%S'),
            event.train.route_number if event.train else 'Неизвестный поезд',
            event.rfid_tag.tag_uid if event.rfid_tag else 'Неизвестно',
            event.station.name,
            event.get_status_display(),
        ])
    
    return response