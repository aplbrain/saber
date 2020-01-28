# webanno

A human-facing web annotation tool for different flavors of data.



## Overview

The `webanno` tool runs a Python process that exposes a web server with a single user-facing web-page which holds developer-defined data to annotate (perhaps it's text, perhaps it's a webform, perhaps it's imagery...). Once the data are annotated and submitted, the web server shuts down gracefully (exitcode 0), which means you can use the output data in a SABER workflow.

### Why not a conventional web app?

A conventional web application process does not stop once the data are annotated, which means you cannot run it "in-line" with the rest of a SABER workflow.

## How do I pick the data to annotate?

`webanno` uses a plugin architecture system: A plugin defines both the HTML of the page as well as what to do with the data when annotation is over.

There are many already-existing annotation plugins:

### `ButtonPressPlugin`

This plugin is the simplest (and a good example to learn from!), and just monitors when a button is pressed.

### `FormInputPlugin`

This plugin lets you create a custom form in HTML for a user to fill out.

### `CentroidsPlugin`

This plugin lets a user place points in a 2D image, and returns a JSON file of the coordinates of those clicks.

### `BossVolumePlugin`

This plugin lets a user place points in a 3D volume downloaded from BossDB.


## Installation

To get started, you need only pip-install this package and its dependencies:

```shell
pip3 install -r requirements.txt
pip3 install -e .
```

## Usage

Use the `webanno` tool from the command-line:

```shell
webanno examples/example_centroids_image.json
```

Results will be stored in `results.json` in PWD. If you would like to store them elsewhere, set `json_file_output` in any config file (all plugins accept this config value).
