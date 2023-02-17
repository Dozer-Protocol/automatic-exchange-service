from django.contrib import admin
from .models import Tx

# Register your models here.
@admin.register(Tx)

class TxAdmin(admin.ModelAdmin):
    list_display = ("txid_receive","creation_time", "success", "txid_send")