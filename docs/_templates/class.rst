{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :noindex:

   {% block methods %}
   {% if methods %}
   Members:

   {# Show implemented members #}
   .. autosummary::
   {% for item in members %}
   {% if item not in inherited_members and item not in ['__annotations__', '__doc__', '__module__', '__repr__', '_pybind11_conduit_v1_'] %}
      ~{{ name }}.{{ item }}
   {% endif %}
   {%- endfor %}
   {% endif %}
   {% endblock %}
