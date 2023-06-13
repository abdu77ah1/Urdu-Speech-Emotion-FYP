from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from urllib.parse import urlencode
import librosa
import numpy as np
from keras.models import load_model

model = load_model('./models/1_best_model.h5')

def home(request):
    return render(request, 'users/home1.html')

def predict(request):
    return render(request, 'users/home.html')

def predictEmotion(request):
    if request.method == 'POST':
        fileObj=request.FILES['filePath']
        fs=FileSystemStorage()
        filePathName=fs.save(fileObj.name,fileObj)
        #filePathName=fs.url(filePathName)
        filePathName = fs.path(filePathName)  # Get the actual file path
        y, sr = librosa.load(filePathName, duration=3, offset=0.5)
        mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
        X_test = np.expand_dims(mfcc, axis=0)
        X_test = np.expand_dims(X_test, axis=2)
        # make a prediction
        predictions = model.predict(X_test)
        print(predictions)
        emotion_labels = ['neutral', 'happiness', 'sadness', 'surprise', 'anger', 'fearful', 'disgust', 'boredom']
        predicted_label = emotion_labels[np.argmax(predictions)]
        context={
            'predictedLabel':predicted_label
        }
        return redirect(reverse('users-predicts') + f'?{urlencode(context)}')
    
    

class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})
