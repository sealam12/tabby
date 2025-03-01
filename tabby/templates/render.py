from jinja2 import Environment, FileSystemLoader

class JinjaTemplateRenderer:
    def __init__(self, template_dir: str):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render(self, template_name: str, context: dict) -> str:
        template = self.env.get_template(template_name)
        return template.render(context)

# Example usage
if __name__ == "__main__":
    # Create a directory named 'templates' and place a file named 'greeting.html' inside it
    # greeting.html content:
    # Hello, {{ name }}! Welcome to {{ place }}.

    renderer = JinjaTemplateRenderer(template_dir='')
    context = {
        "name": "Alice",
        "place": "Wonderland"
    }
    
    result = renderer.render('example_template.html', context)
    print(result)  # Output: Hello, Alice! Welcome to Wonderland.