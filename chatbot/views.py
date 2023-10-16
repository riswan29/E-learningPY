from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse 
from django.contrib.auth.decorators import login_required
from .models import *
import openai
import markdown
from django.utils.html import escape
from django.shortcuts import render, get_object_or_404
import uuid
from app.models import *
import datetime
from django.utils.safestring import mark_safe
import pandas as pd
import io
import csv


openai.api_key = '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'

def sesi(request):
    new_uuid = uuid.uuid4()
    new_sesi = SesiChat.objects.create(uuid=new_uuid, user=request.user)
    
    sesi_list = SesiChat.objects.filter(user=request.user)
    sesi_last = SesiChat.objects.last()
    return render(request, 'sesi.html', {'sesi_list': sesi_list, 'sesi_last': sesi_last, 'new_sesi': new_sesi})


def generate_transcript_excel(assignments):
    # Create a DataFrame from the assignments
    data = {
        'Submission Author': [assignment.submission.author.username for assignment in assignments],
        'Assignment Title': [assignment.submission.assignment.title for assignment in assignments],
        'Grade': [assignment.grade for assignment in assignments],
        'Feedback': [assignment.feedback for assignment in assignments],
    }
    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Transcript', index=False)

    buffer.seek(0)
    return buffer

@login_required
def chatbot_view_d(request, uuid):
    sesi_last = SesiChat.objects.last()
    sesi_list = SesiChat.objects.filter(user=request.user).order_by('-id')

    sesi = get_object_or_404(SesiChat, uuid=uuid)
    conversations = Conversation.objects.filter(sesi=sesi, user=request.user)

    chatbot_response = ''

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')

        current_user = request.user

        conversation_history = [
            {"role": "system", "content": "Anda adalah asisten yang membantu."}
        ]

        for conversation in conversations:
            conversation_history.append({"role": "user", "content": conversation.user_message})
            conversation_history.append({"role": "assistant", "content": conversation.chatbot_response})

        conversation_history.append({"role": "user", "content": user_input})

        # language = detect_programming_language(user_input)

        # if language:
        #     chatbot_response = f'<pre><code>{chatbot_response}</code></pre>'

        if user_input == "/jadwalku_hari_ini":
            if current_user.role == CustomUser.Dosen:
                today = datetime.datetime.today().strftime('%A').upper()

                jadwal_hari_ini = JadwalMengajar.objects.filter(dosen=current_user, hari=today).first()

                if jadwal_hari_ini:
                    chatbot_response = f"MK : {jadwal_hari_ini.mata_kuliah}, JAM MULAI : {jadwal_hari_ini.jam_mulai.strftime('%H:%M')}, Semester : {jadwal_hari_ini.semester}, Jurusan : {jadwal_hari_ini.jurusan}"
                else:
                    chatbot_response = "Tidak ada jadwal untuk hari ini."
                    
        elif user_input == "/jadwalku" and current_user.role == CustomUser.Dosen:
            jadwal_dosen = JadwalMengajar.objects.filter(dosen=current_user)
            if jadwal_dosen:
                chatbot_response = "\n".join(
                    [f"MK : {jadwal.mata_kuliah}, JAM MULAI : {jadwal.jam_mulai.strftime('%H:%M')}, Semester : {jadwal.semester}, Jurusan : {jadwal.jurusan}" for jadwal in jadwal_dosen]
                )
            else:
                chatbot_response = "Anda tidak memiliki jadwal."
        elif user_input == "/jadwalku":
            if current_user.role == CustomUser.Mahasiswa:
                today = datetime.datetime.today().strftime('%A').upper()

                if current_user.semester and current_user.department:
                    jadwal_hari_ini = JadwalMengajar.objects.filter(semester=current_user.semester, jurusan=current_user.department, hari=today)

                    if jadwal_hari_ini:
                        chatbot_response = "\n".join(
                            [f"MK : {jadwal.mata_kuliah}, JAM MULAI : {jadwal.jam_mulai.strftime('%H:%M')}, Semester : {jadwal.semester}, Jurusan : {jadwal.jurusan}" for jadwal in jadwal_hari_ini]
                        )
                    else:
                        chatbot_response = "Belum ada jadwal untuk hari ini."
                else:
                    chatbot_response = "Silakan hubungi admin untuk mengisi jurusan dan semester Anda."
    
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=conversation_history,
            )

            chatbot_response = response['choices'][0]['message']['content']

        escaped_chatbot_response = escape(chatbot_response)
        formatted_chatbot_response = f'<code class="language-python">{escaped_chatbot_response}</code>'

        conversation = Conversation(user=current_user, user_message=user_input, chatbot_response=chatbot_response, sesi=sesi)
        conversation.save()

        return JsonResponse({'user_input': user_input, 'chatbot_response': formatted_chatbot_response})

    return render(request, 'chatbot_dsn.html', {
        'chatbot_response': chatbot_response,
        'conversations': conversations,
        'sesi': sesi,
        'sesi_last': sesi_last,
        'sesi_list': sesi_list,
    })

@login_required
def chatbot_view_m(request, uuid):
    sesi_last = SesiChat.objects.last()
    sesi_list = SesiChat.objects.filter(user=request.user).order_by('-id')

    sesi = get_object_or_404(SesiChat, uuid=uuid)
    conversations = Conversation.objects.filter(sesi=sesi, user=request.user)

    chatbot_response = ''

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')

        current_user = request.user

        conversation_history = [
            {"role": "system", "content": "Anda adalah asisten yang membantu."}
        ]

        for conversation in conversations:
            conversation_history.append({"role": "user", "content": conversation.user_message})
            conversation_history.append({"role": "assistant", "content": conversation.chatbot_response})

        conversation_history.append({"role": "user", "content": user_input})

        if user_input.startswith("/jadwal_dosen "):
            # Mengambil username dosen dari input pengguna
            username_dosen = user_input.split("/jadwal_dosen ")[1]

            # Cari dosen berdasarkan username
            try:
                dosen = CustomUser.objects.get(username=username_dosen, role=CustomUser.Dosen)
                # Ambil jadwal dosen untuk hari ini
                today = datetime.datetime.today().strftime('%A').upper()
                hari_indonesia = {
                    'MONDAY': 'MONDAY',
                    'TUESDAY': 'TUESDAY',
                    'WEDNESDAY': 'WEDNESDAY',
                    'THURSDAY': 'THURSDAY',
                    'FRIDAY': 'FRIDAY',
                    'SATURDAY': 'SATURDAY',
                    'SUNDAY': 'SUNDAY'
                }
                today_indonesia = hari_indonesia.get(today, today)
                jadwal_dosen_hari_ini = JadwalMengajar.objects.filter(dosen=dosen, hari=today_indonesia)

                if jadwal_dosen_hari_ini:
                    chatbot_response = "\n".join(
                        [f"MK: {jadwal.mata_kuliah}, Jam Mulai: {jadwal.jam_mulai.strftime('%H:%M')}, Semester: {jadwal.semester}, Jurusan: {jadwal.jurusan}, Hari: {jadwal.get_hari_display()}" for jadwal in jadwal_dosen_hari_ini]
                    )
                else:
                    chatbot_response = f"Tidak ada jadwal untuk {username_dosen} hari ini ({today_indonesia})."
            except CustomUser.DoesNotExist:
                chatbot_response = f"Dosen dengan username {username_dosen} tidak ditemukan."
        elif user_input == "/jadwalku":
            if current_user.role == CustomUser.Mahasiswa:
                if current_user.semester and current_user.department:
                    today = datetime.datetime.today().strftime('%A').upper()
                    translated_today = {
                        'MONDAY': 'MONDAY',
                        'TUESDAY': 'TUESDAY',
                        'WEDNESDAY': 'WEDNESDAY',
                        'THURSDAY': 'THURSDAY',
                        'FRIDAY': 'FRIDAY',
                        'SATURDAY': 'SATURDAY',
                        'SUNDAY': 'SUNDAY'
                    }.get(today, today)

                    jadwal_hari_ini = JadwalMengajar.objects.filter(
                        hari=translated_today,
                        semester=current_user.semester,
                        jurusan=current_user.department
                    )

                    if jadwal_hari_ini:
                        # Buat pesan jadwal untuk hari ini
                        jadwal_message = "\n".join(
                            [f"Dosen: {jadwal.dosen}, Jam Mulai: {jadwal.jam_mulai.strftime('%H:%M')}, Jam Berakhir: {jadwal.jam_berakhir.strftime('%H:%M')}" for jadwal in jadwal_hari_ini]
                        )
                        chatbot_response = f"Jadwal Anda hari ini ({today}):\n{jadwal_message}"
                    else:
                        chatbot_response = f"Tidak ada jadwal untuk hari ini ({today})."
                else:
                    chatbot_response = "Silakan hubungi admin untuk memperbarui status profil Anda (jurusan dan semester)."

        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=conversation_history,
            )

            chatbot_response = response['choices'][0]['message']['content']

        escaped_chatbot_response = escape(chatbot_response)
        formatted_chatbot_response = f'<code class="language-python">{escaped_chatbot_response}</code>'

        conversation = Conversation(user=current_user, user_message=user_input, chatbot_response=chatbot_response, sesi=sesi)
        conversation.save()

        return JsonResponse({'user_input': user_input, 'chatbot_response': formatted_chatbot_response})

    return render(request, 'chatbot.html', {
        'chatbot_response': chatbot_response,
        'conversations': conversations,
        'sesi': sesi,
        'sesi_last': sesi_last,
        'sesi_list': sesi_list,
    })


def hapus_sesi(request, uuid):
    sesi = get_object_or_404(SesiChat, uuid=uuid)
    sesi.delete()
    
    # Assuming you want to redirect to 'tambah_data_tabel' with the last session UUID
    sesi_last = SesiChat.objects.last()
    if sesi_last:
        return redirect('tambah_data_tabel', uuid=sesi_last.uuid)
    
    # Handle the case when there is no last session
    return HttpResponse("No last session available.")

def hapus_sesi_d(request, uuid):
    sesi = get_object_or_404(SesiChat, uuid=uuid)
    sesi.delete()
    
    # Assuming you want to redirect to 'tambah_data_tabel' with the last session UUID
    sesi_last = SesiChat.objects.last()
    if sesi_last:
        return redirect('dsn_cb', uuid=sesi_last.uuid)
    
    # Handle the case when there is no last session
    return HttpResponse("No last session available.")
