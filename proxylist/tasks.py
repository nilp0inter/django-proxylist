# -*- coding: utf-8 -*-
from celery import task

@task(ignore_result=True)
def async_check(proxy, checker):
    checker._check(proxy)
