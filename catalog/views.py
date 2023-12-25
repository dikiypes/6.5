from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.views import View
from .models import Product, Version
from .forms import ProductForm, VersionForm
import json


class ProductListView(View):
    template_name = 'catalog/home.html'

    def get(self, request):
        products = Product.objects.all()
        return render(request, self.template_name, {'products': products})


class ContactView(View):
    def get(self, request):
        return render(request, "catalog/contact.html")


class ProductDetailView(View):
    template_name = 'catalog/product_detail.html'

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        # Получаем текущую версию для продукта
        current_version = Version.objects.filter(
            product=product, is_current=True).first()

        return render(request, self.template_name, {'product': product, 'current_version': current_version})


class ProductCreateView(View):
    template_name = 'product_form.html'

    def get(self, request):
        form = ProductForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/catalog')  # Замените на ваш путь
        return render(request, self.template_name, {'form': form})


class ProductUpdateView(View):
    template_name = 'product_form.html'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        versions = Version.objects.filter(product=product)
        version_choices = [(version.id, version.version_number)
                           for version in versions]
        current_version = versions.filter(is_current=True).first()
        form.fields['version'] = forms.ChoiceField(
            choices=version_choices, initial=current_version.id if current_version else None)

        return render(request, self.template_name, {'form': form, 'product': product})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, request.FILES, instance=product)

        selected_version_id = request.POST.get('version')

        if form.is_valid():
            form.save()

            if selected_version_id:
                selected_version = Version.objects.get(id=selected_version_id)
                selected_version.product = product
                selected_version.is_current = True
                selected_version.save()

            Version.objects.filter(product=product).exclude(
                id=selected_version_id).update(is_current=False)
            return redirect('/catalog')  # Замените на ваш путь
        return render(request, self.template_name, {'form': form, 'product': product})


class ProductDeleteView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return redirect('/catalog')  # Замените на ваш путь


class VersionCreateView(View):
    template_name = 'catalog/version_form.html'

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = VersionForm(initial={'product': product})
        return render(request, self.template_name, {'form': form, 'product': product})

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = VersionForm(request.POST)
        if form.is_valid():
            version = form.save(commit=False)
            version.product = product
            version.save()
            # Измените на ваше представление списка продуктов
            return redirect('/catalog')
        return render(request, self.template_name, {'form': form, 'product': product})
