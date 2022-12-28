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


## Vistas como objetos en vez de como funciones<a name="id1"></a>

[Información](https://docs.djangoproject.com/en/4.0/ref/class-based-views/)
[Información](https://ccbv.co.uk/)

Para este caso, el objeto que mejor se adapta al ejemplo es el <b>TemplateView</b>

De esta manera. Dentro de la clase se tiene que añadir la propiedad <b>template_name</b> y definir el método <b>get_context_data</b>

```python
def home(request):
    return render(request, "core/home.html", {"title": 'Mi web'})
</code></pre>
seria:
<pre><code>
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
    paginate_by = 10
    template_name = "pages/pages.html"
</code></pre>
```

Ahora en la vista se puede utilizar la paginación utilizando {{page_obj}} y algunos atributos que tiene este objeto como por ejemplo:

- <b>page_obj.has_previous:</b> saber si hay una página antes. 
- <b>page_obj.has_next:</b> saber si hay una página después
- <b>page_obj.previous_page_number:</b> saber el número de página anterior
- <b>page_obj.next_page_number:</b> saber el número de página siguiente
- <b>page_obj.number:</b> saber el número de página actual
- <b>page_obj.paginator.num_pages:</b> saber el número de páginas totales

Un ejemplo es: 

```html
<main role="main">
  <div class="container mb-4">
    {% for page in page_obj %}
      <div class="row mt-3">
        <div class="col-md-9 mx-auto">
          <h2 class="mb-4">{{page.title}}</h2>
          <div>
            <p>{{page.content|striptags|safe|truncatechars:"200"}}</p>
            <p><a href="{% url 'page' page.id page.title|slugify %}">Leer más</a>
              <!--
              {% if request.user.is_staff %}
                | <a href="#">Editar</a>
                | <a href="#">Borrar</a>
              {% endif %}
              -->
            </p>
          </div>
        </div>
      </div>
    {% endfor %}
  </div>
  <div class="d-flex justify-content-center">
    <span class="step-links">
        {% if page_obj.has_previous %}
            <a href="?page=1">&laquo; first</a>
            <a href="?page={{ page_obj.previous_page_number }}">previous</a>
        {% endif %}

        <span class="current">
            Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}.
        </span>

        {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}">next</a>
            <a href="?page={{ page_obj.paginator.num_pages }}">last &raquo;</a>
        {% endif %}
    </span>
</div>
</main>
</code></pre>
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
- [Información Documentación](https://docs.djangoproject.com/en/4.0/topics/class-based-views/mixins/)

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