from django.db.models.signals import pre_save
from django.dispatch import receiver
from geopy.geocoders import Nominatim
from .models import VariantStudyagmp

@receiver(pre_save, sender=VariantStudyagmp)
def generate_coordinates(sender, instance, **kwargs):
    if not instance.latitude or not instance.longitude:
        geolocator = Nominatim(user_agent="agmp_app")
        location = geolocator.geocode(instance.country_participant)
        if location:
            instance.latitude = location.latitude
            instance.longitude = location.longitude

    if not instance.latitude_01 or not instance.longitude_01:
        geolocator = Nominatim(user_agent="agmp_app")
        location = geolocator.geocode(instance.country_participant_01)
        if location:
            instance.latitude_01 = location.latitude
            instance.longitude_01 = location.longitude

    if not instance.latitude_02 or not instance.longitude_02:
        geolocator = Nominatim(user_agent="agmp_app")
        location = geolocator.geocode(instance.country_participant_02)
        if location:
            instance.latitude_02 = location.latitude
            instance.longitude_02 = location.longitude

    if not instance.latitude_03 or not instance.longitude_03:
        geolocator = Nominatim(user_agent="agmp_app")
        location = geolocator.geocode(instance.country_participant_03)
        if location:
            instance.latitude_03 = location.latitude
            instance.longitude_03 = location.longitude

    if not instance.latitude_04 or not instance.longitude_04:
        geolocator = Nominatim(user_agent="agmp_app")
        location = geolocator.geocode(instance.country_participant_04)
        if location:
            instance.latitude_04 = location.latitude
            instance.longitude_04 = location.longitude

    if not instance.latitude_05 or not instance.longitude_05:
        geolocator = Nominatim(user_agent="agmp_app")
        location = geolocator.geocode(instance.country_participant_05)
        if location:
            instance.latitude_05 = location.latitude
            instance.longitude_05 = location.longitude

    if not instance.latitude_06 or not instance.longitude_06:
        geolocator = Nominatim(user_agent="agmp_app")
        location = geolocator.geocode(instance.country_participant_06)
        if location:
            instance.latitude_06 = location.latitude
            instance.longitude_06 = location.longitude

    if not instance.latitude_07 or not instance.longitude_07:
        geolocator = Nominatim(user_agent="agmp_app")
        location = geolocator.geocode(instance.country_participant_07)
        if location:
            instance.latitude_07 = location.latitude
            instance.longitude_07 = location.longitude






