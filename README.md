# Image Classification Labeling Tool
This project is an image labeling tool based on Tkinter. It allows users to label images and save the data into a CSV file.

<hr>

## Requirements
* pandas
* Pillow
* requests

Python comes with Tkinter included, so there's no need to install it separately.

<hr>

## How to Use
1. `image_url.csv`: A CSV file containing URLs of images to be labeled. This file must include at least one column named `URL`.
2. `label_classes.json`: A JSON file containing a list of available label classes. This file can start with an empty array [] and will be updated as users add labels through the application. It's okay not to have a json file at first.

Run the following command in the project directory to start the image labeling tool:
```
python image_classification_labeling_tool.py
```

<hr>

## Features
* Image Labeling: Directly download images from the web and display them in the GUI for labeling with predefined labels.
* Label Management: Add new labels or remove existing ones.
* Save and Navigate: Save labeled data to a CSV file and easily move to the next/previous image.
