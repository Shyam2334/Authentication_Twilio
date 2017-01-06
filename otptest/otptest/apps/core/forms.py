from django  import forms

from .models import Student

class RegisterForm(forms.Form):
    name = forms.CharField(label="Your Name", max_length=128)
    mobile_phone = forms.RegexField(regex=r'^\+?1?\d{3,15}$',
                                    label="Phone Number",
                                    error_message = ("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    class_name = forms.CharField(label="Class Name", max_length=128)


class LoginForm(forms.Form):
    mobile_phone = forms.RegexField(regex=r'^\+?1?\d{3,15}$',
                                    label="Phone Number",
                                    error_message = ("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data.get('mobile_phone')

        student = Student.objects.filter(phone_number=mobile_phone).exists()

        if not student:
            raise forms.ValidationError("Mobile Phone Not found")
        
        return mobile_phone

class OTPForm(forms.Form):
    otp = forms.CharField(label="OTP", max_length=10)
    
    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        return otp
    
