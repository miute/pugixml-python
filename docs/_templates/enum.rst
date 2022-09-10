{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :noindex:
   :no-members:

{% block attributes %}
{% if attributes %}
{% for item in attributes %}
{% if item not in ['name', 'value'] %}
.. autoattribute:: {{ module }}.{{ item }}
   :noindex:
{% endif %}
{%- endfor %}
{% endif %}
{% endblock %}
