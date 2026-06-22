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
    """Главная страница диспетчера с фильтром по станции"""
    station_filter = request.GET.get('station', 'all')
    events = PassEvent.objects.select_related('station', 'train', 'rfid_tag')
    
    if station_filter != 'all':
        events = events.filter(station__station_id=station_filter)
    
    events = events.order_by('-occurred_at')[:20]
    stations = Station.objects.all()
    
    context = {
        'events': events,
        'stations': stations,
        'selected_station': station_filter,
    }
    return render(request, 'dashboard.html', context)