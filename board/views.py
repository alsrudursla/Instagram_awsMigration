from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from app01.models import Users
from board.models import Board, Comment

from kafka import KafkaProducer
from json import dumps

import requests

# Create your views here.
def posting(request):
    contents = request.POST.get('contents',None)
    bimg = request.FILES['image']

    post = Board()
    post.contents = contents
    post.bimg = bimg
    post.writer = request.session['user_id']
    post.save()

    #
    # #db 저장과 동시에 메세지 발행 (토픽메세지 - kafka)
    # producer = KafkaProducer(
    #     acks=0,
    #     compression_type='gzip',
    #     bootstrap_servers=['200.200.200.152:9092'],
    #     value_serializer=lambda x: dumps(x).encode('utf-8')
    # )
    # data = {'message': post.id, 'user': post.writer}
    # producer.send('WEB_BOARD_REGISTER', value=data)
    # producer.flush()
    #
    return redirect("/")
    # #return redirect('/postnow/') - 게시판 등록 현황으로 갈 때
#
# #게시판 등록 현황 확인
# def posting_now(request):
#     result = requests.post("http://200.200.200.150:8082/consumers/" + request.session['user_id'],
#                            data='{"name": "'+request.session['user_id']+'_instance", "format": "json", "auto.offset.reset": "earliest"}',
#                            headers={'Content-Type': 'application/vnd.kafka.v2+json'})
#     print(result.content)
#     result = requests.post("http://200.200.200.150:8082/consumers/"+request.session['user_id']+"/instances/"+request.session['user_id']+"_instance/subscription",
#                            data='{"topics":["WEB_BOARD_REGISTER"]}',
#                            headers={'Content-Type': 'application/vnd.kafka.v2+json'})
#     print(result.content)
#     return render(request, 'pulling.html')


def del_post(request, id, writer):
    now_user = Users.objects.get(uname=writer)
    post = Board.objects.get(id=id)
    if now_user.uname == request.session['user_id']:
        post.delete()
        return redirect('/')
    else :
        #경고 알림창 넣고 싶은데ㅠ
        return redirect('/')

def edit_post(request, id, writer):
    now_user = Users.objects.get(uname=writer)
    post = Board.objects.get(id=id)
    info = { "user" : now_user, "info" : post }
    if now_user.uname == request.session['user_id']:
        return render(request, 'edit_post.html', info)
    else :
        return redirect('/')

def edit_db(request, id):
    contents = request.POST.get('contents',None)

    post = Board.objects.get(id=id)
    post.contents = contents
    post.save()
    return redirect('/')

def detail(request, id):
    now_user = Users.objects.get(uname = request.session['user_id'])
    posting = Board.objects.get(id=id)
    info =  {"user": now_user, "info" : posting}
    return render(request,'detail-page.html', info)

def like(request, id):
    board = Board.objects.get(id=id)
    user = Users.objects.get(uname=request.session['user_id'])

    if board.like.filter(id=user.id).exists():
        board.like.remove(user)
        message = "del like"
    else:
        board.like.add(user)
        message = "add like"

    return JsonResponse({
        "message" : message
    })

'''
def create_comment(request, id):
    comment = Comment()
    comment.board_id = Board.objects.get(id=id).id
    comment.writer = request.session['user_id']
    comment.contents = request.POST.get('contents',None)
    comment.save()
    return redirect('/show_comment/'+ id +'/')

def show_comment(request, id):
    comment = Comment.objects.filter(board_id=id)
    info = {"info" : comment}
    return 
'''
