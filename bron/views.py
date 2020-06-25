from django.shortcuts import render, redirect
from django.http import HttpResponse
from .form import UserForm, HiddenForm
from .models import Booking, Merop
from django.core.mail import EmailMessage

from reportlab.pdfgen import canvas 
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.lib.pagesizes import letter

import time

import rsa
import os


(pubkey, privkey) = rsa.newkeys(512)
import qrcode

def CreateQr(qr_link):
	# Create qr code instance
	qr = qrcode.QRCode(
		version = 1,
		error_correction = qrcode.constants.ERROR_CORRECT_H,
		box_size = 2,
		border = 4,
	)

	# The data that you want to store
	data = qr_link

	# Add data
	qr.add_data(data)
	qr.make(fit=True)

	# Create an image from the QR Code instance
	img = qr.make_image()

	# Save it somewhere, change the extension as needed:
	# img.save("image.png")
	# img.save("image.bmp")
	# img.save("image.jpeg")
	img.save("media/img/qrkode.jpg")






def PDF(merop, name, booked):
	for i in range(len(booked)):
		packet = io.BytesIO()
		# create a new PDF with Reportlab
		MyFontObject = ttfonts.TTFont('Arial', 'arial.ttf')
		pdfmetrics.registerFont(MyFontObject)
		MyCanvas = canvas.Canvas(packet, pagesize=letter)
		MyCanvas.setFont("Arial", 20)
		MyCanvas.drawString(178, 69, str(merop))
		MyCanvas.drawString(167, 101, setMestaforPdf(''.join(str(booked[i]))))
		MyCanvas.drawString(139, 35, str(name))
		MyCanvas.drawImage('media/img/qrkode.jpg', 440, 30)
		MyCanvas.save()

		#move to the beginning of the StringIO buffer
		packet.seek(0)
		new_pdf = PdfFileReader(packet)
		# read your existing PDF
		existing_pdf = PdfFileReader(open(r"media/pdf/ticket.pdf", "rb"))
		output = PdfFileWriter()
		# add the "watermark" (which is the new pdf) on the existing page
		page = existing_pdf.getPage(0)
		page.mergePage(new_pdf.getPage(0))
		output.addPage(page)
		# finally, write "output" to a real file

		outputStream = open(r"media/pdf/destination"+str(i)+".pdf", "wb")
		output.write(outputStream)
		outputStream.close()

def Merop_list(request):
	zap = Merop.objects.in_bulk()
	kol = 0
	slov = {}
	for id in zap:
		kol+=1
		mass = []
		mass.append(zap[id].mero)
		mass.append(zap[id].place)
		mass.append(zap[id].date)
		mass.append(zap[id].image)
		#mass.append(zap[id].)
		slov[kol] = [mass]
	meropri = []
	places = []
	dates = []
	meropri_rsa = []
	images = []
	for i in slov.values():
		meropri.append(i[0][0])
		meropri_rsa.append(Crypto(i[0][0]))
	for i in slov.values():
		places.append(i[0][1])
	for i in slov.values():
		dates.append(i[0][2])
	for i in slov.values():
		images.append(i[0][3])
	return render(request, 'brony.html', {'meropri_rsa': meropri_rsa, 'places': places, 'dates': dates, 'slov': slov.values(), 'meropri': meropri, 'images': images})

def Crypto(some):
	some = rsa.encrypt(some.encode('utf-8'), pubkey)
	return str(some.hex())

def prov(request):
	place = request.GET.get("place")
	merop = request.GET.get("merop")
	email = request.GET.get("email")
	name = request.GET.get("name")
	return render(request, "prov.html", {"merop": merop, "place": place, "email": email, "name": name})	

def saver(request):
	merop = request.GET.get("merop")
	email = request.GET.get("email")
	places = request.GET.get("DataString")
	name = request.GET.get("name")
	return render(request, 'saver.html', {"email": email, "places": places, "merop": merop, "name": name})


def index(request):
	userform = UserForm()
	return render(request, 'index.html', {"form": userform})
	
def page(request):
	userform = UserForm()
	merop = request.GET.get("merop")
	date = request.GET.get("date")
	place = request.GET.get("place")
	return render(request, 'page.html', {"form": userform, "merop": (rsa.decrypt(bytes.fromhex(merop), privkey)).decode('utf-8'), "place": place, "date": date})

def contact(request):
	userform = UserForm()
	return render(request, 'contact.html', {"form": userform})
    
def query(request):
	if request.GET.get("Command")=="ConfirmBooking":
		if request.GET.get("password") == "хуй":
			email = request.GET.get("email")
			name = request.GET.get("name")
			merop = request.GET.get("mero")
			place = request.GET.get("place")
		
			obj_merop = Merop.objects.get(pk = merop)
		
			Booking.objects.filter(mero = obj_merop, places = place, email = email, username = name).update(conf = 1)
			return HttpResponse("каеф")
		else:
			return HttpResponse("ошибка")
	if request.GET.get("Command")=="LoadBooking":
		DataString = ""
		merop = request.GET.get("merop")
		
		obj_merop = Merop.objects.get(pk = merop)
		
		zap = Booking.objects.in_bulk()
		for id in zap:
			if zap[id].mero == obj_merop: 
				DataString += zap[id].places + ","
		return HttpResponse(DataString)
    
	if request.GET.get("Command") == "Filler":
		merop = request.GET.get("merop")
		Fill = Merop(mero = merop)
		Fill.save()
		return HttpResponse('good')
	
	if request.GET.get("Command")=="SaveBooking":
		booked = request.GET.get("DataString")
		booked = str(booked).split(',')
		place = request.GET.get("place")
		date = request.GET.get("date")
        
        ################################
        #Booking.objects.all().delete()#
        ################################
        
		email = request.GET.get("email")
		name = request.GET.get("name")
		merop = request.GET.get("mero")
		
		print(email, name, merop)
		
		obj_merop = Merop.objects.get(pk = merop)
		
		#проверка на 5 мест
		k = 0
		prov = Booking.objects.in_bulk()
		for id in prov:
			if prov[id].email == email and prov[id].mero == obj_merop:
				k += 1
				if k >= 2:
					return HttpResponse("места")
		
		for i in booked:
			if Booking.objects.filter(places = i, mero = obj_merop).count() != 0:
				return HttpResponse("ошибка")
				
		for i in booked:
			book = Booking(username = name, email = email, places = i, mero = obj_merop)
			book.save()

		zap = Booking.objects.in_bulk()
		
		link = "http://127.0.0.1:8000/cancel/?email=" + Crypto(email) +"&"+ "merop=" + Crypto(merop) +"&"+ "date=" + date +"&"+ "place=" + place

		data = '''
	<!DOCTYPE html>
		<html xmlns="http://www.w3.org/1999/xhtml">
		<head>
		<meta content="text/html; charset=utf-8" http-equiv="Content-Type">
		<meta content="width=device-width" name="viewport">

		<style>body {
		width: 100% !important; min-width: 100%; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; margin: 0; padding: 0;
		}
		.ExternalClass {
		width: 100%;
		}
		.ExternalClass {
		line-height: 100%;
		}
		#backgroundTable {
		margin: 0; padding: 0; width: 100% !important; line-height: 100% !important;
		}
		img {
		outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; width: auto; max-width: 100%; float: left; clear: both; display: block;
		}
		body {
		background-color: #ffffff; background-repeat: repeat; background-position: center top;
		}
		body {
		color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; padding: 0; margin: 0; text-align: left; line-height: 1.3;
		}
		a:hover {
		color: #2795b6;
		}
		a:active {
		color: #2795b6;
		}
		a:visited {
		color: #2ba6cb;
		}
		h1 a:active {
		color: #2ba6cb !important;
		}
		h2 a:active {
		color: #2ba6cb !important;
		}
		h3 a:active {
		color: #2ba6cb !important;
		}
		h4 a:active {
		color: #2ba6cb !important;
		}
		h5 a:active {
		color: #2ba6cb !important;
		}
		h6 a:active {
		color: #2ba6cb !important;
		}
		h1 a:visited {
		color: #2ba6cb !important;
		}
		h2 a:visited {
		color: #2ba6cb !important;
		}
		h3 a:visited {
		color: #2ba6cb !important;
		}
		h4 a:visited {
		color: #2ba6cb !important;
		}
		h5 a:visited {
		color: #2ba6cb !important;
		}
		h6 a:visited {
		color: #2ba6cb !important;
		}
		table.secondary:hover td {
		background: #d0d0d0 !important; color: #555555;
		}
		table.secondary:hover td a {
		color: #555555 !important;
		}
		table.secondary td a:visited {
		color: #555555 !important;
		}
		table.secondary:active td a {
		color: #555555 !important;
		}
		table.success:hover td {
		background: #457a1a !important;
		}
		table.alert:hover td {
		background: #970b0e !important;
		}
		body.outlook p {
		display: inline !important;
		}
		@media only screen and (min-width: 768px) {
		  table.container {
			width: 580px !important;
		  }
		}
		@media only screen and (max-width: 600px) {
		  .mail img {
			max-width: 100% !important; max-height: 100% !important; padding: 0 !important; width: auto !important; height: auto !important;
		  }
		  .mail .social img {
			width: inherit !important;
		  }
		  .mail img.normal {
			width: inherit !important;
		  }
		  .mail center {
			min-width: 0 !important;
		  }
		  .mail .container {
			width: 100% !important;
		  }
		  .mail .row {
			width: 100% !important; display: block !important;
		  }
		  .mail .wrapper {
			display: block !important; padding-right: 0 !important;
		  }
		  .mail .columns {
			table-layout: fixed !important; float: none !important; width: 100% !important; padding-right: 0px !important; padding-left: 0px !important; display: block !important;
		  }
		  .mail .column {
			table-layout: fixed !important; float: none !important; width: 100% !important; padding-right: 0px !important; padding-left: 0px !important; display: block !important;
		  }
		  .mail .wrapper.first .columns {
			display: table !important;
		  }
		  .mail .wrapper.first .column {
			display: table !important;
		  }
		  .mail table.columns > tbody > tr > td {
			width: 100% !important;
		  }
		  .mail table.column > tbody > tr > td {
			width: 100% !important;
		  }
		  .mail .columns td.one {
			width: 8.33333% !important;
		  }
		  .mail .column td.one {
			width: 8.33333% !important;
		  }
		  .mail .columns td.two {
			width: 16.66667% !important;
		  }
		  .mail .column td.two {
			width: 16.66667% !important;
		  }
		  .mail .columns td.three {
			width: 25% !important;
		  }
		  .mail .column td.three {
			width: 25% !important;
		  }
		  .mail .columns td.four {
			width: 33.33333% !important;
		  }
		  .mail .column td.four {
			width: 33.33333% !important;
		  }
		  .mail .columns td.five {
			width: 41.66667% !important;
		  }
		  .mail .column td.five {
			width: 41.66667% !important;
		  }
		  .mail .columns td.six {
			width: 50% !important;
		  }
		  .mail .column td.six {
			width: 50% !important;
		  }
		  .mail .columns td.seven {
			width: 58.33333% !important;
		  }
		  .mail .column td.seven {
			width: 58.33333% !important;
		  }
		  .mail .columns td.eight {
			width: 66.66667% !important;
		  }
		  .mail .column td.eight {
			width: 66.66667% !important;
		  }
		  .mail .columns td.nine {
			width: 75% !important;
		  }
		  .mail .column td.nine {
			width: 75% !important;
		  }
		  .mail .columns td.ten {
			width: 83.33333% !important;
		  }
		  .mail .column td.ten {
			width: 83.33333% !important;
		  }
		  .mail .columns td.eleven {
			width: 91.66667% !important;
		  }
		  .mail .column td.eleven {
			width: 91.66667% !important;
		  }
		  .mail .columns td.twelve {
			width: 100% !important;
		  }
		  .mail .column td.twelve {
			width: 100% !important;
		  }
		  .mail td.offset-by-one {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-two {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-three {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-four {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-five {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-six {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-seven {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-eight {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-nine {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-ten {
			padding-left: 0 !important;
		  }
		  .mail td.offset-by-eleven {
			padding-left: 0 !important;
		  }
		  .mail table.columns td.expander {
			width: 1px !important;
		  }
		  .mail .right-text-pad {
			padding-left: 10px !important;
		  }
		  .mail .text-pad-right {
			padding-left: 10px !important;
		  }
		  .mail .left-text-pad {
			padding-right: 10px !important;
		  }
		  .mail .text-pad-left {
			padding-right: 10px !important;
		  }
		  .mail .hide-for-small {
			display: none !important;
		  }
		  .mail .show-for-desktop {
			display: none !important;
		  }
		  .mail .show-for-small {
			display: block !important; width: auto !important; overflow: visible !important;
		  }
		  .mail .hide-for-desktop {
			display: block !important; width: auto !important; overflow: visible !important;
		  }
		}
		</style>
		</head>
		<body style="width: 100% !important; min-width: 100%; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; text-align: left; line-height: 1.3; background: #ffffff repeat center top; margin: 0; padding: 0;" bgcolor="#ffffff">
		<table class="mail" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; height: 100%; width: 100%; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; background: #ffffff repeat center top; margin: 0; padding: 0;" bgcolor="#ffffff">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td align="center" class="center" valign="top" style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: center; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0;">
		<center style="width: 100%; min-width: 580px;">
		<table class="container" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: inherit; max-width: 580px; margin: 0 auto; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0;" align="left" valign="top">
		<table class="row" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 100%; position: relative; display: block; background: #000000 repeat center top; padding: 0px;" bgcolor="#000000">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td class="wrapper first last" style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; position: relative; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 10px 0px 0px;" align="left" valign="top">
		<table class="twelve columns" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 580px; margin: 0 auto; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 100%; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0px 0px 10px;" align="left" valign="top">
		<table class="table-block" width="100%" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td class="" style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 100%; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; background: #000000 repeat center center; margin: 0; padding: 0px 10px;" align="left" bgcolor="#000000" valign="top">
		<p style="text-align: center; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0 0 10px; padding: 0;" data-mce-style="text-align: center;" align="center"><span style="font-size: 36pt; color: rgb(255, 255, 255); font-family: Roboto, Tahoma, sans-serif;" data-mce-style="font-size: 36pt; color: #ffffff; font-family: Roboto, Tahoma, sans-serif;"><strong>PKCINEMA</strong></span></p>
		</td>
		</tr>
		</tbody>
		</table>


		</td>
		<td class="expander" style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 100%; visibility: hidden; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0;" align="left" valign="top"></td>
		</tr>
		</tbody>
		</table>
		</td>

		</tr>
		</tbody>
		</table>
		</td>
		</tr>
		</tbody>
		</table>
		<table class="container" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: inherit; max-width: 580px; margin: 0 auto; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0;" align="left" valign="top">
		<table class="row" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 100%; position: relative; display: block; background: #000000 repeat center top; padding: 0px;" bgcolor="#000000">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td class="wrapper first last" style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; position: relative; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 10px 0px 0px;" align="left" valign="top">
		<table class="twelve columns" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 580px; margin: 0 auto; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 100%; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0px 0px 10px;" align="left" valign="top">
		<table class="table-block" width="100%" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td class="" style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 100%; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; background: #000000 repeat center center; margin: 0; padding: 0px 10px;" align="left" bgcolor="#000000" valign="top">
		<p style="text-align: center; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0 0 10px; padding: 0;" data-mce-style="text-align: center;" align="center"><span style="font-size: 26pt;" data-mce-style="font-size: 26pt;"><span color="#ffffff" data-mce-style="color: #ffffff;" style="color: #ffffff;">Здравствуйте ''' + str(name) + '''!</span></span></p>
		<p style="text-align: center; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0 0 10px; padding: 0;" data-mce-style="text-align: center;" align="center"><span style="font-size: 16pt;" data-mce-style="font-size: 16pt;"><span color="#ffffff" data-mce-style="color: #ffffff;" style="color: #ffffff;">Вы успешно забронировали билеты)</span></span></p>
		<p style="text-align: center; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0 0 10px; padding: 0;" data-mce-style="text-align: center;" align="center"><span color="#ffffff" data-mce-style="color: #ffffff;" style="color: #ffffff;"><span style="font-size: 21.3333px;" data-mce-style="font-size: 21.3333px;">Ваши места: ''' + setMestaforEmail('; '.join(booked)) + '''</span></span></p>
		<p style="text-align: center; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0 0 10px; padding: 0;" data-mce-style="text-align: center;" align="center"><span color="#ffffff" data-mce-style="color: #ffffff;" style="color: #ffffff;"><span style="font-size: 21.3333px;" data-mce-style="font-size: 21.3333px;">Мероприятие: ''' + str(merop) + '''</span></span></p>
		<p style="text-align: center; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0 0 10px; padding: 0;" data-mce-style="text-align: center;" align="center"><br></p>
		</td>
		</tr>
		</tbody>
		</table>

		<table class="table-full" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; background: transparent repeat center center; padding: 0;" width="100%" bgcolor="transparent">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td height="%" style="width: 22% !important; height: % !important; word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; background: repeat center top; margin: 0; padding: 0;" width="22%" align="left" valign="top"></td>
		<td height="%" style="width: 57% !important; height: % !important; word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; background: repeat center top; margin: 0; padding: 0;" width="57%" align="left" valign="top">
		<table class="button" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 100%; overflow: hidden; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: center; width: auto !important; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: initial !important; display: block; margin: 0; padding: 0px;" align="center" valign="top">
		<!--[if mso]>
		<p style='line-height:0;margin:0;'>&nbsp;</p>
		<v:roundrect arcsize='5%' fill='t' fillcolor='#bd3535' href="''' + str(link) + '''" stroke='f' strokecolor='' style='v-text-anchor:middle;width:331px;height:55px;' xmlns:v='urn:schemas-microsoft-com:vml' xmlns:w='urn:schemas-microsoft-com:office:word'>
		<w:anchorlock>
		<center style='color: #FFF; font-family:sans-serif; font-size:13px; font-weight:bold; mso-line-height-rule:exactly; mso-text-raise:4px'>
		Отменить Бронирование
		</center>
		</w:anchorlock>
		</v:roundrect>
		<![endif]-->
		<!--[if !mso]>
		<!---->
		<a href="''' + str(link) + '''" style="line-height: 20px; font-size: 20px !important; width: auto; display: block; border-radius: 5px; -webkit-border-radius: 5px; -moz-border-radius: 5px; color: #ffffff; text-decoration: none; font-weight: bold; font-family: Helvetica, Arial, sans-serif; height: 100%; background: #bd3535 repeat center center; padding: 15px 10px;">Отменить Бронирование</a>
		<!-- <![endif]-->
		<!--[endif]---->
		</td>
		</tr>
		</tbody>
		</table>

		</td>
		<td height="%" style="width: 21% !important; height: % !important; word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; background: repeat center top; margin: 0; padding: 0;" width="21%" align="left" valign="top"></td>
		</tr>
		</tbody>
		</table>


		</td>
		<td class="expander" style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 100%; visibility: hidden; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0;" align="left" valign="top"></td>
		</tr>
		</tbody>
		</table>
		</td>

		</tr>
		</tbody>
		</table>
		</td>
		</tr>
		</tbody>
		</table>

		<table class="container" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: inherit; max-width: 580px; margin: 0 auto; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0;" align="left" valign="top">
		<table class="row" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 100%; position: relative; display: block; background: transparent repeat center top; padding: 0px;" bgcolor="transparent">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td class="wrapper first last" style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; position: relative; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 10px 0px 0px;" align="left" valign="top">
		<table class="twelve columns" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 580px; margin: 0 auto; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 100%; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0px 0px 10px;" align="left" valign="top">
		<table width="100%" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; padding: 0;">
		<tbody>
		<tr style="vertical-align: top; text-align: left; padding: 0;" align="left">
		<td class="center" style="text-align: center; word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; width: 100%; font-weight: normal; line-height: 1.3; background: transparent repeat center center; margin: 0; padding: 0px;" align="center" bgcolor="transparent" valign="top">
		</td>
		</tr>
		</tbody>
		</table>


		</td>
		<td class="expander" style="word-break: break-word; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 100%; visibility: hidden; color: #222222; font-family: Helvetica, Arial, sans-serif; font-weight: normal; font-size: 14px; line-height: 1.3; margin: 0; padding: 0;" align="left" valign="top"></td>
		</tr>
		</tbody>
		</table>
		</td>

		</tr>
		</tbody>
		</table>
		</td>
		</tr>
		</tbody>
		</table>

		</center>
		</td>
		</tr>
		</tbody>
		</table>




			</body>
		</html>
'''
		email1 = EmailMessage('Бронирование', data, to=[str(email)])
		email1.content_subtype = "html"
		
		for i in range(len(booked)):
			qr_link = "http://127.0.0.1:8000/prov/?email=" + email +"&"+ "merop=" + merop +"&"+ "name=" + name +"&"+ "place=" + booked[i]
			print(qr_link)
			PDF(merop, name, booked)
			CreateQr(qr_link)
		
			email1.attach_file(r'media/pdf/destination'+str(i)+'.pdf')
		email1.send()
        
		for id in zap: 
			print(zap[id].username, zap[id].email, zap[id].places, zap[id].mero)

		return HttpResponse("бронь")
    
	if request.GET.get("Command")=="DeleteBooking":
		Booking.objects.all().delete()
		return HttpResponse("Все места удалены, милорд")

def change(request):
		if request.GET.get("Command")=="LoadBooking":
			DataString = ""
			merop = request.GET.get("merop")
			email = request.GET.get("email")
			zap = Booking.objects.in_bulk()
			
			print(merop, email)
			
			obj_merop = Merop.objects.get(pk = merop)
			
			for id in zap:
				if zap[id].email == email and zap[id].mero == obj_merop: 
					DataString += zap[id].places + ","
			return HttpResponse(DataString)
            
		if request.GET.get("Command")=="CancelBooking":
			booked = request.GET.get("DataString")
			booked = str(booked).split(',')
			if booked == "":
				return HttpResponse('ошибка')
			
			email = request.GET.get("email")
			merop = request.GET.get("mero")
			
			obj_merop = Merop.objects.get(pk = merop)
			
			data = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
	<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>Demystifying Email Design</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
	<body>
	<style>
	* {box-sizing: border-box;}
	body {background: #FFF2E3;}
	.wedding {
	  position: relative;
	  max-width: 350px;
	  margin: 50px auto 0;
	  text-align: center;
	}
	.form-inner:before {
	  display: inline-block;
	  margin-top: -45px;
	  content: url(https://html5book.ru/wp-content/uploads/2017/05/form-flower.png);
	}
	.form-inner {
	  padding: 0 40px 10px;
	  margin-top: 45px;
	  background: #ffffff;
	  border-radius: 2px;
	  box-shadow: 0 0 6px 1px rgba(0,0,0,.1);
	}
	.form-inner h2 {
	  font-weight: 300;
	  font-size: 20px;
	  text-transform: uppercase;
	  font-family: 'Cormorant Garamond', serif;
	}
	.form-content {
	  position: relative;
	  margin: 30px -40px 0 -40px;
	  padding: 10px 40px 0 40px;
	  background: #FFF8F3;
	}
	.form-content:before {
	  content: "";
	  position: absolute;
	  top: -4px;
	  right: 0;
	  left: 0;
	  height: 2px;
	  border-top: 1px solid #DDDDDD;
	  border-bottom: 1px solid #DDDDDD;
	}
	.form-content h3 {
	  font-family: 'Marck Script', cursive;
	  font-size: 22px;
	  color: #898989;
	  font-weight: normal;
	}
	.form-content input,
	.form-content select {
	  height: 38px;
	  line-height: 38px;
	  padding: 0 10px;
	  background: #ffffff;
	  border: 1px solid #DDDDDD;
	  font-size: 20px;
	  font-family: 'Cormorant Garamond', serif;
	  color: #808080;
	  outline: none;
	}
	.form-content input {width: 100%;}
	.form-content input:focus,
	.form-content select:focus {border-color: #C44D58;}
	.form-content input[type="submit"] {
	  margin: 20px 0;
	  padding: 0 10px;
	  background: #FF6B6B;
	  color: #ffffff;   
	  font-size: 18px;
	  text-transform: uppercase;
	  border-width: 0;
	  border-radius: 20px;
	  cursor: pointer;
	  transition: .2s linear}
	.form-content input[type="submit"]:hover {background: #C44D58;}
	</style>
	<form class="wedding">
	  <div class="form-inner">
		<h2>Вы успешно отменили бронирование<br><h2>
		</div>
	  </div>
	</form>
	</body>
	</head>
</html>'''
		
		email1 = EmailMessage('Отмена Бронирования', data, to=[str(email)])
		email1.content_subtype = "html"
		email1.send()
			
		for i in booked:
			Booking.objects.filter(places = i, mero = obj_merop).delete()
		return HttpResponse("успех")

def cancel(request):
		hidform = HiddenForm()
		email = request.GET.get("email")
		merop = request.GET.get("merop")
		place = request.GET.get("place")
		date = request.GET.get("date")
		
		return render(request, "cancel.html", context={"email" : (rsa.decrypt(bytes.fromhex(email), privkey)).decode('utf-8'),"merop" : (rsa.decrypt(bytes.fromhex(merop), privkey)).decode('utf-8'), "form": hidform, "place": place, "date": date})
def setMestaforEmail(mesta):
		mesta = mesta.replace('s', 'место ')
		mesta = mesta.replace('_', ',')
		mesta = mesta.replace('r', ' ряд \n')
		return mesta
		
def setMestaforPdf(mesta):
		mesta = mesta.replace('s', 'место ')
		mesta = mesta.replace('_', ',')
		mesta = mesta.replace('r', ' ряд ')
		return mesta
        
def mail(request):
	if request.GET.get("Command")=="GetEmail":
		email = request.GET.get("email")
		usr = request.GET.get("usr")
		message = request.GET.get("message")
		data = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Demystifying Email Design</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<body>
<style>
* {box-sizing: border-box;}
body {background: #FFF2E3;}
.wedding {
  position: relative;
  max-width: 350px;
  margin: 50px auto 0;
  text-align: center;
}
.form-inner:before {
  display: inline-block;
  margin-top: -45px;
  content: url(https://html5book.ru/wp-content/uploads/2017/05/form-flower.png);
}
.form-inner {
  padding: 0 40px 10px;
  margin-top: 45px;
  background: #ffffff;
  border-radius: 2px;
  box-shadow: 0 0 6px 1px rgba(0,0,0,.1);
}
.form-inner h2 {
  font-weight: 300;
  font-size: 20px;
  text-transform: uppercase;
  font-family: 'Cormorant Garamond', serif;
}
.form-content {
  position: relative;
  margin: 30px -40px 0 -40px;
  padding: 10px 40px 0 40px;
  background: #FFF8F3;
}
.form-content:before {
  content: "";
  position: absolute;
  top: -4px;
  right: 0;
  left: 0;
  height: 2px;
  border-top: 1px solid #DDDDDD;
  border-bottom: 1px solid #DDDDDD;
}
.form-content h3 {
  font-family: 'Marck Script', cursive;
  font-size: 22px;
  color: #898989;
  font-weight: normal;
}
.form-content input,
.form-content select {
  height: 38px;
  line-height: 38px;
  padding: 0 10px;
  background: #ffffff;
  border: 1px solid #DDDDDD;
  font-size: 20px;
  font-family: 'Cormorant Garamond', serif;
  color: #808080;
  outline: none;
}
.form-content input {width: 100%;}
.form-content input:focus,
.form-content select:focus {border-color: #C44D58;}
.form-content input[type="submit"] {
  margin: 20px 0;
  padding: 0 10px;
  background: #FF6B6B;
  color: #ffffff;   
  font-size: 18px;
  text-transform: uppercase;
  border-width: 0;
  border-radius: 20px;
  cursor: pointer;
  transition: .2s linear}
.form-content input[type="submit"]:hover {background: #C44D58;}
</style>
<form class="wedding">
  <div class="form-inner">
    <h2>От пользователей<br><h2>
    <div class="form-content">
      <h3>Почта отправителя: ''' + str(email) + '''</h3>
      <h3>Имя отправителя: ''' + str(usr) + '''</h3>
	  <h3>Его текст: ''' + str(message) + '''</h3> 
    </div>
  </div>
</form>
</body>
</head>
</html>'''
		email1 = EmailMessage('Служебка', data, to=['pkcinemaru@gmail.com'])
		email1.content_subtype = "html"
		email1.send()
		return HttpResponse("Fu")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
