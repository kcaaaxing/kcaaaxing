from django.shortcuts import render
from .models import Topic, Entry
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from .forms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required
# render提供数字渲染响应


def index(request):
    """学习笔记的主页"""
    return render(request, 'learning_logs/index.html')


@login_required
def topics(request):
    """显示所有的主题"""
    # objects是垃圾社区版的问题,下次一定要安装专业版
    topics_o = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics_o}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    """显示单个主题及其所有的条目"""
    topic_o = Topic.objects.get(id=topic_id)
    # 确认请求的主题属于当前用户
    if topic_o.owner != request.user:
        raise Http404
    entries = topic_o.entry_set.order_by('-date_added')
    context = {'topic': topic_o, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """添加新主题"""
    if request.method != 'POST':
        """未提交数据: 创建一个新表单"""
        form = TopicForm()
    else:
        """POST提交的数据,对数据进行处理"""
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic_o = form.save(commit=False)
            new_topic_o.owner = request.user
            new_topic_o.save()
            return HttpResponseRedirect(reverse('learning_logs:topics'))

    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """在特定的主题中添加新条目"""
    topic_o = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        # 未提交数据,创建一个空表单
        form = EntryForm()
    else:
        # POST提交的数据,对数据进行处理
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry_o = form.save(commit=False)
            new_entry_o.topic = topic_o
            new_entry_o.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_id]))

    context = {'topic': topic_o, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """编辑既有条目"""
    entry_o = Entry.objects.get(id=entry_id)
    topic_o = entry_o.topic
    if topic_o.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # 初次请求, 使用当前条目填充表单
        form = EntryForm(instance=entry_o)
    else:
        # POST提交的数据,对数据进行处理
        form = EntryForm(instance=entry_o, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_o.id]))

    context = {'entry': entry_o, 'topic': topic_o, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
