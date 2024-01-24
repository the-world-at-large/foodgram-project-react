from django.contrib import admin
from recipes.models import (FavouritesList, Ingredients, RecipeIngredients,
                            Recipes, ShoppingList, Tags)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ('name', 'author', 'favourites_count')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    exclude = ('ingredients',)

    def favourites_count(self, obj):
        return obj.favourites.count()


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
admin.site.register(FavouritesList)
admin.site.register(ShoppingList)
