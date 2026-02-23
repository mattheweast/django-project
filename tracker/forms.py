from django import forms
from .models import Category, Item


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'name',
            'category',
            'purchase_price',
            'estimated_value',
            'purchase_date',
            'condition',
            'photo',
            'description',
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        base_classes = (
            'mt-2 block w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 '
            'text-sm text-white placeholder:text-gray-500 focus:border-indigo-400 focus:outline-none '
            'focus:ring-2 focus:ring-indigo-500/40'
        )

        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} {base_classes}".strip()

        self.fields['photo'].widget.attrs['class'] = (
            'mt-2 block w-full text-sm text-gray-200 '
            'file:mr-4 file:rounded-lg file:border-0 file:bg-indigo-500 file:px-3 file:py-2 '
            'file:font-semibold file:text-white hover:file:bg-indigo-400'
        )

        if user is not None:
            self.fields['category'].queryset = Category.objects.filter(user=user)
