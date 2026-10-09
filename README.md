Joey Group Website Portal
=========================

Website for https://joeygonzalez.com, owned by https://github.com/jegonzal/gonzalezgroup.github.io.
Originally created by Lisa Dunlap and transferred to Joey in February 2025.
Simple website portal based on https://github.com/square/square.github.io.

Development
-----------

### Run the site locally
```bash
gem install bundler # first time only
bundle install # first time only
bundle exec jekyll serve
```

Use the Ruby version in `.ruby-version` and the Bundler version in `Gemfile.lock`.

Adding a Person
-----------

1. Open `_data/people.yml`. You will see a clearly organized list of titles and people.
2. Insert or update your entry in the YAML list.
3. Place your headshot in `profile_images/` with a clean filename (ideally
   `firstname.<ext>` or `firstlast.<ext>`) and a small file size.

Current students use portrait cards (or an initial when no photo is available).
Alumni are listed compactly; set `alumni: true` on alumni divisions and use
`years` for advising dates. Names link to personal websites or professional profiles.

Adding a Project
-----------

Edit `_data/projects.yml`; the carousel renders this list automatically.
Each project needs `name`, `url`, and an `image` filename in `logo_pictures/`.
Use `wordmark: true` instead of an image for official text-only branding.

Research page
-----------

`/research/` and the homepage "Research Through the Years" strip render from
`_data/research.yml`. Project cards use `_includes/project-card.html`. In HTML
inside `research.yml`, prefix internal links with `%BASE%`
(e.g. `%BASE%/#person-lianmin-zheng`).

Publications
-----------

The homepage's selected publications come from `_data/featured_publications.yml`
(`title`, `authors`, `venue`, `year`, `url`).

`python generate_paper_html.py --since-year YEAR` refreshes the Google Scholar
export (`_data/publications.yml` and `publications.json`). By default it includes
the last five years.

Bio and activities
-----------

- Edit the About, Recent Preprints, and Recent Activities sections of `index.html`.
- `/bio/` holds short, medium, and long biographies.
- Update the date in `_includes/footer.html` when changing content.
