# views.py
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import ContactForm

def submit_contact_form(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            print("the form was valid")
            send_mail("Feedback for PGx", "Message content", "khucnam@yahoo.com", ["nguyentrinhtrungduong@gmail.com"] )
            return redirect("submit_contact_form")
    else:
        form = ContactForm()
        print("method is not a post")
    return render(request, "home/questions_to_pgx.html", {"form": form})