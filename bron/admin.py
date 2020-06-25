from django.contrib import admin
from .models import Booking, Merop

@admin.register(Booking)

class BookingAdmin(admin.ModelAdmin):
   list_display = ('username', 'email', 'places', 'mero', 'conf')

@admin.register(Merop)

class MeropAdmin(admin.ModelAdmin):
    list_display = ('mero', 'place', 'date')
