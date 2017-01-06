from django.shortcuts import render,redirect
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.conf import settings
from django.forms.utils import ErrorList
from django import forms

from .forms import RegisterForm, LoginForm, OTPForm
from .models import Student, StudenClass, OTP
from twilio.rest import TwilioRestClient
import string
import random

class IndexView(TemplateView):
    template_name = 'base.html'
    def dispatch(self, request, *args, **kwargs):
        self.request.session.flush()
        return super(IndexView, self).dispatch(request, *args, **kwargs)

class RegisterView(FormView):
    template_name = "register.html"
    form_class = RegisterForm
    success_url = '/otp-register/'

    def form_valid(self, form):
        student_name = form.cleaned_data.get('name')
        mobile_phone = form.cleaned_data.get('mobile_phone')
        class_name   = form.cleaned_data.get('class_name')

        obj, create  = Student.objects.get_or_create(phone_number=mobile_phone,
                                                     defaults={'name': student_name} )

        st = StudenClass.objects.create(student=obj, class_name=class_name)

        #store on session
        self.request.session['student_id'] = obj.id

        #save and generate otp
        otp = generate_otp()
        obj_otp, create = OTP.objects.get_or_create(student=obj,
                                                    type_name=1,
                                                    defaults={'otp': otp})
        self.request.session['otp'] = otp
        send_otp(form.cleaned_data.get('mobile_phone'),otp)
        
        return super(RegisterView, self).form_valid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = '/otp-login'

    def form_valid(self, form):
      
        mobile_phone = form.cleaned_data.get('mobile_phone')
      
        obj = Student.objects.get(phone_number=mobile_phone)
    

        #store on session
        self.request.session['student_id_login'] = obj.id

        #save and generate otp
        otp = generate_otp()
        obj_otp, create = OTP.objects.get_or_create(student=obj,
                                                    type_name=1,
                                                    defaults={'otp': otp})
        self.request.session['otp_login'] = otp
        send_otp(form.cleaned_data.get('mobile_phone'),otp)
      
        return super(LoginView, self).form_valid(form)

    
class RegisterOtpView(FormView):
    template_name = "otp.html"
    form_class    = OTPForm
    success_url   = '/dashboard'

    def form_valid(self, form):
        otp = form.cleaned_data.get('otp')
        student_id = self.request.session.get('student_id', False)
        if not student_id:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList([
                                    u'OTP NOT VALID'
                                ])
            return self.form_invalid(form)
        otp_ref = self.request.session.get('otp', False)
        if not otp_ref or otp_ref != otp:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList([
                                    u'OTP NOT VALID %s %s' % (otp_ref, otp)
                                ])
            return self.form_invalid(form)
        
        #check if type is 1, an check user 
        return super(RegisterOtpView, self).form_valid(form)
    

class LoginOtpView(FormView):
    template_name = "otp.html"
    form_class    = OTPForm
    success_url   = "/dashboard"
    
    def form_valid(self, form):
        otp = form.cleaned_data.get('otp')
        student_id = self.request.session.get('student_id_login', False)
        if not student_id:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList([
                                    u'OTP NOT VALID'
                                ])
            return self.form_invalid(form)
        otp_ref = self.request.session.get('otp_login', False)
        if not otp_ref or otp_ref != otp:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList([
                                    u'OTP NOT VALID %s %s' % (otp_ref, otp)
                                ])
            return self.form_invalid(form)
        
        return super(LoginOtpView, self).form_valid(form)

class DashboardView(TemplateView):
    template_name = "dashboard.html"
    
    def dispatch(self, request, *args, **kwargs):
        student_id = self.request.session.get('student_id', False)
        if not student_id:
            student_id = self.request.session.get('student_id_login', False)
        if not student_id:
            return redirect('index')

        return super(TemplateView, self).dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        student_id = self.request.session.get('student_id', False)
        if not student_id:
            student_id = self.request.session.get('student_id_login', False)
        context['student'] = Student.objects.get(id=student_id)
        context['class']   = StudenClass.objects.filter(student__id=student_id)
        
        return context

def send_otp(phone_number, otp):
        account = settings.ACCOUNT_SID
        token   = settings.AUTH_TOKEN
        
        client = TwilioRestClient(account, token)

        message = client.sms.messages.create(to=phone_number,
                                             from_="+14143774545",
                                             body=otp)
    

def generate_otp():
    otp =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    return otp
