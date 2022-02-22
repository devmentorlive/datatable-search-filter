from django.db import models


class Program(models.Model):
    class Meta:
        db_table = "cal_program"

    prog_id = models.CharField(max_length=120, primary_key=True)
    program = models.TextField(max_length=120)
    year_level = models.TextField(null=True, max_length=120)
    deleted = models.BooleanField(default=False)

