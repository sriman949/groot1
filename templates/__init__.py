"""
Kubernetes resource templates for Groot CLI.
"""

import os
import jinja2

# Get the directory containing the templates
TEMPLATES_DIR = os.path.dirname(os.path.abspath(__file__))

# Create a Jinja2 environment for loading templates
template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    trim_blocks=True,
    lstrip_blocks=True
)

def get_template(template_name):
    """
    Get a Jinja2 template by name.

    Args:
        template_name (str): Name of the template file (e.g., 'deployment.yaml')

    Returns:
        jinja2.Template: The loaded template
    """
    return template_env.get_template(template_name)

def render_template(template_name, **kwargs):
    """
    Render a template with the given context.

    Args:
        template_name (str): Name of the template file (e.g., 'deployment.yaml')
        **kwargs: Context variables for the template

    Returns:
        str: The rendered template
    """
    template = get_template(template_name)
    return template.render(**kwargs)