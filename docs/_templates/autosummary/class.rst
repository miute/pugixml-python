{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   {%- set ns = namespace(has_own_methods=false, has_own_attrs=false) -%}
   {%- set exclude_members = ['__annotations_cache__', '__annotate_func__', '__doc__', '__format__', '__module__', '__new__', '__repr__', '_pybind11_conduit_v1_', '__pybind11_native_enum__'] -%}

   {%- for item in members -%}
      {%- if item not in attributes and
            item not in inherited_members and
            item not in exclude_members -%}
         {%- set ns.has_own_methods = true -%}
      {%- endif -%}
      {%- if item in attributes and item not in inherited_members -%}
         {%- set ns.has_own_attrs = true -%}
      {%- endif -%}
   {%- endfor -%}

   {% block METHODS %}
   {% if ns.has_own_methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
   {% for item in members %}
   {% if item not in attributes and
         item not in inherited_members and
         item not in exclude_members %}
      ~{{ name }}.{{ item }}
   {% endif %}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block DESCRIPTION %}
   {% if ns.has_own_methods %}
   .. rubric:: {{ _('Member Documentation') }}
   {% endif %}
   {% endblock %}
