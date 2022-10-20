from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
import pandas as pd
from cryptography.fernet import Fernet
import numpy as np

# Create your views here.
def HomeLoginPage(req):
    return render(req, "loginPage.html")

def checkLoginCredentials(req):
    fernet = Fernet(open("fernet_key","rb").read())

    email = req.POST['email']
    password = req.POST['password']

    df = None
    if os.path.exists("user_details.csv"):
        df = pd.read_csv("user_details.csv", low_memory=False)
        # df['last_name'] = df['last_name'].fillna("")
    if df is None:
        return render(req, "loginPage.html", {"message": "No User Found"})

    flag = (df['email'].astype(str)==email)
    if df[flag].shape[0]>0:
        correct_pass = df[flag]['password'].astype(str).iloc[0]
        if password == fernet.decrypt(correct_pass.encode()).decode():
            return render(req, "SuccessFullLogin.html", {"name": df[flag]['first_name'].astype(str).iloc[0]})
        else:
            return render(req, "loginPage.html", {"message": "Wrong Password"})

    return render(req, "loginPage.html", {"message": "Seems like you're a New User, Please Register !!!"})

def RegistrationPage(req):
    return render(req, "Registration.html")

def RegisterUser(req):
    first_name = req.POST['first_name']
    last_name = req.POST['last_name']
    email = req.POST['email']
    ph_no = req.POST['ph_no']
    password = req.POST['password']
    confirm_password = req.POST['confirm_password']

    df = None
    if os.path.exists("user_details.csv"):
        df = pd.read_csv("user_details.csv", low_memory=False)

    if df is not None:
        if df[df['email'].astype(str)==email].shape[0] > 0:
            return render(req, "loginPage.html", {"message": "Email ID already registered, Please Try to Login"})
        if df[df['ph_no'].astype(str)==ph_no].shape[0] > 0:
            return render(req, "Registration.html", {"message": "Phone Number already taken, Please try with another Phone Number"})

    if password != confirm_password:
        return render(req, "Registration.html", {"message": "Passwords Don't Match"})

    fernet = Fernet(open("fernet_key","rb").read())
    
    user_data = {}
    user_data['first_name'] = [first_name]
    user_data['last_name'] = [last_name]
    user_data['email'] = [email]
    user_data['ph_no'] = [ph_no]
    user_data['password'] = [fernet.encrypt(password.encode()).decode()] ## Encrypting Password

    if df is None:
        df = pd.DataFrame(user_data)
        df.to_csv("user_details.csv", index=False)
    else:
        df = df.append(pd.DataFrame(user_data))
        df.to_csv("user_details.csv", index=False)
    return render(req, "loginPage.html", {"message": "User Successfully Registered"})

def logout(req):
    return render(req, "loginPage.html", {"message":"User Successfully Logged Out"})

def show_registered_users(req):
    if not os.path.exists("user_details.csv"):
        return render(req, 'SuccessFullLogin.html', {"message": "No Registered Users Found"})
    df = pd.read_csv("user_details.csv", low_memory=False, usecols=['first_name','last_name','email','ph_no'])
    df.index = df.index+1
    df.replace(np.nan, "", inplace=True)
    return HttpResponse(df.to_html())