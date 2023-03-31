from django.shortcuts import render,redirect
from django.http.response import JsonResponse, HttpResponse
from .models import Room,Message, Map, Active
import csv,os
from django.conf import settings
import os
from random import sample
from django.db.models import Q
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def update_userinfo(roomid,user):
    if Active.objects.filter(Q(roomid=roomid) & Q(user=user)).exists():
        models = Active.objects.get(Q(roomid=roomid) & Q(user=user))
        print(models)
        models.online = True
        models.save()
    else:
        models = Active.objects.create(roomid=roomid,user=user,online=True)
def gen():
    alpha = list("abcdefghijklmnopqrstuvwxyz")
    name = "".join(sample(alpha,3))
    return name
def Home(request):
    return render(request,"index.html")

def Chat(request):
    return render(request,"chat.html")
def Stranger_map(request):
    print("working")
def Check_room(request):
    if 'create' in request.GET:
        #Room Creation
        room_id = request.GET['room_id']
        username = request.GET["username"]
        if Room.objects.filter(name=room_id).exists():
            return render(request, 'chat.html', {'message': "Room Already Exist", 'message2':""})
        else:
            creation = Room.objects.create(name=room_id, creater=username)
            creation.save()
            update_userinfo(room_id,username)
            return redirect("/"+room_id+"/?username="+username) 
    elif "join" in request.GET:
        room_id = request.GET['room_id']
        username = request.GET["username"]
        if Room.objects.filter(name=room_id).exists():
            update_userinfo(room_id,username)
            return redirect("/"+room_id+"/?username="+username)
        else:    
            return render(request, 'chat.html', {'message':"",'message2': "No Room Found"})
        
    elif "stranger" in request.GET:
        name = gen()
        if Map.objects.filter(status=False).exists():
            username= 'user1542325451'
            roomcode = Map.objects.filter(status=False)
            roomcode = roomcode.values()[0].get('roomid')
            print(roomcode)
            details = Map.objects.get(roomid=roomcode)
            details.status = True
            details.save()
            update_userinfo(roomcode,username)
            return redirect("/"+roomcode+"/?username="+username)
        else:
            def else_room():
                name = gen()
                username = 'user15453232512'
                if Room.objects.filter(name=name).exists() == False:
                    creation = Room.objects.create(name=name, creater=username)
                    creation.save()
                    creation2 = Map.objects.create(roomid=name,status=False)
                    creation2.save()
                    return render(request,'lobby.html',{'user':username,'room':name})
                else:
                    else_room()
            return else_room()

        return JsonResponse({"messages":'working'})
    else:
        print(request.GET)
        return JsonResponse({"messages":'not wroking'})

def Room_join(request,room):
    print(request.GET)
    username = request.GET.get('username')
    print("username 54654654654 : ",username)
    print(username,room)
    return render(request,"message.html",{
        "user":username,
        "room":room,
    })

def Send(request):
    print("Recieveing")
    print(request)
    username = request.POST['username']
    room = request.POST["room_id"]
    message = request.POST['message']
    entry = Message.objects.create(msg=message,room=room,sender=username)
    entry.save()
    return HttpResponse('Message sent successfully')
def message(request,room):
    print("Message Recieving")
    print(room)
    msg_list = Message.objects.filter(room=room)
    active_users = Active.objects.filter(roomid=room, online=True, active_display=False)
    offline_users = Active.objects.filter(roomid=room, online=False, offline_display=False)
    # actibe
    for user in active_users:
        user.active_display = True
        message = f'{user.user} has joined the chat'
        entry = Message.objects.create(msg=message,room=room,sender='Chatlets(bot)')
        entry.save()
        user.save()
    #offline
    for user in offline_users:
        user.offline_display = True
        message = f'{user.user} has left the chat'
        entry = Message.objects.create(msg=message,room=room,sender='Chatlets(bot)')
        entry.save()
        user.save()

   
    return JsonResponse({"messages":list(msg_list.values())})

def Download(request):
    room = request.GET["roomname"]
    info = Message.objects.filter(room=room)
    method = list(info.values())
    file_name = room + ".csv"
    path = os.path.join(settings.STATICFILES_DIRS[0], 'files', file_name)
    
    with open(path, "w", newline="") as f:
        fwriter = csv.writer(f)
        final = []
        fwriter.writerow(["Chatlets","Created by","Praveen"])
        fwriter.writerow(["Message","Sender","Time&Date"])
        for i in method:
            msg = i["msg"]
            sender = i["sender"]
            if sender == 'Chatlets(bot)':
                continue
            time = str(i['date'])
            time = time[:time.index(".")]
            final.append([msg, sender, time])
        fwriter.writerows(final)

    with open(path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{path}"'
        response['Content-Length'] = os.path.getsize(path)

    return response


def Page(request):
    return redirect("/home")


def Lobby(request):
    roomid = request.POST['room_id']
    user = request.POST['username']
    roomcode = Map.objects.filter(roomid=roomid)
    a = roomcode.values()[0]
    print(a)
    status = a['status']
    print(status)

    if status == True:
        update_userinfo(roomid,user)
        return JsonResponse({'room_id': roomid, 'username': user, 'status': True})

    return HttpResponse("Finding a Match")

def Remove_room(request):
    roomid = request.POST['room_id']
    user = request.POST['username']
    models = Map.objects.get(roomid=roomid).delete()
    models2 = Room.objects.get(name=roomid).delete()
    return HttpResponse("All done")

def User_inactive(request):
    roomid = request.POST['room_id']
    user = request.POST['username']
    models = Active.objects.get(Q(roomid=roomid) & Q(user=user))
    models.online = False
    models.save()
    return HttpResponse("OK")

def checkuser(request):
    room_id = request.POST.get('room_id')
    username = request.POST.get('username')
    active_user = Active.objects.filter(roomid=room_id, online=True, active_display=False).first()
    if active_user:
        print(active_user.user)
    offline_user = Active.objects.filter(roomid=room_id, online=False, offline_display=False).first()
    if offline_user:
        print(offline_user.user)
    
    return HttpResponse("fyn")

