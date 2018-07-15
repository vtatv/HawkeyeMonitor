#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time : 2018/7/15 14:59
# @Auther : Wshu
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import django.utils.timezone as timezone


# 设置菜单
class Menu(models.Model):
    title = models.CharField(u'菜单标题', max_length=25, unique=True)
    icon = models.CharField(u'菜单图标', max_length=50)
    parent = models.ForeignKey('self', verbose_name=u'父菜单', related_name='menu_menu', null=True, blank=True,
                               on_delete=models.CASCADE)

    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)


# 设置访问链接
class Permission(models.Model):
    title = models.CharField(u'权限标题', max_length=50, unique=True)
    is_menu = models.BooleanField('菜单显示', default=False)
    url = models.CharField(max_length=128)
    menu = models.ForeignKey(Menu, null=True, verbose_name=u'权限菜单', related_name='permission_menu',
                             on_delete=models.CASCADE)

    def __str__(self):
        return '{menu}--{permission}'.format(menu=self.menu, permission=self.title)


# 设置角色和权限
class Role(models.Model):
    title = models.CharField(u'角色名称', max_length=25, unique=True)
    permissions = models.ManyToManyField(Permission, verbose_name=u'权限菜单', related_name='role_permission')

    def __str__(self):
        return self.title


class Area(models.Model):
    name = models.CharField('属地信息', max_length=90, unique=True)
    parent = models.ForeignKey('self', verbose_name='父级属地', related_name='assetarea_area', null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        # 显示层级菜单
        title_list = [self.name]
        p = self.parent
        while p:
            title_list.insert(0, p.name)
            p = p.parent
        return '-'.join(title_list)




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_num = models.CharField(u'员工编号', max_length=50, null=True, blank=True)
    title = models.CharField(u'职位名称', max_length=50)

    telephone = models.CharField(u'座机号码', max_length=50, null=True, blank=True)
    mobilephone = models.CharField(u'手机号码', max_length=50)
    description = models.TextField(u'用户简介')
    error_count = models.IntegerField(u'错误登陆', default=0)
    lock_time = models.DateTimeField(u'锁定时间', default=timezone.now)

    parent_email = models.EmailField('上级邮箱',null=True,blank=True)
    parent = models.ForeignKey(User, verbose_name='上级汇报', related_name='user_parent', null=True, blank=True, on_delete=models.CASCADE)
    area =  models.ForeignKey(Area, verbose_name='所属区域', related_name='user_area', null=True, on_delete=models.CASCADE, limit_choices_to={'parent__isnull': True})

#同步保存信息
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()