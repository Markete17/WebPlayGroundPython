# WebPlayGroundPython

Toda la información en: [Información](https://docs.hektorprofe.net/django/web-playground/)

**Índice**   
1. [TemplateView: Vistas como objetos en vez de como funciones](#id1)
2. [ListView y Paginación](#id2)
3. [DetailView](#id3)
4. [URL Patterns](#id4)
5. [CreateView y Include TemplateTag](#id5)
6. [UpdateView](#id6)
7. [DeleteView](#id7)
8. [Formulario para los CBV (los View)](#id8)
9. [Proteger las url (Utilización de Mixin)](#id9)
10. [Decoradores de identificación](#id10)
11. [Autenticación con Django](#id11)
12. [Perfil de usuario, relaciones entre modelos Django e imágenes en modelos, UpdateView sin indicar la PK](#id12)
13. [Señales](#id13)
14. [Pruebas unitarias Django](#id14)
15. [App de mensajería con TDD](#id15)
16. [Django MySQL](#id16)
17. [Django Deploy: Ngnix, Gunicorn y Docker](#id17)


## Vistas como objetos en vez de como funciones<a name="id1"></a>

[Información](https://docs.djangoproject.com/en/4.0/ref/class-based-views/)
[Información](https://ccbv.co.uk/)

Para este caso, el objeto que mejor se adapta al ejemplo es el <b>TemplateView</b>

De esta manera. Dentro de la clase se tiene que añadir la propiedad <b>template_name</b> y definir el método <b>get_context_data</b>

```python
def home(request):
    return render(request, "core/home.html", {"title": 'Mi web'})
```

sería:

```python
class HomePageView(TemplateView):
    template_name = "core/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mi web'
        return context

```

y en las urls.py se llama a la clase con el método as_view()


```python
from django.urls import path
from .views import SampleView, HomePageView
from . import views

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('sample/', SampleView().as_view(), name="sample"),
]
```

También se puede hacer de esta forma y es parecido a lo que se hacía con las funciones y es definir el método <b>def get(self, request, *args, **kwargs)</b>


```python
class HomePageView(TemplateView):
    template_name = "core/home.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"title": 'Mi web'})
```

---------------------------------------

## ListView y Paginación <a name="id2"></a>

[Información](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-display/#django.views.generic.list.ListView)

Igual que pasa con el TemplateView, para devolver una lista de objetos a la vista o el detalle de un modelo, se puede utilizar <b>ListView</b> y <b>DetailView</b>

1. ListView

Se importa la biblioteca: from django.views.generic.list import ListView

Y ahora en vez de tener una función que devuelve la lista de objetos, se tiene una clase ListView configurada de la siguiente manera:

Lo siguiente:
```python
def pages(request):
    pages = get_list_or_404(Page)
    return render(request, 'pages/pages.html', {'pages':pages})
```

Se convierte en una clase ListView

```python
class HomePageView(TemplateView):
    template_name = "core/home.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"title": 'Mi web'})
```

No olvidar que en el archivo urls.py hay que poner la clase creada con el método as_view().

```python
urlpatterns = [
    path('', views.pages, name='pages'),
    path('<int:page_id>/<slug:page_slug>/', PageListView.as_view() , name='page'),
]```

En la vista se puede llamar a esta lista como {{object_list}} o el {{nombreModelo_list}}

### Paginación

Para hacer la paginación de este modelo, es necesario que la clase ListView tenga la propiedad <b>paginated_by</b> indicando el número de objetos que va a tener cada página.

```python
class PageListView(ListView):
    model = Page
    paginate_by = 3
    # template_name = "pages/pages.html" no hace falta, detecta que es page_list
    
    # Paginación: https://stackoverflow.com/questions/39088813/django-paginator-with-many-pages
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context.get('is_paginated', False):
            return context

        paginator = context.get('paginator')
        num_pages = paginator.num_pages
        current_page = context.get('page_obj')
        page_no = current_page.number

        if num_pages <= 11 or page_no <= 6:  # case 1 and 2
            pages = [x for x in range(1, min(num_pages + 1, 12))]
        elif page_no > num_pages - 6:  # case 4
            pages = [x for x in range(num_pages - 10, num_pages + 1)]
        else:  # case 3
            pages = [x for x in range(page_no - 5, page_no + 6)]

        context.update({'pages': pages})
        return context
```

En StackOverflow explica el algoritmo para hacer responsive la paginación y siempre mostrar 11 páginas.

[Paginación Responsive](https://stackoverflow.com/questions/39088813/django-paginator-with-many-pages)


Ahora en la vista se puede utilizar la paginación utilizando {{page_obj}} y algunos atributos que tiene este objeto como por ejemplo:

- <b>page_obj.has_previous:</b> saber si hay una página antes. 
- <b>page_obj.has_next:</b> saber si hay una página después
- <b>page_obj.previous_page_number:</b> saber el número de página anterior
- <b>page_obj.next_page_number:</b> saber el número de página siguiente
- <b>page_obj.number:</b> saber el número de página actual
- <b>page_obj.paginator.num_pages:</b> saber el número de páginas totales

Un ejemplo es: 

```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Páginas{% endblock %}

{% block content %}
{% include "pages/includes/pages_menu.html" %}
<main role="main">
  <div class="container mb-4">
    {% for page in page_list|dictsort:'id' reversed %}
      <div class="row mt-3">
        <div class="col-md-9 mx-auto">
          <h2 class="mb-4">{{page.title}}</h2>
          <div>
            <p>{{page.content|striptags|safe|truncatechars:"200"}}</p>
            <p><a href="{% url 'pages:page' page.pk page.title|slugify %}">Leer más</a>
              {% if request.user.is_staff %}
                | <a href="{% url 'pages:update' page.id %}">Editar</a>
                | <a href="{% url 'pages:delete' page.id %}">Borrar</a>
              {% endif %}
            </p>
          </div>
        </div>
      </div>
    {% endfor %}

    <!-- Menú de paginación -->
{% if is_paginated %}
<nav aria-label="Page navigation">
  <ul class="pagination justify-content-center">
    {% if page_obj.has_previous %}
      <li class="page-item ">
        <a class="page-link" href="?page={{ page_obj.previous_page_number }}">&laquo;</a>
      </li>
    {% else %}
      <li class="page-item disabled">
        <a class="page-link" href="#" tabindex="-1">&laquo;</a>
      </li>
    {% endif %}
    {% for i in pages %}
      <li class="page-item {% if page_obj.number == i %}active{% endif %}">
        <a class="page-link" href="?page={{ i }}">{{ i }}</a>
      </li>
    {% endfor %}
    {% if page_obj.has_next %}
      <li class="page-item ">
        <a class="page-link" href="?page={{ page_obj.next_page_number }}">&raquo;</a>
      </li>
    {% else %}
      <li class="page-item disabled">
        <a class="page-link" href="#" tabindex="-1">&raquo;</a>
      </li>
    {% endif %}
  </ul>
</nav>
{% endif %}
<div class="d-flex justify-content-center">
  <span class="current">
    Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}.
  </span>
  </div>
  </div>
</main>
{% endblock %}

```

---------------------------------------

## DetailView <a name="id3"></a>

[Información](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-display/#django.views.generic.detail.DetailView)

Pasa igual que como el ListView. En vez de crear una función render, se crea una clase que herede de DetailView:

```python
class PageDetailView(DetailView):
    model = Page
    template_name = "pages/page.html"
```

El template_name se puede personalizar pero si no se pone nada por defecto estará en pages/page_detail.html
Luego en la template se puede usar el nombre del objeto, en este caso, {{page.propiedad}}


---------------------------------------

## URL Patterns <a name="id4"></a>

Lo que se ha utilizado hasta ahora es la lista url_patterns = [...] y dentro de ésta,
cada path con un name que es único pero, para tenerlo más organizado, es recomendable utilizar el URL patterns que consiste en
cambiar el nombre del url_patterns a otro nombre y pasarle otro argumento, por ejemplo [nombre_modelo]_patterns y ésta sera ahora una tupla
que se le pasará como primer campo la lista de paths y como segundo campo el nombre del 'tag' para referirse a esas url. Por ejemplo:

```python
pages_patterns = (
    [
    path('', PageListView.as_view(), name='pages'),
    path('<int:pk>/<slug:slug>/', PageDetailView.as_view(), name='page'),
    path('create/', PageCreateView.as_view(), name='create')
    ], 'pages')
```

No olvidarse que en el urls.py general ahora hay que importar esta nueva pattern modificada:

```python
from pages.urls import pages_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('core.urls')),
    path('pages/', include(pages_patterns))
]
```

<b>Ahora para referenciar a estas url, en este ejemplo, va a ser pages:[name]</b>, por ejmeplo:

```html
<a class="nav-link" href="{% url 'pages:pages' %}"><i>Listar páginas</i></a>
<a href="{% url 'pages:page' page.pk page.title|slugify %}">Ver página detalle</a>
```

---------------------------------------

## CreateView y Include TemplateTag <a name="id5"></a>

Para agregar una vista para crear objetos.

### Include TemplateTag

1. Primero es necesario conocer el <b>TemplateTag Include</b>, es necesario crear una opción del menú para que solo los administradores puedan acceder a él.
Esto no deja ser más que una reutilización del código de una vista a otra.
2. En templates/pages, crear una carpeta <b>includes</b> que tenga <b>page_menu.html</b> y se escribe el código con el submenú usando la variable:
<b>{% if request.user.is_staff %}</b>

```html
{% if request.user.is_staff %}
<nav class="navbar navbar-expand-lg navbar-light bg-light">
  <div class="container">
    <span class="navbar-brand" href="#"><i>Administrar</i></span>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#nep" aria-controls="nep" aria-expanded="false">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="nep">
      <ul class="navbar-nav mr-auto">
        <li class="nav-item">
          <a class="nav-link" href="#"><i>Crear página</i></a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="{% url 'pages' %}"><i>Listar páginas</i></a>
        </li>
      </ul>
    </div>
  </div>
</nav>
{% endif %}
```

3. Ahora con el template tag {{%include 'pages/includes/page_menu.html'%}} se va a copiar el código de este archivo
en la vista seleccionada.

```html
{% block content %}

{% include 'pages/includes/pages_menu.html' %}
.....
```


### CreateView

[Información Documentación](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-editing/#django.views.generic.edit.CreateView)


Al igual que las otras, en el <b>views.py</b>, se tiene que añadir una clase que herede de CreateView. Además, hay que indicar
los campos con los que el usuario va a crear el modelo. También definir el método get_success_url(self) para indicar la página a la que
se quiere que se redirija una vez se cree el modelo.

```html
class PageCreateView(CreateView):
    model = Page
    fields = ['title', 'content', 'order']
    
    def get_success_url(self):
        success_url = reverse('pages:pages')
```

Pero al ser tedioso, se ha creado una nueva forma y es usar reverse_lazy:

```html
class PageCreateView(CreateView):
    model = Page
    fields = ['title', 'content', 'order']
    success_url = reverse_lazy('pages:pages')
```

Con esto, es necesario tener en la app/templates un archivo HTML que se llame page_form.html, es decir el nombremodelo_form.html. Si se quiere cambiar este nombre,
con poner en el CreateView template_url = 'ruta', servirá.

---------------------------------------

## UpdateView <a name="id6"></a>

Parecida al CreateView pero sirve para modificar un modelo.
[Información Documentación](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-editing/#django.views.generic.edit.UpdateView)

Para ello, crear una UpdateView implementando el método <b>get_success_url</b>. 

Para ir a una url que requiera parámetros, no se puede hacer lo anterior ya que es necesario pasar como parámetros el id.
Es necesario también indicar el sufijo del formulario de modificación. Si no se indica este campo, se elige de forma predeterminada el formulario de creación
y esto a veces no es lo deseado porque cosas cambian.

```python
class PageUpdateView(UpdateView):
    model = Page
    fields = ['title', 'content', 'order']
    template_name_suffix = '_update_form'
    def get_success_url(self):
        return reverse_lazy('pages:update', args=[self.object.id]) + '?ok'
```

Ahora con el <b>request.GET</b> se puede saber si se ha modificado correctamente.

page_update_form.html
```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Editar página{% endblock %}
{% block content %}
{% include 'pages/includes/pages_menu.html'%}
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto">
        <div>
          {% if 'ok' in request.GET %}
            <p class="text-success">Página modificada correctamente.
              <a href="{% url 'pages:page' page.id page.title|slugify %}">Haz click aquí para ver el resultado:</a>
            </p>

          {% endif %}
            <form action="" method="post">
                {% csrf_token %}              
                <table>
                    {{ form.as_table }}
                </table>
                <br>
                <input type="submit" value="Editar página" />
            </form>
        </div>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```

---------------------------------------

## DeleteView <a name="id7"></a>

Esta vista se encargará de eliminar un modelo.
[Información Documentación](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-editing/#django.views.generic.edit.DeleteView)

Es necesario crear una vista DeleteView que tenga una url para saber qué hacer cuando se confirma el eliminar:

```python
class PageDeleteView(DeleteView):
    model = Page
    success_url = reverse_lazy('pages:pages')
```

También, es necesario tener en las templates un html llamado page_confirm_delete.html que lo que hará será confirmar el eliminado.

```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Borrar página{% endblock %}
{% block content %}
{% include 'pages/includes/pages_menu.html'%}
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto">
        <div>
            <form action="" method="post">{% csrf_token %}
                <p>¿Estás seguro de que quieres borrar "{{ object }}"?</p>
                <input type="submit" value="Sí, borrar la página" />
            </form>
        </div>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```

---------------------------------------

## Personalizar formulario para los CBV (los View)<a name="id8"></a>

[Información Documentación](https://docs.djangoproject.com/en/4.0/topics/forms/)

Normalmente de manera predeterminada se ven mal los formularios por defecto de django. Lo bueno es que se pueden modificar estos formularios. Para ello:

1. Crear un archivo en la app llamado <b>forms.py</b> 
En este fichero, crear un ModelForm, que será un formulario hecho para un modelo creado. A este modelForm se le pueden agregar atributos css, bootstrap
para personalizar el formulario:

```python
from django import forms
from .models import Page

class PageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ['title', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'content': forms.Textarea(attrs={'class':'form-control'}),
            'order': forms.NumberInput(attrs={'class':'form-control'}),
        }
```

2. Ahora hay que añadir este formulario al CreateView con la propiedad <b>form_class</b> y quitar los fields debido a que en el ModelForm ya se indican:

```python

class PageCreateView(CreateView):
    model = Page
    form_class = PageForm
    success_url = reverse_lazy('pages:pages')
```

3. Cuando se tiene ck-editor, los Django incorporará los textarea con el ck-editor en las templates por lo tanto, es necesario incluir sus estilos en la plantilla
en el head: [Información Documentación](https://github.com/django-ckeditor/django-ckeditor#outside-of-django-admin) 

```html
   
   {% load static %}
	
	<head>
	....
	.....
    <script type="text/javascript" src="{% static 'ckeditor/ckeditor-init.js' %}"></script>
    <script type="text/javascript" src="{% static 'ckeditor/ckeditor/ckeditor.js' %}"></script>
  </head>
```

4. También se pueden agregar labels y placeholders:

```python
class PageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ['title', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Título'},),
            'content': forms.Textarea(attrs={'class':'form-control'}),
            'order': forms.NumberInput(attrs={'class':'form-control'}),
        }
        labels = {
            'title': '',
            'content': '',
            'order': ''
        }
```

5. Hacer que el widget se Ck-Editor sea responsive

Se tiene que crear un archivo css que sobrescriba el código del ck-editor.
Para ello, crear un fichero csss en la app con la siguiente ruta static/pages/css/custom_ckeditor.css que tendrá lo siguiente:

```css
.django-ckeditor-widget, .cke_editor_id_content {
    width: 100% !important;
    max-width: 821px !important;
}
```

```html
{% load static %}
......
<script type="text/javascript" src="{% static 'ckeditor/ckeditor-init.js' %}"></script>
<script type="text/javascript" src="{% static 'ckeditor/ckeditor/ckeditor.js' %}"></script>
<link href="{% static 'pages/css/custom_ckeditor.css' %}" rel="stylesheet">

```

Para arreglarlo en el panel de administrador, se necesita ir al fichero admin.py y crear una clase Media sobrescribiendo un diccionario llamado css
y en all, importar el fichero css

```python
from django.contrib import admin
from .models import Page

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    
    # Inyectamos nuestro fichero css
    class Media:
        css = {
            'all': ('pages/css/custom_ckeditor.css',)
        }
        
admin.site.register(Page, PageAdmin)

```

---------------------------------------

## Proteger las url (Utilización de Mixin) <a name="id9"></a>

[Información Documentación](https://docs.djangoproject.com/en/4.0/topics/class-based-views/mixins/)

Primero para proteger una URL es necesario sobrescribir el método <b>dispatch</b> dentro de la vista. Dispatch lo que detecta es la primera toma de contacto con la url.
Y aquí se puede hacer una comprobación para comprobar si el usuario es un staff

```python
class PageCreateView(CreateView):
    model = Page
    form_class = PageForm
    success_url = reverse_lazy('pages:pages')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse_lazy('admin:login'))
        return super().dispatch(request, *args, **kwargs)
```

Pero no es necesario implementar el dispatch en todas las vistas, para ello se usan los MIXIN. Un Mixin es una implementación de una o varias funcionalidades para una clase.
Se puede implementar una vez y luego heredarla en cualquier momento.

Para ello, se crea una clase y aquí se define el método dispatch que heredarán todas las vistas:

```python
class StaffRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse_lazy('admin:login'))
        return super().dispatch(request, *args, **kwargs)
```

y ahora poner que la vista hereda esta clase:

```python
class PageCreateView(StaffRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    success_url = reverse_lazy('pages:pages')
```

---------------------------------------

## Proteger las url (Utilización decoradores de identificación en los CBV) <a name="id10"></a>

[Documentación decorar CBV](https://docs.djangoproject.com/en/4.0/topics/class-based-views/intro/#decorating-class-based-views)

Se puede hacer con Mixin pero Django incluye ya decoradores de identificación que nos ahorra comprobar si un usuario es un staff.
Por lo tanto, aquí se ahorarrían dos líneas de código.

```python
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

@method_decorator(staff_member_required)
def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)
```

```python
@method_decorator(staff_member_required, name='dispatch')
class PageCreateView(CreateView):
    model = Page
    form_class = PageForm
    success_url = reverse_lazy('pages:pages')
```
	
Esto tiene una ventaja sobre la anterior ya que cuando se accede a una página protegida te pide autenticación y si te logueas, vuelve a la página deseada ya
que añade una query param ?next=[pagina] cuando se autentica el usuario.

Además de este, hay más decoradores de identificación como:

- [@login_required](https://docs.djangoproject.com/en/4.0/topics/auth/default/#the-login-required-decorator)
- [@permission_required](https://docs.djangoproject.com/en/4.0/topics/auth/default/#the-permission-required-decorator)
- [@staff_member_required](https://docs.djangoproject.com/en/2.0/_modules/django/contrib/admin/views/decorators/)

---------------------------------------

## Autenticación con Django <a name="id11"></a>

**Índice**   
1. [Inicio de sesión](#id11-1)
2. [Cerrar sesión sesión](#id11-2)
3. [Registro](#id11-3)
4. [Recuperar contraseña](#id11-4)

### Inicio de sesión<a name="id11-1"></a>

1. Crear una nueva app llamada registration y ponerla en el settings.py <b>(Arriba del todo para darle prioridad respecto a las otras)</b>
```python
INSTALLED_APPS = [
    'registration.apps.RegistrationConfig',
```
2. En el fichero <b>urls.py</b> global, incluir una path que contenga las urls defenidas para la utenticación con django usando <b>django.contrib.auth.urls</b>

```python
urlpatterns = [
	....
    path('accounts/', include('django.contrib.auth.urls'))
]
```

Con esto, se darán de alta multitudes de URL para hacer efectiva la autenticación:
- accounts/ login/ [name='login']
- accounts/ logout/ [name='logout']
- accounts/ password_change/ [name='password_change']
- accounts/ password_change/done/ [name='password_change_done']
- accounts/ password_reset/ [name='password_reset']
- accounts/ password_reset/done/ [name='password_reset_done']
- accounts/ reset/<uidb64>/<token>/ [name='password_reset_confirm']
- accounts/ reset/done/ [name='password_reset_complete']

3. Por lo tanto para el iniciar sesión es necesario preparar una template login.html en templates/registration/login.html que tenga el formulario de login.

```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Iniciar sesión{% endblock %}
{% block content %}
<style>.errorlist{color:red;}</style>
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto mb-5">
        <form action="" method="post">{% csrf_token %}
          <h3 class="text-center mb-4">Iniciar sesión</h3>
          {% if form.non_field_errors %}
            <p style="color:red">Usuario o contraseña incorrectos, prueba de nuevo.</p>
          {% endif %}
          <p>
            <input type="text" name="username" autofocus maxlength="254" required
              id="id_username" class="form-control" placeholder="Nombre de usuario"/>
          </p>
          <p>
            <input type="password" name="password" required
              id="id_password" class="form-control" placeholder="Contraseña"/>
          </p>
          <p><input type="submit" class="btn btn-primary btn-block" value="Acceder"></p>
        </form>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```

4. Con esto iniciará sesión pero es necesario cambiar la ruta de redirección para cuando se complete el Login. Esto se hace en settings.py con la 
constante: <b>LOGIN_REDIRECT_URL = 'home'</b>
De esta forma, cuando el usuario se loguea, se redirige a la página principal

### Cerrar sesión<a name="id11-2"></a>

1. Se implementan los botones de login y logout en el menú de la vista. Debido a que django ya pone por defecto estas url pattern los nombres login y logout
solo hace falta indicarlo

```html
            <ul class="navbar-nav">

              {% if not request.user.is_authenticated %}
              <li class="nav-item">
                <a class="nav-link" href="{% url 'login' %}">
                  Login
                </a>
              </li>
              {% else %}
              
              <li class="nav-item">
                <a class="nav-link" href="{% url 'logout' %}">
                  Logout
                </a>
              </li>

              {% endif %}

            </ul>
```

2. En el settings.py indicar la ruta a la que se tiene que ir al cerrar sesión con la constante: <b>LOGOUT_REDIRECT_URL = 'home'</b>

### Registro<a name="id11-3"></a>

1. Es necesario incluir en la urls.py global con el include refiriendose a la nueva app registration ya que se va a crear una vista:

```html
urlpatterns = [
	.....
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('registration.urls'))
]
```
2. Es necesario crear una vista CreateView que utilice un formulario para crear usuarios ya implementado en Django llamado: UserCreationForm
También indicar la success_url y el template del registro

```html
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy

class SignUpCreateView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse_lazy('login')+'?register'
```

3. Crear el template del registro

```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Registro{% endblock %}
{% block content %}
<style>.errorlist{color:red;}</style>
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto mb-5">
        <form action="" method="post">{% csrf_token %}
          <h3 class="text-center mb-4">Registro</h3>
          {{form.as_p}}
          <p><input type="submit" class="btn btn-primary btn-block" value="Registrarse"></p>
        </form>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```

4. Crear el archivo urls.py que incluya la ruta de registro y la vista que lo maneja.

```python
from django.urls import path, include
from .views import SignUpCreateView

urlpatterns = [
    path('signup/', SignUpCreateView.as_view(), name='signup')
]
```

5. Mejorar la apariencia del formulario

Para mejorar y personalizar el formulario que se crea automáticamente desde django, se necesita implementar el método get_form en la vista:

```python
class SignUpCreateView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse_lazy('login')+'?register'

    def get_form(self, form_class=None):
        form = super().get_form()
        # Modificar el formulario a tiempo real
        form.fields['username'].widget = forms.TextInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Nombre de usuario'}
            )
        form.fields['password1'].widget = forms.PasswordInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Contraseña'}
            )
        form.fields['password2'].widget = forms.PasswordInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Confirmar Contraseña'}
            )
        return form
```

6. Añadir que el email sea obligatorio al registrarse

Para hacer esto es necesario crear un fichero forms.py donde se va a crear un formulario que herede de UserCreationForm para poder modificarlo a gusto.
En esta clase se añade el email y se crea la clase Meta que contendrá el modelo y los campos del formulario:

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserCreationFormWithEmail(UserCreationForm):
    
    email = forms.EmailField(required=True, help_text='Requerido, 254 carácteres como máximo y debe ser válido.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
```

Ahora en la vista se tiene que registrar la vista incluyendo el formulario creado en el forms.py:

```python
class SignUpCreateView(CreateView):
    form_class = UserCreationFormWithEmail
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse_lazy('login')+'?register'

    def get_form(self, form_class=None):
        form = super().get_form()
        # Modificar el formulario a tiempo real
        form.fields['username'].widget = forms.TextInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Nombre de usuario'}
            )
        form.fields['email'].widget = forms.EmailInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Dirección email'}
            )
        form.fields['password1'].widget = forms.PasswordInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Contraseña'}
            )
        form.fields['password2'].widget = forms.PasswordInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Confirmar Contraseña'}
            )
        return form
```

Para validar que el email sea único, se tiene que modificar el formulario e incluir un método clean_[parámetro_para_comprobar].
Para esto se utiliza la función <b>self.cleaned_data.get('parametro')</b> para recuperar el campo que ha escrito el usuario en el formulario antes que se procese el formulario.
Con esto se pueden hacer las comprobaciones pertinentes y si falla devolver un <b>ValidationError</b>

```python
class UserCreationFormWithEmail(UserCreationForm):
    
    email = forms.EmailField(required=True, help_text='Requerido, 254 carácteres como máximo y debe ser válido.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
   
    def clean_email(self):
        
        # Con esto se recupera el email que ha puesto el usuario antes de que se procese el formulario
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('El email ya está registrado, prueba con otro')
        return email
```

### Recuperar contraseña<a name="id11-4"></a>


[Documentación Email Backend](https://docs.djangoproject.com/en/4.0/topics/email/#email-backends)
[Templates registration](https://github.com/django/django/tree/main/django/contrib/admin/templates/registration)


1. Se puede hacer con un servidor SMTP de pruebas. Para ello ir al settings e incluir este SMTP de pruebas:

```python
import os
# EMAILS
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
else:
    # Aquí hay que configurar un email real para producción

```

2. Incluir las 4 templates que requiere el cambio de contraseña:

- <b>password_reset_form.html</b>
```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Restablecer contraseña{% endblock %}
{% block content %}
<style>.errorlist{color:red;}</style>
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto mb-5">
        <form action="" method="post">{% csrf_token %}
          <h3 class="mb-4">Restablecer contraseña</h3>
          <p>¿Ha olvidado su clave? Introduzca su dirección de correo a continuación y le enviaremos por correo electrónico las instrucciones para establecer una nueva.</p>
          {{ form.email.errors }}
          <p><input type="email" name="email" maxlength="254" required="" id="id_email" class="form-control" placeholder="Introduce tu email"/></p>
          <p><input type="submit" class="btn btn-primary btn-block" value="Confirmar"></p>
        </form>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```
- <b>password_change_done.html</b>
```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Restablecimiento de contraseña enviado{% endblock %}
{% block content %}
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto mb-5">
        <h3 class="mb-4">Restablecimiento de contraseña enviado</h3>
        <p>Le hemos enviado por email las instrucciones para restablecer la contraseña, si es que existe una cuenta con la dirección electrónica que indicó. Debería recibirlas en breve.</p>
        <p>Si no recibe un correo, por favor asegúrese de que ha introducido la dirección de correo con la que se registró y verifique su carpeta de spam.</p>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```
- <b>password_reset_confirm.html</b>
```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Escriba la nueva contraseña{% endblock %}
{% block content %}
<style>.errorlist{color:red;}</style>
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto mb-5">
        {% if validlink %}
          <form action="" method="post">{% csrf_token %}
            <h3 class="mb-4">Escriba la nueva contraseña</h3>
            <p>Por favor, introduzca su contraseña nueva dos veces para verificar que la ha escrito correctamente.</p>
            {{form.new_password1.errors}}
            <p><input type="password" name="new_password1" required="" id="id_new_password1" class="form-control" placeholder="Introduce la nueva contraseña"></p>
            {{form.new_password2.errors}}
            <p><input type="password" name="new_password2" required="" id="id_new_password2" class="form-control" placeholder="Repite la nueva contraseña"></p>
            <p><input type="submit" class="btn btn-primary btn-block" value="Cambiar mi contraseña"></p>
          </form>
        {% else %}
          <h3 class="mb-4">Restablecimiento de contraseñas fallido</h3>
          <p>El enlace de restablecimiento de contraseña era inválido, seguramente porque se haya usado antes. Por favor, solicite un nuevo restablecimiento de contraseña <a href="{% url 'password_reset' %}">aquí</a>.</p>
        {% endif %}
      </div>
    </div>
  </div>
</main>
{% endblock %}
```
- <b>password_reset_complete.html</b>
```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Restablecimiento de contraseña completado{% endblock %}
{% block content %}
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto mb-5">
        <h3 class="mb-4">Restablecimiento de contraseña completado  </h3>
        <p>Su contraseña ha sido establecida. Ahora puede seguir adelante e iniciar sesión.</p>
        <p><a href="{% url 'login' %}">Iniciar sesión</a></p>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```

3. Por último añadir un enlace para ir a esta página de restablecimiento de contraseña como el siguiente:

```html
	<p>
		¿Ha olvidado su contraseña? Puede restaurarla <a href="{% url 'password_reset' %}">Aquí</a>
	</p>
```

---------------------------------------

## Perfil de usuario, relaciones entre modelos Django e imágenes en modelos, UpdateView sin indicar la PK<a name="id12"></a>

**Índice**   
1. [Modelo Profile con relación 1:1 User](#id12-1)
2. [Tener instalado Pillow para manejar imágenes](#id12-2)
3. [Configurar settings.py para crear las carpetas con los archivos media](#id12-3)
4. [Crear la vista para el formulario del perfil de usuario](#id12-4)
5. [Crear la template con el formulario profile_form.html y que acepte ficheros media](#id12-5)
6. [Actualizar la URL y el redirect de login en settings](#id12-6)
7. [No hace falta related_name en relaciones OneToOne](#id12-7)
8. [Mejorar aspecto del formulario del perfil de usuario](#id12-8)
9. [Incluir opción para editar email](#id12-9)
10. [Formulario para cambiar la contraseña](#id12-10)

### 1. Modelo Profile con relación 1:1 User<a name="id12-1"></a>

Ofrecer al usuario tres campos para el usuario: imagen avatar, un texto como biografía y un enlace a su página web.

Las relaciones entre modelos que existen con Django son:
- <b>models.OneToOneField: </b> (1:1) -> 1 usuario - 1 perfil
- <b>models.ForeignKeyField: </b> (N:1 Many To One) -> N usuario - 1 perfiles
- <b>models.ManyToManyField: </b> (N:N) -> N usuarios - N perfiles



```python
def custom_upload_to(instance, filename):
    old_instance = Profile.objects.get(pk=instance.pk)
    old_instance.avatar.delete()
    return 'profiles/'+filename


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=custom_upload_to, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True, max_length=200)

    class Meta:
        verbose_name = ("Perfil")
        verbose_name_plural = ("Perfiles")
        ordering = ['user__username']

    def __str__(self):
        return self.user.username
```
Para que la carpeta media se encuentre ordenada, es necesario crear una carpeta para cada modelo. Para que se cree de forma automática cuando
se cree una instancia del modelo, es necesario modificar el campo imagen del modelo con el atributo <b>upload_to='carpeta'</b> indicando el nombre
de la carpeta para este modelo.

<b>Pero con el atributo upload_to asignandole solo la carpeta, el problema que se tiene es que cuando el usuario cambia el avatar, se almacena el nuevo y el antiguo. Para que se elimine el viejo y
quedarse con el más reciente, se necesita escribir una nueva función para asignársela al upload_to</b>

[Documentación Upload_to](https://docs.djangoproject.com/en/4.0/ref/models/fields/#django.db.models.FileField.upload_to)


```python
def custom_upload_to(instance, filename):
    old_instance = Profile.objects.get(pk=instance.pk)
    old_instance.avatar.delete()
    return 'profiles/'+filename

...

avatar = models.ImageField(upload_to=custom_upload_to, null=True, blank=True)
```

### 2. Tener instalado Pillow para manejar imágenes<a name="id12-2"></a>

Cabe destacar que es necesario tener instalado Pillow en el entorno virtual para usar ImageField y servir archivos media.
Para ello, pipenv shell para activar el entorno virtual y una vez dentro, ejecutar <b>pip install Pilow </b>

### 3. Configurar settings.py para crear las carpetas con los archivos media<a name="id12-3"></a>


Django por defecto no maneja el contenido multimedia y cuando se añade una imagen en un registro en el panel de administración, también se añade en el
directorio raíz.

Para esto, hay que crear en el directorio raíz una carpeta llamada <b>media</b> para almacenar ahí las imágenes.
Para cambiar la ubicación por defecto, ir al <b>settings.py</b> y añadir estas línes al final que lo que hace es establecer la ruta
para guardar las imágenes.

```python
# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

Para ver los ficheros media dentro de desarrollo:

Modificar el archivo urls.py. Primero se comprueba si está en modo DEBUG. Si es así, se importa static que permite servir ficheros estáticos.
Despues a urlPatters se concatena con la función static() junto con los enlaces de las variables creadas anteriormente: MEDIA_URL y MEDIA_ROOT

```python
urlpatterns = [
    path('',views.home,name="home"),
    path('about-me/',views.about,name="about"),
    path('portfolio/',views.portfolio,name="portfolio"),
    path('contact/',views.contact,name='contact'),
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    from django.conf.urls.static import static #static que permite servir ficheros estáticos
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4. Crear la vista para el formulario del perfil de usuario<a name="id12-4"></a>

```python
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import Profile

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = Profile
    fields = ['avatar', 'bio', 'link']
    success_url = reverse_lazy('profile')
    template_name = 'registration/profile_form.html'

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
```
<b>Al crear una UpdateView Django por defecto pide que en la URL haya una primary key o id. Pero esto no siempre es seguro mostrarlo. Por lo tanto,
hay otra alternativa y es redefinir el método get_object que lo que va a hacer es recuperar el perfil a través de la request con el objeto user y de esta
forma se podrá devolver el perfil a la template sin necesidad de incluir la id en la url</b>


Destacar que esta vista solo estará disponible para aquellos usuarios autenticados. Esto se marca con el decorador @method_decorator(login_required, name='dispatch')

### 5. Crear la template con el formulario profile_form.html  <a name="id12-5"></a>

<b>Para aceptar imágenes en el formulario, es necesario escribir: enctype="multipart/form-data"</b>

```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Perfil{% endblock %}
{% block content %}
<style>
    .errorlist{
        color:red;
    } 
    label{
        display:none
    }<
</style>
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto mb-5">
        <form action="" method="post" enctype="multipart/form-data">{% csrf_token %}
          <div class="row">
            <!-- Previa del avatar -->
            <div class="col-md-2">
              {% if request.user.profile.avatar %}
                <img src="{{request.user.profile.avatar.url}}" class="img-fluid">
                <p class="mt-1">¿Borrar? <input type="checkbox" id="avatar-clear" name="avatar-clear" /></p>
                {% else %}
                <img src="{% static 'registration/img/no-avatar.jpg' %}" class="img-fluid">
                {% endif %}
            </div>
            <!-- Formulario -->
            <div class="col-md-10">
              <h3>Perfil</h3>
              <input type="file" name="avatar" class="form-control-file mt-3" id="id_avatar">
              {{ form.bio }}
              {{ form.link }}
              <input type="submit" class="btn btn-primary btn-block mt-3" value="Actualizar">
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```

### 6. Actualizar la URL y el redirect de login en settings <a name="id12-6"></a>

```python
urlpatterns = [
    path('signup/', SignUpCreateView.as_view(), name='signup'),
    path('profile/', ProfileUpdateView.as_view(), name='profile')
]
```

Ahora una vez el usuario inicie sesión hace falta que lo redirecione a esta página. Esto se tiene que comentar en SETTINGS:

```python
# AUTHENTICATION settings
#comentar LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
```

### 7. No hace falta related_name en relaciones OneToOne <a name="id12-7"></a>

En relaciones OneToOne, no es necesario tener un related_name para referirse al objeto a la inversa. Ya viene implícito, por lo tanto,
en el ejemplo, se tiene una relación en que 1 Perfil tiene 1 Usuario. 
En la vista se podría hacer esto para acceder a los campos del profile

```python
{{request.user.profile.link}}
```

### 8. Mejorar aspecto del formulario del perfil de usuario <a name="id12-8"></a>

Para ello hay que crear un ModelForm para poner con bootstrap los campos.

```python
class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('avatar', 'bio', 'link')
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control-file mt-3'}),
            'bio': forms.Textarea(attrs={'class': 'form-control mt-3', 'rows': 1, 'placeholder': 'Biografía'}),
            'link': forms.URLInput(attrs={'class': 'form-control mt-3', 'placeholder': 'Enlace'})
        }
```

Cabe destacar que hay que indicarlo en la vista y se tiene que eliminar los campos fields ya que son indicados en el formulario:

```python
@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileForm
    success_url = reverse_lazy('profile')

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
```

### 9. Incluir opción para editar email <a name="id12-9"></a>

Al tener una UpdateView, solo modifica el modelo seleccionado por lo tanto, con la UpdateView no se va a poder modificar el email ni la contraseña.
Para ello, sí que se puede crear un enlace para acceder a un formulario para modificar estos dos campos.
Así que primero agregar un botón en el formulario

```html
            <!-- Formulario -->
			<form>
				.....
              <p class="mt-3">Si desea editar su email haga clic <a href="{% url 'profile_email' %}""></a></p>
              <input type="submit" class="btn btn-primary btn-block mt-3" value="Actualizar">
			 ....
			 </form>
```
Después en forms.py hay que crear un nuevo formulario para el modelo usuario para modificar el email

```python
class EmailForm(forms.ModelForm):
    
    email = forms.EmailField(required=True, help_text='Requerido, 254 carácteres como máximo y debe ser válido.')

    class Meta:
        model = User
        fields = ['email']
    
    def clean_email(self):
        
        # Con esto se recupera el email que ha puesto el usuario antes de que se procese el formulario
        email = self.cleaned_data.get("email")

        if 'email' in self.changed_data: #para comprobar que el campo email del formulario ha cambiado
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('El email ya está registrado, prueba con otro')
        return email
```

### 10. Formulario para cambiar la contraseña<a name="id12-10"></a>

Cambio de la contraseña a partir de un formulario.
Primero, se pone un botón al igual que con el email. 
```html
            <!-- Formulario -->
			<form>
				.....
              <p class="mt-3">Si desea editar su email haga clic <a href="{% url 'profile_email' %}""></a></p>
			  <p class="mt-3">Si quieres cambiar tu contraseña, haz clic <a href="{% url 'password_change' %}">Aquí</a></p>
              <input type="submit" class="btn btn-primary btn-block mt-3" value="Actualizar">
			 ....
			 </form>
```

Tendrá la ruta <b>password_change</b> que viene por defecto cuando definimos el url_patterns global.

Ahora solo hace falta crear las dos templates que pide esta URL por defecto que se llaman: 

- <b>password_change_form.html</b>
```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Cambio de contraseña{% endblock %}
{% block content %}
<style>.errorlist{color:red;}</style>
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto mb-5">
        <form action="" method="post">{% csrf_token %}
            <h3 class="mb-4">Cambio de contraseña</h3>
            <p>Por favor, introduzca su contraseña antigua por seguridad, y después introduzca dos veces la nueva contraseña para verificar que la ha escrito correctamente.</p>
            {{form.old_password.errors}}
            <p><input type="password" name="old_password" autofocus="" required="" id="id_old_password"class="form-control" placeholder="Contraseña antigua"></p>
            {{form.new_password1.errors}}
            <p><input type="password" name="new_password1" required="" id="id_new_password1" class="form-control" placeholder="Contraseña nueva"></p>
            {{form.new_password2.errors}}
            <p><input type="password" name="new_password2" required="" id="id_new_password2" class="form-control" placeholder="Contraseña nueva (confirmación)"></p>
            <p><input type="submit" class="btn btn-primary btn-block" value="Cambiar mi contraseña"></p>
        </form>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```
- <b>password_change_done.html</b>
```html
{% extends 'core/base.html' %}
{% load static %}
{% block title %}Contraseña cambiada correctamente{% endblock %}
{% block content %}
<main role="main">
  <div class="container">
    <div class="row mt-3">
      <div class="col-md-9 mx-auto mb-5">
        <h3 class="mb-4">Contraseña cambiada correctamente</h3>
        <p>Puedes volver a tu perfil haciendo clic <a href="{% url 'profile' %}">aquí</a>.</p>
      </div>
    </div>
  </div>
</main>
{% endblock %}
```

---------------------------------------

## Señales <a name="id13"></a>

[Información Signals](https://docs.djangoproject.com/en/4.0/topics/signals/)


Una señal es un disparador que se llama automáticamente después de un evento que ocurre un ORM.

Pueden ocurrir errores en el que cuando se registra un usuario no siempre rellena su perfil.
Por lo tanto, con las señales cada vez que un usuario se registra va a tener que editar su perfil.

Entonces es necesario ir al modelo y crear una nueva función (fuera del modelo) con el decorador <b>receiver</b> y dentro post_save,es decir, 
que se ejecute después de guardar el modelo. Y el modelo se indica con el <b>sender=[Modelo]</b>.
Con los kwargs se puede comprobar si es la primera vez que se crea la instancia del modelo, ideal para hacer una comprobación y si es la primera vez, crear
el perfil con los datos del usuario:

```python
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profiles', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True, max_length=200)

    class Meta:
        verbose_name = ("Perfil")
        verbose_name_plural = ("Perfiles")

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, **kwargs):
    ## Comprobar que solo sea de creación y es la primera vez que se guarda esta intancia
    if kwargs.get('created', False):
        Profile.objects.get_or_create(user=instance)
        print('Se acaba de crear un usuario y su perfil enlazado')
```

---------------------------------------

## Pruebas unitarias Django <a name="id14"></a>

[Información Pruebas Unitarias](https://docs.djangoproject.com/en/4.0/topics/testing/overview/)

Se va a hacer una prueba unitaria con Django para comprobar el ejemplo anterior de las señales: <a name="id14">Señales</a>

Para crear una prueba unitaria con Django, es necesario ir a <b>test.py</b> de la aplicación y escribir dentro la prueba.
Primero crear una clase que contendrá todas las pruebas y heredará de TestCase.
En el método setUp se incluyen las primeras acciones antes de ejecutar los test.
Y al definir la prueba unitaria se debe de poner delante test_[nombre]

```python
from django.test import TestCase
from .models import Profile
from django.contrib.auth.models import User

# Create your tests here.
class ProfileTest(TestCase):
    def setUp(self):
        User.objects.create_user('test','test@test.com', 'test1234')

    def test_profile_exists(self):
        exists = Profile.objects.filter(user__username="test").exists()
        self.assertEqual(exists, True)
```

Para ejecutarlo: 
```shell
python manage.py test [nombre_app]
```

---------------------------------------

## App de Chat/Mensajería, TDD, M2M Changed, Model Manager<a name="id15"></a>

- WHO: Un usuario registrado e identificado
- WHAT: Un chat privado entre el usuario y otros usuarios para comunicarse
- WHEN: Cuando un usuario decida comunicarse
- WHERE: EN su sección de Mensajes o a través de un botón de enviar mensaje
- WHY: Para ofrecer una vía de comunicación

Crear una app con dos modelos:

1. Message

- usuario_emisor (FK_USER)
- contenido (TEXT)
- fecha_creación (DateTime)

2. Thread
- Usuarios (M2M User)
- Mensajes (M2M Message)

```python
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ("Mensaje")
        verbose_name_plural = ("Mensajes")

class Thread(models.Model):
    users = models.ManyToManyField(User, related_name="threads")
    messages = models.ManyToManyField(Message)
	
    # Los campos ManyToMany no afectan al updated, se actualizan con la señal
    updated = models.DateTimeField(auto_now=True)
```

Para comprobar que un hilo solo pueda aceptar mensajes de usuarios que estén en ese hilo, es necesario crear una señal pre_add con la señal m2m-changed:
[Información M2M Changed](https://docs.djangoproject.com/en/4.0/ref/signals/#m2m-changed)


```python

class Thread(models.Model):

	.............


# Señal para hacer que un hilo solo pueda recibir mensajes de usuario que sí estén en el hilo
def messages_changed(sender, **kwargs):
    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action', None)
    pk_set = kwargs.pop('pk_set', None)
    print(instance, action, pk_set)

    false_pk_set = set()
    if action is 'pre_add':
        for msg_pk in pk_set:
            msg = Message.objects.get(pk=msg_pk)
            if msg.user not in instance.users.all():
                print('El usuario ({}) no forma parte del hilo'.format(msg.user))
                false_pk_set.add(msg_pk)
        
    # Borrar los mensajes que no forman parte del hilo
    # Metodo conjuntos A-B
    pk_set.difference_update(false_pk_set)
	
	# Forzar para actualizar el update del modelo
    instance.save()

m2m_changed.connect(messages_changed, sender=Thread.messages.through)
```


TDD se basa primero en hacer primero las pruebas y luego el desarrollo.
Por lo tanto, se va a crear primero las pruebas en el fichero test.py


```python
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Thread, Message

class ThreadTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', None, 'test1234')
        self.user2 = User.objects.create_user('user2', None, 'test1234')
        self.user3 = User.objects.create_user('user3', None, 'test1234')
        self.thread = Thread.objects.create()
    
    # Comprueba que se añaden los usuarios en el modelo Thread
    def test_add_users_to_thread(self):
        self.thread.users.add(self.user1, self.user2)
        self.assertEqual(len(self.thread.users.all()), 2)
    
    # Recuperar un hilo existente a partir de sus usuarios
    def test_filter_thread_by_users(self):
        self.thread.users.add(self.user1, self.user2)
        threads = Thread.objects.filter(users=self.user1).filter(users=self.user2)
        self.assertEqual(self.thread, threads[0])
    
    # Comprobar que no existe un thread si no existe usuario
    def test_filter_non_existent_thread(self):
        threads = Thread.objects.filter(users=self.user1).filter(users=self.user2)
        self.assertEqual(0, len(threads))
    
    # Comprobar que se añaden mensajes a los hilos
    def test_add_messages_to_thread(self):
        self.thread.users.add(self.user1, self.user2)
        message1 = Message.objects.create(user=self.user1, content='Buenas')
        message2 = Message.objects.create(user=self.user2, content='Hola')

        self.thread.messages.add(message1, message2)
        self.assertEqual(2, len(self.thread.messages.all()))
    
    # Comprobar que un usuario no pueda añadir un mensaje al hilo si no pertenece a él
    def test_add_message_from_user_not_in_thread(self):
        self.thread.users.add(self.user1, self.user2)
        message1 = Message.objects.create(user=self.user1, content='Buenas')
        message2 = Message.objects.create(user=self.user2, content='Hola')
        message3 = Message.objects.create(user=self.user3, content='Soy Espia')
        
        self.thread.messages.add(message1, message2, message3)
        self.assertEqual(len(self.thread.messages.all()), 2)
```


### Model Manager

[Información Model Manager](https://docs.djangoproject.com/en/4.0/topics/db/managers/)

- Un <b>ModelManager</b> es un manejador de las querys del modelo. Hace que se puedan programar y simplificar las consultas con métodos propios y definidos:

```python
class ThreadManager(models.Manager):
    def find(self, *arguments):

        for i, user in enumerate(arguments):
            if i==0:
                queryset = self.filter(users=user)
            else:
                queryset = queryset.filter(users=user)
        if len(queryset) > 0:
            return queryset[0]
        return None

    def find_or_create(self, *arguments):
        thread = self.find(*arguments)
        if thread is None:
            thread = Thread.objects.create()
            for user in arguments:
                thread.users.add(user)
        return thread

class Thread(models.Model):
    users = models.ManyToManyField(User, related_name="threads")
    messages = models.ManyToManyField(Message)
	
	# Los campos ManyToMany no afectan al updated, se actualizan con la señal
    updated = models.DateTimeField(auto_now=True)

    objects = ThreadManager()
```

Y se podrá usar como función:

```python
    # Consultas con el ModelManager
    def test_find_thread_with_custom_manager(self):
        self.thread.users.add(self.user1, self.user2)
        thread = Thread.objects.find(self.user1, self.user2)
        self.assertEqual(self.thread, thread)

    def test_find_or_create_thread_with_custom_manager(self):
        self.thread.users.add(self.user1, self.user2)
        thread = Thread.objects.find_or_create(self.user1, self.user2)
        self.assertEqual(self.thread, thread)

        thread = Thread.objects.find_or_create(self.user1, self.user3)
        self.assertIsNotNone(thread)
```

Después crear las vistas para listar los threads del usuario y el detalle de los thread:

```python
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Thread
from django.http import Http404

@method_decorator(login_required, name='dispatch')
# Create your views here.
class ThreadListView(TemplateView):
    template_name = "messenger/thread_list.html"

    """ Filtrar solo los mensajes del usuario conectado
    No hace falta puesto que se puede usar el related para filtrar en la template
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(users=self.request.user)
    """

class ThreadDetailView(DetailView):
    model = Thread

    def get_object(self):
        obj = super().get_object()
        if self.request.user not in obj.users.all():
            raise Http404()
        return obj
```


### Peticiones Asíncronas JS

[Información Peticiones Asíncronas JS](https://docs.hektorprofe.net/django/web-playground/mensajes-asincronos-javascript-1/)

Se crearía un script Javascript y se usaría el método fetch para enviar una petición en la URL:

```html
	<!-- Aquí crearemos el formulario -->
	<textarea id="content" class="form-control mb-2" rows="2" placeholder="Escribe tu mensaje aquí"></textarea>
	<button id="send" type="button" class="btn btn-primary btn-sm btn-block" disabled>Enviar</button>
	<script>
		
	  var send = document.getElementById("send");
	  send.addEventListener("click", function(){
		var content = encodeURIComponent(document.getElementById("content").value); // &
		if (content.length > 0){
		  const url = "{% url 'messenger:add' thread.pk %}" + "?content="+content;
		  fetch(url, {'credentials':'include'}).then(response => response.json()).then(function(data){
			// Si el mensaje se ha creado correctamente...
			if (data.created) {
			  var message = document.createElement('div')
			  message.classList.add('mine','mb-3')
			  message.innerHTML = '<small><i>Hace unos segunos</i></small><br>'+decodeURIComponent(content)
			  document.getElementById('thread').appendChild(message)
			  ScrollBottomInThread()
			  document.getElementById("content").value = ''
			  send.disabled = true
			} else {
			  // Si algo ha ido mal podemos debugear en la consola del inspector
			  console.log("Algo ha fallado y el mensaje no se ha podido añadir.")
			}
		  })
		  
		}
	  })

	  /* Evento que activa o desactiva el botón dependiendo de si hay*/
	  var textArea = document.getElementById("content")
	  textArea.addEventListener("keyup",function(){
		send.disabled = !this.checkValidity() || !this.value ? true : false
	  })

	  /* Forzar scroll to bottom*/
	  function ScrollBottomInThread(){
		var thread = document.getElementById("thread")
		thread.scrollTop = thread.scrollHeight
	  }
	  ScrollBottomInThread()
	</script>
```

Y en la vista sería:

```python

def add_message(request, pk):
    json_response = {'created':False}
    if request.user.is_authenticated:
        content = request.GET.get('content',None)
        if content:
            thread = get_object_or_404(Thread, pk=pk)
            message = Message.objects.create(user=request.user, content=content)
            thread.messages.add(message)
            json_response['created'] = True
    else:
        raise Http404('User is not authenticated')

    # Convierte Dict a JSON
    return JsonResponse(json_response)
```

## Django MYSQL <a name="id16"></a>

1. Instalar MySQL 

[Instalar MYSQL](https://dev.mysql.com/downloads/installer/)

Instalando MySQL Workbench y MySQL Server

2. Crear base de datos y super usuario

```sql:
CREATE DATABASE nombreDB

CREATE USER nombreusuario@localhost IDENTIFIED BY 'pass';
GRANT ALL PRIVILEGES ON nombreDB.* TO nombreusuario@localhost;
FLUSH PRIVILEGES;
```

3. Instalar SQL en Django

Ejecutar: <b>pip install pymysql</b> en el entorno virtual

4. Importar pymysql en settings.py

5. Configuración

En __init__py, a la altura de settings.py, agregar lo siguiente para iniciar la base de datos MySQL:

```python:
import pymysql
pymysql.install_as_MySQLdb()
```

6. Editar settings.py

Eliminar la Database de desarrollo y añadir la de MySQL poniendo lo siguiente:

```python:
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases



"""
ELIMINAR

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'db_webplaygroundpython',
            'USER': 'marcos',
            'PASSWORD': '1234',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
```

7. Hacer las migraciones

Ejecutar <b>python manage.py makemigrations</b> y <b>python manage.py migrate</b>

## Django Deploy: Ngnix, Gunicorn y Docker<a name="id17"></a>

1. Tener instalado Docker

[Descargar Docker](https://www.docker.com/get-started/)

2. Configurar Gunicorn

Primero, ejecutar <b>pip install gunicorn</b> y ponerlo en el archivo <b>settings.py</b>
Después, el el directorio raíz añadir una carpeta config/gunicorn y crear el archivo <b>conf.py</b>
Este archivo tendrá lo siguiente:

```python:
name = 'webplaygroundpython'
loglevel = 'info'
errorlog = '-'
accesslog = '-'
workers = 2
```

3. Configurar Nginx

En la carpeta config creada anteriormente, añadir las carpetas config/nginx/conf.d que dentro tendrá el archivo <b>local.conf</b> con la siguiente configuración:

```conf:
upstream django_server {
    server localhost:8000;
}

server {
    listen 80;
    server_name localhost;

    location /static/ {
        alias /code/static/;
    }

    location / {
        proxy_pass http://django_server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

Es necesario que en el <b>settings.py</b> estén configurados los archivos estáticos con la siguiente dirección:

```python:
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = 'code/static/'

```

4. Crear el DockerFile

El archivo DockerFile sirve para crear una nueva imagen que tendrá todo lo necesario para ejecutar el proyecto python. Es necesario tener todas las dependecias en <b>requirements.txt</b> (con ese nombre). Esta imagen luego será utilizada por el contenedor en el docker-compose.yml
El archivo DockerFile tiene que estar a la altura del manage.pu tendrá lo siguiente:

```dockerfile:
FROM python:3.10.8

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
```

De esta manera los archivos estáticos necesarios para la app estarán en /code/code
Se ejecutará el fichero requirements.txt con todas las dependencias necesarias.

5. Crear el docker-compose

Teniendo en cuenta las imágenes mysql y nginx de Docker y la imagen que se ha creado en el DockerFile, ya se puede construir el docker-compose.yml (a la misma altura que el DockerFile)

```yml:
version: '3'

services:
  db:
    image: mysql:5.7
    ports:
      - '3306:3306'
    environment:
       MYSQL_DATABASE: 'db_webplaygroundpython'
       MYSQL_USER: 'marcos'
       MYSQL_PASSWORD: '1234'
       MYSQL_ROOT_PASSWORD: '1234'
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db

  nginx:
    image: nginx:1.13
    ports:
      - 8001:81
    volumes:
      - ./config/nginx/conf.d:/etc/nginx/conf.d
      - static:/code/static
    depends_on:
      - web

volumes:
  .:
  static:
```

6. Construir el contenedor

Ejecutar <b>docker compose build</b> y posteriormente levantar el contenedor con <b>docker compose up</b>

7. Shell de Docker

- Para ver las carpetas del contenedor y como están almacenados los archivos, se puede acceder con el comando: <b>docker exec -it <mycontainer> bash</b>
- Para ver la lista de contenedores: <b>docker container ls</b>
- Ver las imagenes en ejecución: <b>docker ps</b>

8. Ya esta desplegado y se puede acceder al localhost:8000
