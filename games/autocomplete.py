from dal import autocomplete
from cities_light.models import Country, Region, City


class CountryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Country.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class RegionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Region.objects.all()
        country_id = self.forwarded.get("country")
        if not country_id:
            return Region.objects.none()
        qs = qs.filter(country_id=country_id)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def get_result_label(self, item):
        return item.name


class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = City.objects.all()
        region_id = self.forwarded.get("region")
        if not region_id:
            return City.objects.none()
        if region_id:
            qs = qs.filter(region_id=region_id)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def get_result_label(self, item):
        return item.name
