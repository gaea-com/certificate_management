from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **init_kwargs):
        view = super().as_view(**init_kwargs)
        return login_required(view)
