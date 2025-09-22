"""
Animal data HTML generator.

This script reads animal data from a JSON file and generates an HTML page
with styled cards for each animal.
"""

import json
import subprocess
from typing import Dict, List, Optional


def serialize_animal(animal: Dict) -> str:
    """
    Generate HTML card markup for a single animal.

    Args:
        animal: Dictionary containing animal data with 'name', 'characteristics',
               and 'locations' fields.

    Returns:
        str: HTML markup for the animal card or empty string if required fields missing.
    """
    characteristics = animal.get('characteristics', {})
    locations = animal.get('locations', [])
    name = animal.get('name')
    
    if not name:
        return ''
    
    # Building the card
    output = '<li class="cards__item">\n'
    output += f'  <div class="card__title">{name}</div>\n'
    output += '  <div class="card__text">\n'
    output += '    <ul class="card__details">\n'
    
    if diet := characteristics.get('diet'):
        output += f'      <li><strong>Diet:</strong> {diet}</li>\n'
    
    if locations:
        output += f'      <li><strong>Location:</strong> {locations[0]}</li>\n'
    
    if animal_type := characteristics.get('type'):
        output += f'      <li><strong>Type:</strong> {animal_type}</li>\n'
    
    output += '    </ul>\n'
    output += '  </div>\n'
    output += '</li>\n'
    
    return output


def read_json_file(filepath: str) -> List[Dict]:
    """
    Read and parse a JSON file.
    Args:
        filepath: Path to the JSON file.
    """
    with open(filepath, 'r') as file:
        return json.load(file)


def read_template_file(filepath: str) -> str:
    """
    Read an HTML template file.

    Args:
        filepath: Path to the template file.
    """
    with open(filepath, 'r') as file:
        return file.read()


def generate_html(animals: List[Dict], template: str) -> str:
    """
    Generate complete HTML by combining animal data with template.

    Args:
        animals: List of animal dictionaries to serialize.
        template: HTML template string containing __REPLACE_ANIMALS_INFO__ placeholder.
    """
    # Generate HTML for all animals
    animals_html = ''
    for animal in animals:
        animals_html += serialize_animal(animal)
    
    # Insert the generated HTML into the template
    return template.replace('__REPLACE_ANIMALS_INFO__', animals_html)


def write_html_file(filepath: str, content: str) -> None:
    """
    Write content to an HTML file.

    Args:
        filepath: Path where the file should be written.
        content: String content to write to the file.
    """
    with open(filepath, 'w') as file:
        file.write(content)


def get_available_skin_types(animals: List[Dict]) -> List[str]:
    """
    Extract all unique skin_type values from the animals data.

    Args:
        animals: List of animal dictionaries.

    Returns:
        Sorted list of unique skin_type values, including 'Unknown' for missing values.
    """
    skin_types = set()
    has_missing = False
    
    for animal in animals:
        characteristics = animal.get('characteristics', {})
        skin_type = characteristics.get('skin_type')
        
        if skin_type:
            skin_types.add(skin_type)
        else:
            has_missing = True
    
    result = sorted(list(skin_types))
    if has_missing:
        result.append('Unknown (missing skin_type)')
    
    return result


def get_user_skin_type_choice(available_types: List[str]) -> str:
    """
    Display available skin types and get user selection.

    Args:
        available_types: List of available skin type options.

    Returns:
        Selected skin type string.
    """
    print("\nAvailable skin types:")
    for i, skin_type in enumerate(available_types, 1):
        print(f"{i}. {skin_type}")
    
    while True:
        try:
            choice = input("\nEnter the number of your choice: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(available_types):
                selected = available_types[index]
                print(f"You selected: {selected}")
                return selected
            else:
                print(f"Please enter a number between 1 and {len(available_types)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nExiting...")
            exit(1)


def filter_animals_by_skin_type(animals: List[Dict], selected_skin_type: str) -> List[Dict]:
    """
    Filter animals by the selected skin type.

    Args:
        animals: List of all animal dictionaries.
        selected_skin_type: The skin type to filter by.

    Returns:
        List of animals matching the selected skin type.
    """
    filtered_animals = []
    
    for animal in animals:
        characteristics = animal.get('characteristics', {})
        skin_type = characteristics.get('skin_type')
        
        # Handle the "Unknown" case
        if selected_skin_type == 'Unknown (missing skin_type)':
            if not skin_type:  # Missing skin_type
                filtered_animals.append(animal)
        else:
            if skin_type == selected_skin_type:
                filtered_animals.append(animal)
    
    return filtered_animals


def compile_less_to_css(less_file: str, css_file: str) -> None:
    """
    Compile LESS file to CSS using lessc command.

    Args:
        less_file: Path to the input LESS file.
        css_file: Path to the output CSS file.

    Raises:
        subprocess.CalledProcessError: If lessc compilation fails.
    """
    try:
        subprocess.run(['lessc', less_file, css_file], check=True, capture_output=True)
        print(f"Successfully compiled {less_file} to {css_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling LESS: {e.stderr.decode()}")
        raise
    except FileNotFoundError:
        print("Error: lessc not found. Install with: npm install -g less")
        raise


def main() -> None:
    try:
        # Compile LESS to CSS
        compile_less_to_css('styles.less', 'styles.css')
        
        # Read input files
        animals_data = read_json_file('animals_data.json')
        template = read_template_file('animals_template.html')
        
        # Get available skin types and user selection
        available_skin_types = get_available_skin_types(animals_data)
        
        if not available_skin_types:
            print("No skin types found in the data.")
            return
        
        selected_skin_type = get_user_skin_type_choice(available_skin_types)
        
        # Filter animals by selected skin type
        filtered_animals = filter_animals_by_skin_type(animals_data, selected_skin_type)
        
        if not filtered_animals:
            print(f"No animals found with skin type: {selected_skin_type}")
            return
        
        print(f"\nFound {len(filtered_animals)} animals with skin type '{selected_skin_type}'")
        
        # Generate and write HTML
        html_content = generate_html(filtered_animals, template)
        write_html_file('animals.html', html_content)
        
        print("Successfully generated animals.html!")

    except FileNotFoundError as e:
        print(f"Error: Required file not found - {e.filename}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in animals_data.json")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
