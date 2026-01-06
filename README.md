Joey Group Website Portal
=========================

Simple website portal based on https://github.com/square/square.github.io

Development
-----------

### Run the site locally
```bash
gem install bundler # first time only
bundle install # first time only
bundle exec jekyll serve
```

### To update the papers page
This repo’s homepage shows a small “Recent Publications” section sourced from `_data/publications.yml`.

1. Run the python script `generate_paper_html.py` in the root folder to fetch publications from Google Scholar and write:
   - `_data/publications.yml` (used by `index.html`)
   - `publications.json` (same data in JSON form)
   - `publications_preview.html` (a standalone preview page)
2. Commit the updated files.

Adding a Person
-----------
Here are the steps to add or modify a person:

1. Open `_data/people.yml`. You will see a clearly organized list of titles and people.
2. Insert/update yourself to the YAML list.
3. Ensure your headshot is placed in `profile_images/`, that the filename is clean (ideally `firstname.<ext>` or `firstlast.<ext>`), and that you have minimzed the file size.

Adding a Project
-----------

Here are the steps to add projects, datasets or other content:

1. Open the index.html file. There are two clearly marked sections for adding list items for datasets and projects
2. Fill out the template:
```html
<div class="menu-item-info">
  <h4 class="menu-item-name"> PROJECT NAME </h4>
  <span class="menu-item-price"><a href="https://github.com/cannylab/project_github_link"
      target="_blank">GitHub</a></span>
  <p class="menu-item-description" style="height:auto"> PROJECT NAME </p>
  <img src="/repo_images/project_image.png" style="width: 100%;">
</div>
```

3. Add any required images to the `repo_images` folder.

Updating Publications
-----------

Run `python generate_paper_html.py --since-year YEAR` to update the publications data files.

Notes:
- By default, the script only includes publications with year >= (current year - 5). Override with `--since-year`.
