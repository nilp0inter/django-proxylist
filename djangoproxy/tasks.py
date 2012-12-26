# -*- coding: utf-8 -*-
from celery import task

@task(ignore_result=True)
def async_check(proxy, checker):
    return checker._check(proxy)
