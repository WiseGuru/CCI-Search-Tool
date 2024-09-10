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
                # Check if the reference index matches the search criteria
                if criteria_pattern.search(reference.get('index', '')):
                    # Further filter to include only references that mention NIST SP 800-53 Revision 5
                    if "NIST SP 800-53 Revision 5" in reference.get('title', ''):
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

    # Hardcoded title order
    # These titles were the only unique titles extracted from the CCI XML
    title_order = [
        "NIST SP 800-53 Revision 5",
        "NIST SP 800-53 Revision 4",
        "NIST SP 800-53",
        "NIST SP 800-53A",
    ]

    # Sort function: prioritize title order and version
    def sort_references(references):
        # Sort by hardcoded title order and then by version descending
        references.sort(key=lambda ref: (
            title_order.index(ref['title']) if ref['title'] in title_order else len(title_order),  # Use title_order or move to the bottom
            -int(ref['version'])  # Sort by version in descending order
        ))

    # Output to a file
    output_file = os.path.join(output_folder, f'{criteria}_search_results.txt')
    with open(output_file, 'w') as f:
        for result in results:
            output_text = f"  CCI ID:\n{result['id']}\n  Definition:\n{result['definition']}\n  References:\n"
            references = result['references']
            
            # Sort references using the custom sort function
            sort_references(references)
            
            # Output sorted references
            for reference in references:
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

def main():
    while True:
        # Ask for the search criteria and normalize it to uppercase
        search_criteria = input("Enter the reference index to search for (e.g., 'AC-1' or 'AC-1 (2)'): ").strip().upper()

        # Search for the CCI items
        matching_cci_items = search_cci(search_criteria)

        # Output the results and open the file
        if matching_cci_items:
            output_results(search_criteria, matching_cci_items)
            print(f"SUCCESS: CCI items found for the reference index '{search_criteria}' with 'NIST SP 800-53 Revision 5' and exported to file.")
            retry = input("Would you like to conduct another search? (y/N): ").strip().lower()
            if retry.lower() != 'y':
                break  # Exit loop if the user doesn't want to search again
        else:
            print(f"NO RESULTS: No CCI items found for the reference index '{search_criteria}' with 'NIST SP 800-53 Revision 5'.")
            retry = input("Would you like to try another search? (y/N): ").strip().lower()
            if retry.lower() != 'y':
                break  # Exit loop if the user doesn't want to search again

if __name__ == "__main__":
    main()
