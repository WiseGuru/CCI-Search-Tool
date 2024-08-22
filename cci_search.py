import os
import xml.etree.ElementTree as ET
import re
import subprocess
import platform

def search_cci(criteria):
    # Load and parse the XML file
    tree = ET.parse('U_CCI_List.xml')
    root = tree.getroot()

    # Namespace handling
    ns = {'ns': 'http://iase.disa.mil/cci'}

    # Determine which regex pattern to use based on whether the criteria contains parentheses
    if '(' in criteria or ')' in criteria:
        # If criteria contain parentheses, use the pattern that handles them
        criteria_pattern = re.compile(rf'\b{re.escape(criteria)}(?=\s|$|[\(\)\w])')
    else:
        # Otherwise, use the simpler exact match pattern
        criteria_pattern = re.compile(rf'\b{re.escape(criteria)}\b')

    # Search for matching CCI items
    matches = []
    for cci_item in root.findall('ns:cci_items/ns:cci_item', ns):
        references = cci_item.find('ns:references', ns)
        if references is not None:
            for reference in references.findall('ns:reference', ns):
                if criteria_pattern.search(reference.get('index', '')):
                    matches.append({
                        'id': cci_item.get('id'),
                        'definition': cci_item.find('ns:definition', ns).text,
                        'references': [
                            {
                                'creator': ref.get('creator'),
                                'title': ref.get('title'),
                                'version': ref.get('version'),
                                'location': ref.get('location'),
                                'index': ref.get('index')
                            }
                            for ref in references.findall('ns:reference', ns)
                        ]
                    })
                    break

    return matches

def output_results(criteria, results):
    # Prepare the output folder
    output_folder = 'txt_output'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Output to a file
    output_file = os.path.join(output_folder, f'{criteria}_search_results.txt')
    with open(output_file, 'w') as f:
        for result in results:
            output_text = f"  CCI ID:\n{result['id']}\n  Definition:\n{result['definition']}\n  References:\n"
            for reference in result['references']:
                output_text += (
                    f"  - Title: {reference['title']}, Version: {reference['version']}, "
                    f"Index: {reference['index']}\n"
                )
            output_text += "\n"

            # Save to file
            f.write(output_text)

    # Open the file with the default text editor
    open_file(output_file)

def open_file(filepath):
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(("open", filepath))
    else:  # Linux and other Unix-like systems
        subprocess.call(("xdg-open", filepath))

if __name__ == "__main__":
    # Ask for the search criteria
    search_criteria = input("Enter the reference index to search for (e.g., 'AC-1' or 'AC-1 (2)'): ").strip()

    # Search for the CCI items
    matching_cci_items = search_cci(search_criteria)

    # Output the results and open the file
    if matching_cci_items:
        output_results(search_criteria, matching_cci_items)
    else:
        print(f"No CCI items found for the reference index '{search_criteria}'.")
