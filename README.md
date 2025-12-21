# RedM-Inventory-Image-Renaming-Tool-
Rename Image files using an SQL database file (REDM)

This tool is intended to make life easier when renaming inventory images on mass or for finding missing images within a database.

It compares an exported SQL Database file with 1 or more image folders and returns exact matches or suggestions based on image file names.

Exact matches show in green, Filter reason given, displays description from SQL, dropdown search bar, and shows suggestions.

Simply search for the image to match the item entry and tick the box for renaming.

Features:

    * Recursive image scanning

	* Item name & description display
	
	* Analysis filters

	* Match detection & suggestions

	* Matches are Highlighted
	
	* Dropdown Search bar
    
	* Image preview on hover

	* Batch rename after confirmation
    
How to use ths tool:

	* Using a clean folder export the SQL you wish to use from your RedM server.
    
	* Make a copy of the images that are currently matching (that you wish to keep from vorp inventory)
    
	* Make a copy of the image pack you intend to use.
    
	* Put Both folders in the same root folder.

Run the Tool:
    
	* Select the Exported SQL File
    
	* Select the root folder containg both Image folders
    
	* Select Filters
    
	* Analyze

Select Images & Rename:
    
	* Using the suggestions and/or drop down menu select the images you wish to use
    
	* Toggle Select the rows you wish to rename (✔)
    
	* Rename the selected rows when finished

Updates:

	* Update 1.01 - 20/12/25

		- Counter in lower left corner

	* Update 1.02 21/12/25

		- Button Fix
		
		- Rename/Backup Folder fix

		- Added Backup option (good for removing images from image pack)
		
To-Do & Knowen Bugs: 
	
	* Unstable when Analyzing (can crash when interacting with the app while analyzing)

	* Add more settings to filters tab	
