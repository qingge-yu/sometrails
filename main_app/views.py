from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Hike, Review, Photo
from .forms import ReviewForm
import uuid
import boto3
import os


def auth(request):
    return render(request, 'auth.html')


def hikes_index(request):
    hikes = Hike.objects.all()
    return render(request, 'hikes/index.html', {'hikes': hikes})


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


class HikeCreate(LoginRequiredMixin, CreateView):
    model = Hike
    fields = ['name', 'location', 'description', 'difficulty']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    success_url = '/hikes/'

class HikeDetail(DetailView):
    model = Hike
    def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['reviews'] = Review.objects.filter(hike=self.object.id)
      context['review_form'] = ReviewForm()
      return context

class HikeUpdate(LoginRequiredMixin, UpdateView):
    model = Hike
    fields = ['location', 'description', 'difficulty']
    def get_success_url(self):
        return f'/hikes/{self.object.id}'


class HikeDelete(LoginRequiredMixin, DeleteView):
    model = Hike
    success_url= '/hikes/'

class ReviewDelete(LoginRequiredMixin, DeleteView):
    model = Review
    def get_success_url(self):
        return f'/hikes/{self.object.hike_id}'

def add_review(request, hike_id):
  form = ReviewForm(request.POST)
  if form.is_valid():
    new_review = form.save(commit=False)
    new_review.hike_id = hike_id
    new_review.user_id = request.user.id
    new_review.save()
  return redirect(f'/hikes/{hike_id}', hike_id=hike_id)

def add_photo(request, hike_id):
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            Photo.objects.create(url=url, hike_id=hike_id)
        except Exception as e:
            print('An error occurred uploading file to S3')
            print(e)
    return redirect('detail', hike_id=hike_id)