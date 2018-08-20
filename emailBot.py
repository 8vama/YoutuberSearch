import smtplib

#help(smtplib)

smtpObj = smtplib.SMTP('smtp.gmail.com', 587)

smtpObj.starttls()

smtpObj.login('mamingxuan1998@gmail.com','sender_password')


smtpObj.sendmail("mamingxuan1998@gmail.com","mm99@rice.edu","Sent from a python script!")