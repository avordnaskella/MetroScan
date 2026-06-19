from django.contrib import admin
from .models import User, Train, RFIDTag, Station, PassEvent

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'role')
    search_fields = ('username',)

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_id', 'route_number', 'numbers_wagons', 'departure_point', 'arrival_point')
    list_filter = ('route_number',)

@admin.register(RFIDTag)
class RFIDTagAdmin(admin.ModelAdmin):
    list_display = ('rfid_tag_id', 'tag_uid', 'train')
    search_fields = ('tag_uid',)

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('station_id', 'name')
    search_fields = ('name',)

@admin.register(PassEvent)
class PassEventAdmin(admin.ModelAdmin):
    list_display = ('pass_event_id', 'station', 'train', 'rfid_tag', 'occurred_at', 'status')
    list_filter = ('status', 'station')
    ordering = ('-occurred_at',)