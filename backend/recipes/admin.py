from django import forms
from django.contrib import admin

from recipes.models import (FavoritesList, Ingredients, RecipeIngredients,
                            Recipes, ShoppingList, Tags)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1
    min_num = 1


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipes
        fileds = '__all__'

    def clean(self):
        title = self.cleaned_data['title']
        if not title.istitle():
            raise forms.ValidationError({'title': "Неподходящее значение."})


class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm

    inlines = [RecipeIngredientInline]
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    def favorites_count(self, obj):
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Recipes, RecipeAdmin)
admin.site.register(Ingredients, IngredientAdmin)
admin.site.register(Tags, TagAdmin)
admin.site.register(FavoritesList)
admin.site.register(ShoppingList)
