from __future__ import unicode_literals

from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=12, unique=True)

    def __unicode__(self):
        return "%s-%s" % (self.name, self.phone_number)

class StudenClass(models.Model):
    student = models.ForeignKey(Student)
    class_name = models.CharField(max_length=128)
    
    def __unicode__(self):
        return "%s - %s " % (self.student, self.class_name)


class OTP(models.Model):
    type_name = models.PositiveIntegerField(default=0)
    student   = models.ForeignKey(Student)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)
    otp        = models.CharField(max_length=8)
