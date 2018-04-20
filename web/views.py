from django.shortcuts import render,redirect,HttpResponse
from web import models
from rbac.service import initial_permission
import datetime
import json

def login(request):
    if request.method == "GET":
        return render(request,'login.html')
    else:
        u = request.POST.get('username')
        p = request.POST.get('password')
        obj = models.UserInfo.objects.filter(user__username=u,user__password=p).first()
        if obj:
            request.session['user_info'] = {'username':u,'nickname':obj.nickname,'nid':obj.id}
            initial_permission(request,obj.user_id)
            return redirect('/index.html')
        else:
            return render(request,'login.html')

def index(request):
    if not request.session.get('user_info'):
        return redirect('/login.html')

    return render(request,'index.html')

def trouble(request):
    # request.permission_code_list
    if request.permission_code == "LOOK":
        trouble_list = models.Order.objects.filter(create_user_id=request.session["user_info"]["nid"])
        return render(request,"trouble.html",{"trouble_list":trouble_list})
    elif request.permission_code == "DEL":
        nid = request.GET.get("nid")
        models.Order.objects.filter(create_user_id=request.session["user_info"]["nid"],id=nid).delete()
        return redirect("/trouble.html")
    elif request.permission_code == "POST":
        if request.method == "GET":
            return render(request,"trouble_add.html")
        else:
            title = request.POST.get("title")
            content = request.POST.get("content")
            models.Order.objects.create(title=title,detail=content,create_user_id=request.session["user_info"]["nid"])
            return redirect("/trouble.html")


def troubleshoot(request):
    nid = request.session["user_info"]["nid"]
    if request.permission_code == "LOOK":
        # 查看列表：未解决的，当前用户已解决的或者正在解决的
        from django.db.models import Q
        trouble_list = models.Order.objects.filter(Q(status=1)|Q(processer_id=nid)).order_by("status")

        return render(request,"troubleshoot_look.html",{"trouble_list":trouble_list})
    elif request.permission_code == "EDIT":
        if request.method == "GET":
            # /troubleshoot.html?md=edit&nid=1
            order_id = request.GET.get("nid")
            # 抢到，未处理
            if models.Order.objects.filter(id=order_id,processer_id=nid,status=2):
                obj = models.Order.objects.filter(id=order_id).first()
                return render(request,"troubleshoot_edit.html",{"obj":obj})
            # 开始抢
            v = models.Order.objects.filter(id=order_id,status=1).update(processer_id=nid,status=2,)
            if not v:  # 没抢到
                return HttpResponse("没抢到")
            else:  # 抢到了
                obj = models.Order.objects.filter(id=order_id).first()
                return render(request,"troubleshoot_edit.html",{"obj":obj})
        else:
            order_id = request.GET.get("nid")
            solution = request.POST.get("solution")
            models.Order.objects.filter(id=order_id,processer_id=nid).update(status=3,solution=solution,ptime=datetime.datetime.now())
            return redirect("/troubleshoot.html")



def report(request):
    if request.permission_code == "LOOK":
        # 获取每个人处理个数
        """
        ID  title  detail  create_user_id  ctime  status  processer_id  ptime  resolution
        """
        if request.method == "GET":
            return render(request,"report.html")
        else:
            from django.db.models import Count
            result = models.Order.objects.filter(status=3).values("processer_id","processer__nickname").annotate(ct=Count("id"))
            response = {
                "pie":[{
                    "name": 'fangshaowei',
                    "y": 45.00
                }, {
                    "name": 'youqinbing',
                    "y": 12.00
                },
                ]
            }
            return HttpResponse(json.dumps(response))



def test(request):
    x = models.Test.objects.only("name")[0]
    print(x)
    print(x.name)
    print(x.age)
    return HttpResponse("{}".format(x))