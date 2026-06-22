import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import redis

def sendmail(email:str):
    otp="".join(secrets.choice("0123456789") for i in range(6))

    mail=MIMEMultipart()
    mail["From"]="singhsavi333@gmail.com"
    mail["To"]=email
    mail["Subject"]="Your one time password"
    mail.attach(MIMEText(f"Your OTP for registering is: {otp}","plain"))
    smtpserver=smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.starttls()
    smtpserver.login(mail["From"],"olej xwui swyc ayes")
    smtpserver.sendmail(mail["From"],mail["To"],mail.as_string())
    smtpserver.quit()
    r=redis.Redis(host="localhost", port=6379,db=0,decode_responses=True)
    r.set(otp,email,ex=300)
