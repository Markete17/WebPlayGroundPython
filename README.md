# WebPlayGroundPython

Toda la información en: [Información](https://docs.hektorprofe.net/django/web-playground/)

**Índice**   
1. [TemplateView: Vistas como objetos en vez de como funciones ](#id1)
2. [ListView y Paginación ](#id2)
3. [DetailView ](#id3)

## Vistas como objetos en vez de como funciones<a name="id1"></a>

[Información](https://docs.djangoproject.com/en/4.0/ref/class-based-views/)
[Información](https://ccbv.co.uk/)

Para este caso, el objeto que mejor se adapta al ejemplo es el <b>TemplateView</b>

De esta manera. Dentro de la clase se tiene que añadir la propiedad <b>template_name</b> y definir el método <b>get_context_data</b>

<pre><code>
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

</code></pre>

y en las urls.py se llama a la clase con el método as_view()

<pre><code>
from django.urls import path
from .views import SampleView, HomePageView
from . import views

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('sample/', SampleView().as_view(), name="sample"),
]
</code></pre>

También se puede hacer de esta forma y es parecido a lo que se hacía con las funciones y es definir el método <b>def get(self, request, *args, **kwargs)</b>

<pre><code>
class HomePageView(TemplateView):
    template_name = "core/home.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"title": 'Mi web'})
</code></pre>

## ListView y Paginación <a name="id2"></a>

[Información](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-display/#django.views.generic.list.ListView)

Igual que pasa con el TemplateView, para devolver una lista de objetos a la vista o el detalle de un modelo, se puede utilizar <b>ListView</b> y <b>DetailView</b>

1. ListView

Se importa la biblioteca: from django.views.generic.list import ListView

Y ahora en vez de tener una función que devuelve la lista de objetos, se tiene una clase ListView configurada de la siguiente manera:

Lo siguiente:
```python:
def pages(request):
    pages = get_list_or_404(Page)
    return render(request, 'pages/pages.html', {'pages':pages})
```

Se convierte en una clase ListView

```python:
class HomePageView(TemplateView):
    template_name = "core/home.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"title": 'Mi web'})
```

No olvidar que en el archivo urls.py hay que poner la clase creada con el método as_view().

```python:
urlpatterns = [
    path('', views.pages, name='pages'),
    path('<int:page_id>/<slug:page_slug>/', PageListView.as_view() , name='page'),
]```

En la vista se puede llamar a esta lista como {{object_list}} o el {{nombreModelo_list}}

### Paginación

Para hacer la paginación de este modelo, es necesario que la clase ListView tenga la propiedad <b>paginated_by</b> indicando el número de objetos que va a tener cada página.

```python:
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

```html:
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

## ListView y Paginación <a name="id3"></a>

[Información](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-display/#django.views.generic.detail.DetailView)

Pasa igual que como el ListView. En vez de crear una función render, se crea una clase que herede de DetailView:

```python:
class PageDetailView(DetailView):
    model = Page
    template_name = "pages/page.html"
```