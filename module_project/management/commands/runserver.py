from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand

class Command(RunserverCommand):
    default_addr = '10.2.0.54'
    default_port = '7350'