from django.db import models

class Game(models.Model):
    start_time = models.DateTimeField('start time and date')
    board = models.CharField(max_length=50)
    
    def __unicode__(self):
        return str(self.start_time)

        class Meta:
            ordering = ('start_time')