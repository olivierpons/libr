
class PersonTypedMixin:
    """ Init self.persontyped (if user is logged) """

    def __init__(self):
        self.persontyped = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = self.request.user
            person = user.person
            if hasattr(person, 'persontyped'):
                self.persontyped = person.persontyped
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['person_typed'] = self.persontyped
        return result
