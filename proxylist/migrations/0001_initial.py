# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProxyCheckResult'
        db.create_table('proxylist_proxycheckresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mirror', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['proxylist.Mirror'])),
            ('proxy', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['proxylist.Proxy'])),
            ('real_ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('forwarded', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('ip_reveal', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('check_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('response_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('response_end', self.gf('django.db.models.fields.DateTimeField')()),
            ('check_end', self.gf('django.db.models.fields.DateTimeField')()),
            ('raw_response', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('proxylist', ['ProxyCheckResult'])

        # Adding model 'Mirror'
        db.create_table('proxylist_mirror', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('output_type', self.gf('django.db.models.fields.CharField')(default='plm_v1', max_length=10)),
        ))
        db.send_create_signal('proxylist', ['Mirror'])

        # Adding model 'Proxy'
        db.create_table('proxylist_proxy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('port', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('country', self.gf('django_countries.fields.CountryField')(max_length=2, blank=True)),
            ('speed', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('connection_time', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('proxy_type', self.gf('django.db.models.fields.CharField')(default='http', max_length=10)),
            ('anonymity_level', self.gf('django.db.models.fields.PositiveIntegerField')(default=None, null=True)),
            ('last_check', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('next_check', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('errors', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('proxylist', ['Proxy'])


    def backwards(self, orm):
        # Deleting model 'ProxyCheckResult'
        db.delete_table('proxylist_proxycheckresult')

        # Deleting model 'Mirror'
        db.delete_table('proxylist_mirror')

        # Deleting model 'Proxy'
        db.delete_table('proxylist_proxy')


    models = {
        'proxylist.mirror': {
            'Meta': {'object_name': 'Mirror'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output_type': ('django.db.models.fields.CharField', [], {'default': "'plm_v1'", 'max_length': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'proxylist.proxy': {
            'Meta': {'ordering': "('-last_check',)", 'object_name': 'Proxy'},
            'anonymity_level': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True'}),
            'connection_time': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'blank': 'True'}),
            'errors': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_check': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'next_check': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'proxy_type': ('django.db.models.fields.CharField', [], {'default': "'http'", 'max_length': '10'}),
            'speed': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'proxylist.proxycheckresult': {
            'Meta': {'object_name': 'ProxyCheckResult'},
            'check_end': ('django.db.models.fields.DateTimeField', [], {}),
            'check_start': ('django.db.models.fields.DateTimeField', [], {}),
            'forwarded': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'ip_reveal': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mirror': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proxylist.Mirror']"}),
            'proxy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proxylist.Proxy']"}),
            'raw_response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'real_ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'response_end': ('django.db.models.fields.DateTimeField', [], {}),
            'response_start': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['proxylist']