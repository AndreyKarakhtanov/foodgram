from django import forms

from .models import Recipe


class RecipeModelForm(forms.ModelForm):
    """Форма для админ-панели рецепта."""
    favorites = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(RecipeModelForm, self).__init__(*args, **kwargs)
        self.initial['favorites'] = self.instance.favorites.count()
        if self.instance and self.instance.pk:
            favorites = self.fields['favorites']
            favorites.label = 'Общее число добавлений в избранное'
            favorites.widget.attrs['readonly'] = True

    class Meta:
        model = Recipe
        fields = '__all__'
