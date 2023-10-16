from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import openai
import os
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
import json
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test


def is_dosen(user):
    return user.role == 'Dosen'
def is_mahasiswa(user):
    return user.role == 'Mahasiswa'
    
def create_room(request):
    if request.method == 'POST':
        form = DiscussionRoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.author = request.user
            room.save()

            # Check if a cover image was uploaded
            if 'cover' in request.FILES:
                room.cover = request.FILES['cover']
                room.save()

            Participant.objects.create(user=request.user, room=room, is_creator=True)
            messages.success(request, 'Room created successfully.')
            return redirect('room_detail', room_id=room.id)
    else:
        form = DiscussionRoomForm()
    return render(request, 'create_room.html', {'form': form})

@user_passes_test(is_dosen)
def create_room_d(request):
    if request.method == 'POST':
        form = DiscussionRoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.author = request.user
            room.save()

            # Check if a cover image was uploaded
            if 'cover' in request.FILES:
                room.cover = request.FILES['cover']
                room.save()

            Participant.objects.create(user=request.user, room=room, is_creator=True)
            messages.success(request, 'Room created successfully.')
            return redirect('room_detail_d', room_id=room.id)
    else:
        form = DiscussionRoomForm()
    return render(request, 'create_room_d.html', {'form': form})

def check_membership(user, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)
    participant = Participant.objects.filter(user=user, room=room).first()
    return participant is not None

def room_detail(request, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)
    
    if not check_membership(request.user, room_id):
        return redirect('join_room', room_id=room_id)
    
    participants = Participant.objects.filter(room=room)
    messages = Message.objects.filter(room=room)
    message_form = MessageForm()

    return render(request, 'room_detail.html', {
        'room': room,
        'participants': participants,
        'messages': messages,
        'message_form': message_form,
    })

@user_passes_test(is_dosen)
def room_detail_d(request, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)
    
    if not check_membership(request.user, room_id):
        return redirect('join_room_d', room_id=room_id)
    
    participants = Participant.objects.filter(room=room)
    messages = Message.objects.filter(room=room)
    message_form = MessageForm()

    return render(request, 'room_detail_d.html', {
        'room': room,
        'participants': participants,
        'messages': messages,
        'message_form': message_form,
    })




def get_file_type(file_url):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    video_extensions = ['.mp4', '.webm', '.ogg']

    ext = os.path.splitext(file_url)[1].lower()

    if ext in image_extensions:
        return 'image'
    elif ext in video_extensions:
        return 'video'
    else:
        return 'other'
    
    

def chat_room(request, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)

    if not check_membership(request.user, room_id):
        return redirect('join_room', room_id=room_id)

    messages = Message.objects.filter(room=room)
    message_form = MessageForm()

    for message in messages:
        if message.file and message.file.url:
            message.file_type = get_file_type(message.file.url)
        else:
            message.file_type = None

    return render(request, 'chat_room.html', {
        'room': room,
        'messages': messages,
        'message_form': message_form,
    })

@user_passes_test(is_dosen)
def chat_room_d(request, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)

    if not check_membership(request.user, room_id):
        return redirect('join_room_d', room_id=room_id)

    messages = Message.objects.filter(room=room)
    message_form = MessageForm()

    for message in messages:
        if message.file and message.file.url:
            message.file_type = get_file_type(message.file.url)
        else:
            message.file_type = None

    return render(request, 'chat_room_d.html', {
        'room': room,
        'messages': messages,
        'message_form': message_form,
    })

def room_list(request):
    rooms = DiscussionRoom.objects.all()
    return render(request, 'room_list.html', {'rooms': rooms})

@user_passes_test(is_dosen)
def room_list_d(request):
    if 'q' in request.GET:
        query = request.GET.get('q')
        rooms = DiscussionRoom.objects.filter(Q(name__icontains=query) | Q(author__username__icontains=query))
    else:
        rooms = DiscussionRoom.objects.all()

    return render(request, 'room_list_d.html', {'rooms': rooms})

@user_passes_test(is_dosen)
def dsn_rooms(request):
    user = request.user
    query = request.GET.get('q', '')  # Ambil query pencarian

    # Mengambil ruangan yang diikuti oleh pengguna dan sesuai dengan query pencarian
    rooms_joined = DiscussionRoom.objects.filter(Q(participant__user=user) & (Q(name__icontains=query) | Q(author__username__icontains=query)))

    return render(request, 'dsn_rooms.html', {'rooms_joined': rooms_joined, 'query': query})

def mhs_rooms(request):
    user = request.user
    query = request.GET.get('q', '')  # Ambil query pencarian

    # Mengambil ruangan yang diikuti oleh pengguna dan sesuai dengan query pencarian
    rooms_joined = DiscussionRoom.objects.filter(Q(participant__user=user) & (Q(name__icontains=query) | Q(author__username__icontains=query)))

    return render(request, 'mhs_rooms.html', {'rooms_joined': rooms_joined, 'query': query})

def join_room(request, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)
    participant = Participant.objects.filter(user=request.user, room=room).first()
    if participant or room.author == request.user:
        return redirect('room_detail', room_id=room_id)
    
    if request.method == 'POST':
        code = request.POST.get('code', '')
        if code == room.code:
            Participant.objects.create(user=request.user, room=room, is_creator=False)
            messages.success(request, 'You have joined the room.')
            return redirect('room_detail', room_id=room_id)
        else:
            messages.error(request, 'Invalid code. Please try again.')
    return render(request, 'join_room.html', {'room': room})

@user_passes_test(is_dosen)
def join_room_d(request, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)
    participant = Participant.objects.filter(user=request.user, room=room).first()
    if participant or room.author == request.user:
        return redirect('room_detail_d', room_id=room_id)
    
    if request.method == 'POST':
        code = request.POST.get('code', '')
        if code == room.code:
            Participant.objects.create(user=request.user, room=room, is_creator=False)
            messages.success(request, 'You have joined the room.')
            return redirect('room_detail_d', room_id=room_id)
        else:
            messages.error(request, 'Invalid code. Please try again.')
    return render(request, 'join_room_d.html', {'room': room})

def generate_bot_response(user_message, conversation_history):
    openai.api_key = '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'  # Ganti dengan API key Anda
    model_name = "gpt-3.5-turbo-16k"
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=conversation_history,
    )
    chatbot_response = response['choices'][0]['message']['content']
    return chatbot_response

# Fungsi untuk menangani pesan yang diawali dengan '/bot'
def handle_bot_message(message_content):
    if message_content.startswith('/bot'):
        user_message = message_content.lstrip('/bot').strip()
        if user_message:
            # Generate respons menggunakan GPT-3.5 Turbo
            conversation_history = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                                    {'role': 'user', 'content': user_message}]
            bot_response = generate_bot_response(user_message, conversation_history)
            return bot_response
    return None  # Jika pesan bukan dimulai dengan '/bot'

def send_message(request, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)

    if not check_membership(request.user, room_id):
        return redirect('join_room', room_id=room_id)

    if request.method == 'POST':
        message_form = MessageForm(request.POST, request.FILES)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.room = room
            message.user = request.user
            message_content = message_form.cleaned_data['content']

            # Handle pesan yang diawali dengan '/bot'
            bot_response = handle_bot_message(message_content)
            if bot_response:
                message_content += f"\n\nBot: {bot_response}"

            message.content = message_content
            file = request.FILES.get('file')
            if file:
                # Save the file to the default storage (media)
                file_name = default_storage.save(file.name, file)
                message.file = file_name

            message.save()
            messages.success(request, 'Message sent successfully.')

            # Redirect to the same chat room after posting a message
            return redirect('chat_room', room_id=room_id)
         
@user_passes_test(is_dosen)
def send_message_d(request, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)

    if not check_membership(request.user, room_id):
        return redirect('join_room_d', room_id=room_id)

    if request.method == 'POST':
        message_form = MessageForm(request.POST, request.FILES)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.room = room
            message.user = request.user
            message_content = message_form.cleaned_data['content']

            # Handle pesan yang diawali dengan '/bot'
            bot_response = handle_bot_message(message_content)
            if bot_response:
                message_content += f"\n\nBot: {bot_response}"

            message.content = message_content
            file = request.FILES.get('file')
            if file:
                # Save the file to the default storage (media)
                file_name = default_storage.save(file.name, file)
                message.file = file_name

            message.save()
            messages.success(request, 'Message sent successfully.')

            # Redirect to the same chat room after posting a message
            return redirect('chat_room_d', room_id=room_id)

def leave_room(request, room_id):
    room = get_object_or_404(DiscussionRoom, id=room_id)
    participant = get_object_or_404(Participant, user=request.user, room=room)
    if participant.is_creator:
        messages.error(request, 'The creator cannot leave the group.')
    else:
        participant.delete()
        messages.success(request, 'You have left the group.')
    return redirect('room_detail', room_id=room_id)

