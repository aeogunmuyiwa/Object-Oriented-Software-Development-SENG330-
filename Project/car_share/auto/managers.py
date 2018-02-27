from django.db import models
from django.db import connection
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import UserManager

import datetime

from .querysets import *


class CustomerManager(models.Manager):
	def create_customer(self, username, first_name, hours, email, password):
		return self.create(username=username, first_name=first_name, last_name=hours, email=email, password=password)


class DepotManager(models.Manager):
	def create_depot(self, address):
		return self.create(address=address)
	
	def get_queryset(self):
		return DepotQuerySet(self.model, using=self._db)

	def depots(self, address=None):
		if address:
			return self.get_queryset().depots(address=address)
		return self.get_queryset().depots()


class VehicleManager(models.Manager):
	def create_vehicle(self, depot, v_type, license):
		return self.create(depot=depot, v_type=v_type, license=license)

	def get_queryset(self):
		return VehicleQuerySet(self.model, using=self._db)

	def vehicles(self, depot=None, v_type=None):
		if not depot:
			return self.get_queryset().vehicles()
		elif not v_type:
			return self.get_queryset().vehicles(depot)
		else:
			return self.get_queryset().vehicles(depot, v_type)

class BookingManager(models.Manager):
	def create_booking(self, customer, vehicle, depot, start_time, end_time):
		if start_time > end_time:
			return 0
		td = end_time - start_time
		days, seconds = td.days, td.seconds
		hours = days * 24 + seconds // 3600

		try:
			if hours > int(customer.last_name):
				return -1
		except:
			return -2

		customer.last_name = "{}".format(int(customer.last_name) - hours)
		customer.save()
		return self.create(customer=customer, vehicle=vehicle, depot=depot, start_time=start_time, end_time=end_time)

	def get_queryset(self):
		return BookingQuerySet(self.model, using=self._db)

	def bookings(self, customer=None, vehicle=None, depot=None, start_time=None):		
		if start_time and customer:		
			return self.get_queryset().bookings(customer=customer, start_time=start_time)
		if customer:
			return self.get_queryset().bookings(customer=customer)
		if vehicle:
			return self.get_queryset().bookings(vehicle=vehicle)
		if depot:
			return self.get_queryset().bookings(depot=depot)
		return self.get_queryset().bookings()
	
	def delete_booking(self, customer, booking):
		start_time = booking.start_time
		end_time = booking.end_time
		td = end_time - start_time
		days, seconds = td.days, td.seconds
		hours = days * 24 + seconds // 3600
		
		customer.last_name = "{}".format(int(customer.last_name) + hours)
		customer.save()
		booking.delete()

'''__calc_hours(start_time, end_time):  # WILL BE USED TO REMOVE REDUNDENCY
	td = end_time - start_time
	days, seconds = td.days, td.seconds
	hours = days * 24 + seconds // 3600
	return hours'''

