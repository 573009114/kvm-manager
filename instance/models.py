from django.db import models
from servers.models import Compute


class Instance(models.Model):
    compute = models.ForeignKey(Compute)
    name = models.CharField(max_length=100)
    uuid = models.CharField(max_length=36)
    # display_name = models.CharField(max_length=50)
    # display_description = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

class Network(models.Model):
  ipaddr=models.IPAddressField()
  netmask=models.IPAddressField()
  gateway=models.IPAddressField()

  def __unicode__(self):
        return self.ipaddr
