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

    # Relevant titles to include in the output
    included_titles = [
        "NIST SP 800-53 Revision 5",
        "NIST SP 800-53A",
    ]

    # Prepare a list to hold sorted results
    sorted_results = []

    for result in results:
        # Filter references to only include those with titles in included_titles
        references = [ref for ref in result['references'] if ref['title'] in included_titles]

        # Skip if no references match the included titles
        if not references:
            continue

        # Find the "NIST SP 800-53 Revision 5" reference and its index
        revision_5_reference = next(
            (ref for ref in references if ref['title'] == "NIST SP 800-53 Revision 5"), None
        )
        revision_5_index = revision_5_reference['index'] if revision_5_reference else ""

        # Add leading zero to single-digit numbers in parentheses (e.g., (1) becomes (01))
        normalized_index = re.sub(r'\((\d)\)', r'(0\1)', revision_5_index)

        # Append the result with its relevant sorting key (the normalized index/title) to the list
        sorted_results.append({
            'id': result['id'],
            'index': normalized_index,
            'definition': result['definition']
        })

    # Sort the results by:
    # 1. Whether the index contains parentheses (parentheses last)
    # 2. The normalized index (alphabetically with zero-padded numbers)
    sorted_results.sort(key=lambda x: (
        1 if '(' in x['index'] else 0,  # Prioritize titles without parentheses
        x['index']  # Sort alphabetically within each group
    ))

    # Output to a file
    output_file = os.path.join(output_folder, f'{criteria}_search_results.txt')
    with open(output_file, 'w') as f:
        for result in sorted_results:
            # Prepare the output line with CCI ID, Compliant/Non-Compliant, Index, and Definition
            cci_output = f"- {result['id']}: Compliant/Non-Compliant\n"
            cci_output += f"{result['index']}: {result['definition']}\n\n"
            f.write(cci_output)

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
