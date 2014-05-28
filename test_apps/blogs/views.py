from django.shortcuts import render
from django.http import HttpResponse
from test_apps.utils import render_template
from django.contrib.auth.decorators import login_required

def get_preview_context():
    return {
        'app_objects': []
    }

@login_required
def index(request):
    return render_template(request, 'blogs/index.html')
