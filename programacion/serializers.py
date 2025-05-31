from rest_framework import serializers
from .models import Aula, HorarioAula

class AulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aula
        fields = '__all__'

class HorarioAulaSerializer(serializers.ModelSerializer):
    aula = AulaSerializer()
    class Meta:
        model = HorarioAula
        fields = '__all__'