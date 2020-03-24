from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from app.forms.adress import AddressFormset
from app.forms.phone import PhoneFormset
from app.forms.profile import ProfileForm
from app.views.mixins import PersonTypedMixin
from core.models.address import Address
from core.models.address_type import AddressType
from core.models.entity import EntityPhone, EntityAddress
from core.models.phone import Phone


class ProfileView(LoginRequiredMixin, PersonTypedMixin, generic.TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        if not isinstance(self.request.user, AnonymousUser):
            user = self.request.user
            result['profile_form'] = ProfileForm(
                initial={'first_name': user.first_name,
                         'last_name': user.last_name,
                         'username': user.username,
                         'email': user.email
                         })
            result['phone_formset'] = PhoneFormset(
                prefix='phone',
                initial=[{'type': e_p.phone_type,
                          'number': e_p.phone.phone_number} for e_p in
                         EntityPhone.objects.filter(entity=self.persontyped)])
            result['address_formset'] = AddressFormset(
                prefix='address',
                initial=[{'type': e_a.address_type.pk,
                          'details': e_a.address.details} for e_a in
                         EntityAddress.objects.filter(entity=self.persontyped)])
        return result

    def post(self, request, *args, **kwargs):
        _p = request.POST
        _r = request.FILES
        profile_form = ProfileForm(_p, _r)
        ok = profile_form.is_valid()

        phones_formset = PhoneFormset(_p, _r, prefix='phone')
        ok = ok and phones_formset.is_valid()

        addresses_formset = AddressFormset(_p, _r, prefix='address')
        ok = ok and addresses_formset.is_valid()

        if not ok:
            return self.form_invalid(profile_form,
                                     phones_formset, addresses_formset)
        return self.form_valid(profile_form,
                               phones_formset, addresses_formset)

    @staticmethod
    def get_success_url():
        return reverse('index')

    def form_invalid(self, profile_form, phones_formset, addresses_formset):
        # Taken from Django source code:
        """ If the form is invalid, render the invalid form. """
        return self.render_to_response(
            self.get_context_data(profile_form=profile_form,
                                  phones_formset=phones_formset,
                                  addresses_formset=addresses_formset))

    def form_valid(self, profile_form, phones_formset, addresses_formset):
        user = self.request.user
        user.username = profile_form.cleaned_data['username']
        user.first_name = profile_form.cleaned_data['first_name']
        user.last_name = profile_form.cleaned_data['last_name']
        user.save()
        person = user.person.as_person_typed()

        # phones
        with transaction.atomic():
            EntityPhone.objects.filter(entity=person).delete()
            for phone_form in phones_formset:
                number = phone_form.cleaned_data['number']
                phone_type = int(phone_form.cleaned_data['type'])
                if not (number and phone_type and
                        phone_type in EntityPhone.PHONE_TYPES):
                    continue
                phone = Phone.objects.create(phone_number=number)
                EntityPhone.objects.create(entity=person, phone_type=phone_type,
                                           phone=phone, )

        # addresses
        with transaction.atomic():
            EntityAddress.objects.filter(entity=person).delete()
            for address_form in addresses_formset:
                address_type = address_form.cleaned_data['type']
                address_details = address_form.cleaned_data['details']
                if not (address_details and address_type):
                    continue
                try:
                    address_type = AddressType.objects.get(pk=address_type)
                except AddressType.DoesNotExist:
                    continue
                try:
                    address = Address.objects.get(summary=address_details)
                except (Address.DoesNotExist, Address.MultipleObjectsReturned):
                    address = Address.objects.create(summary=address_details,
                                                     details=address_details, )
                EntityAddress.objects.create(entity=person, address=address,
                                             address_type=address_type, )
        return HttpResponseRedirect(self.get_success_url())
