# CCI Search Tool
This is a Python script to search and return CCIs from a local XML file.

You can download the full list of CCI's from the [DoD Cyber Exchange](https://public.cyber.mil/stigs/cci/)

If you want to get started as soon as possible, just download the zip from the exchange above, extract it, and save the `cci_search.py` into the extracted folder.

Run the script from your terminal of choice and enter the control ID you're looking for (e.g., 'AC-1' or 'AC-1 (2)').
The search results will get saved as a file in the subfolder "txt_output" and open in your default text editor.


# Obsidian Modification

This is a version that's designed to be run from within Obsidian using the twibiral's [Execute Code plugin for Obsidian](https://github.com/twibiral/obsidian-execute-code). It outputs files in MarkDown and saves them to a folder in Obsidian, making it easy to reference and search.

Before you can use it, you'll need to  do a few things.

1. Install/enable the plugin mentioned above.
2. Copy the "U_CCI_List.xml" file you're using into your preferred folder in Obsidian.
3. Change the current working directory in the script to that folder with `os.chdir('//path//to//directory')` or `os.chdir("c:\\path\\to\\directory")` or whatever.
5. Change from "Editing" mode to "Reading" mode, scroll to the bottom of the code block, and click Run.
