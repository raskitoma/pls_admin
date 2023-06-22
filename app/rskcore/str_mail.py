#############################################
# core_mail.py
# (c)2023, Raskitoma.com
#--------------------------------------------
# Defaul mail strings
#-------------------------------------------- 

# OTP
MAIL_OTP = '''
Hola {},
<br>
<br>
El código para la activación de su cuenta de {} es: <strong>{}</strong>
<br>
<br>
Este código es válido por <strong>{}</strong> minutos.
<br>
<br>
Atentamente,
<br>
<br>
{}
<hr>
Este es un mensaje automático, por favor no responda al mismo. Para más información, consultas y soporte escribir a <strong>{}</strong>.
'''
MAIL_OTP_SUBJECT = '{} - Código de activación de cuenta.'

# Forgot password
MAIL_FORGOT = '''
Hola {},
<br>
<br>
Para recuperar la contraseña de su cuenta de {}, ingrese el siguiente código: <strong>{}</strong>
<br>
<br>
Este código es válido por <strong>{}</strong> minutos.
<br>
<br>
Atentamente,
<br>
<br>
{}
<hr>
Este es un mensaje automático, por favor no responda al mismo. Para más información, consultas y soporte escribir a <strong>{}</strong>.
'''
MAIL_FORGOT_SUBJECT = '{} - Código de recuperación de contraseña.'