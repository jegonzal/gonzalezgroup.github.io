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

### To update the papers page
The homepage's selected 2026 publications come from `_data/featured_publications.yml`.
This curated list is separate from the Google Scholar export so fetching Scholar
does not overwrite the CV-based selection or its conference information.
Each entry has `title`, `authors`, `venue`, `year`, and `url` fields; JSON syntax
is valid YAML. The full author lists are available in expandable disclosures.

The Google Scholar export can still be refreshed:

1. Run the python script `generate_paper_html.py` in the root folder to fetch publications from Google Scholar and write:
   - `_data/publications.yml` (archival Scholar feed)
   - `publications.json` (same data in JSON form)
   - `publications_preview.html` (a standalone preview page)
2. Commit the updated files.

Adding a Person
-----------
Here are the steps to add or modify a person:

1. Open `_data/people.yml`. You will see a clearly organized list of titles and people.
2. Insert/update yourself to the YAML list.
3. Ensure your headshot is placed in `profile_images/`, that the filename is clean (ideally `firstname.<ext>` or `firstlast.<ext>`), and that you have minimzed the file size.

The People section precedes Research and Activities. Current students use portrait
cards (or an initial when no photo is available). Alumni use compact lists split
into former doctoral students and former postdocs. Set `alumni: true` on alumni
divisions and use `years` for advising dates; these are not necessarily degree dates.
Names link directly to personal websites or verified professional profiles.
See `_maintenance/people-sources.md` for the September 2026 roster review and
the few profile/status uncertainties to confirm on future updates.

Adding a Project
-----------

Edit `_data/projects.yml`; the carousel renders this list automatically.
Each project needs `name`, `url`, and an `image` filename in `logo_pictures/`.
Use `wordmark: true` instead of an image for official text-only branding.
For new screened additions, record `repository`, `stars`, and `checked` (date).
These star counts are maintenance metadata, not displayed as live counts.
See `_maintenance/project-screening.md` for logo sources, paper associations,
and candidates excluded from the September 2026 refresh.

Updating Publications
-----------

Run `python generate_paper_html.py --since-year YEAR` to update the publications data files.

Notes:
- By default, the script only includes publications with year >= (current year - 5). Override with `--since-year`.

Updating the bio and activities
-----------

- Edit the About, Recent Preprints, and Recent Activities sections of `index.html`.
- The September 2026 refresh uses `../Berkeley/cv/bio.tex`,
  `joseph_gonzalez_cv.tex`, and `publications.bib` (paths relative to the parent
  `websites` directory). Conference labels follow that bibliography;
  preprints are listed separately.
- Replace `assets/joseph_gonzalez_cv.pdf` with the latest public CV when updating it.
- Update the content date in the footer when changing content.
- The existing student roster remains in `_data/people.yml`; confirm membership
  directly before changing it based on historical CV advising records.

Use Ruby 3.2 (see `.ruby-version`) and the Bundler version in `Gemfile.lock`.
Before publishing, run `bundle exec jekyll build` and review the local site with
`bundle exec jekyll serve`. GitHub Pages publishes the root of `master`;
pushing or merging changes there updates the live site. Keep `CNAME` set to
`joeygonzalez.com`.

Deploy to the Berkeley server
-----------

The new `deploy.sh` uses the old website's SSH destination:
`watson.millennium.berkeley.edu:~/public_html/`, served at
`https://people.eecs.berkeley.edu/~jegonzal/`. It uses your SSH configuration
and credentials, just like the old script; Berkeley network/VPN access may be required.

```bash
./deploy.sh --build-only  # Build locally; no server connection
./deploy.sh --dry-run     # Build and preview transfers over SSH; no remote writes
./deploy.sh               # Build and upload the new site
```

The script can be invoked from any directory. It uses this Mac's existing
Homebrew Ruby 3.2/local Bundler setup when available, otherwise `bundle` from
your Ruby environment (run `bundle install` first).

Builds go to `_site_berkeley/`, with `/~jegonzal` as the path prefix, leaving
the regular `_site/` preview untouched. The canonical search URL remains
`https://joeygonzalez.com/` so the Berkeley copy does not compete with it.
The GitHub Pages `CNAME` file and deployment script are not uploaded.

Uploads overwrite matching files but **do not delete** old files on the server,
preserving historical papers, course pages, and other content. Replaced files
are automatically backed up outside the public website in a unique directory
under `/home/eecs/jegonzal/website-backups/`; the script prints that location
after upload. File permissions and timestamps are preserved without attempting
to change server ownership or groups. Dry runs do not create backups or write
remote files. This command does not commit or push to GitHub; GitHub Pages
deployment remains separate.

Search indexing and sharing
-----------

- `_config.yml` controls the production URL, search title, description, and optional Google Search Console verification token. Restart the preview server after editing this file.
- The homepage includes a canonical URL, social-sharing metadata, and factual Person/Organization/WebSite structured data in `_includes/structured-data.html`.
- `robots.txt` allows crawling and points to `sitemap.xml`, which lists the homepage and public CV. Add future public pages to the sitemap; do not add section anchors or preview pages. No artificial last-modified date is generated on builds.
- Internal publication previews and generator inputs are excluded from the published site.
- After publishing, verify the domain in Google Search Console (DNS verification, or the optional HTML token above), submit `https://joeygonzalez.com/sitemap.xml`, and inspect/request indexing for the homepage. Check HTTPS enforcement in GitHub Pages and redirects from HTTP, www, and the github.io hostname.
- Validate the deployed markup in Schema.org Validator and Google Rich Results Test. Structured data describes the page; it does not guarantee rich results or indexing. Monitor indexing and Core Web Vitals in Search Console.
