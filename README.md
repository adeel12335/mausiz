# Maurizio Dècina website

Static, responsive website for Prof. Maurizio Dècina (Politecnico di Milano). An English home page presents the career, research, recognition, publications and teaching; the complete original documents (both CVs, the publication list and the full Italian teaching archive) are preserved word for word underneath it.

## Preview

```
npm start
```

Opens a local preview at http://127.0.0.1:4173/. Node.js is the only preview dependency; there is no install or build step for running the site.

## Publish

Upload the complete `public/` folder as the hosting document root and keep all filenames and subfolders. The original `stuff/` URLs still work, so old links to documents and to the two biographies keep resolving.

| Page | File | Language |
| --- | --- | --- |
| Home | `public/index.html` | English |
| Teaching archive (original homepage content, all 10 academic years, 493 anchors) | `public/teaching.html` | Italian |
| Curriculum vitae (page header, contents rail, complete original text) | `public/stuff/decinabiography.htm` | English |
| Curriculum vitae (page header, contents rail, complete original text) | `public/stuff/decinabiografia.htm` | Italian |
| List of selected publications (with category navigation) | `public/stuff/decinapublications.htm` | English |

Also generated: `sitemap.xml`, `robots.txt`, Open Graph tags and a JSON-LD Person record on the home page.

## Content rules

- Every fact on the home page comes from the captured source pages (the CV dated 4/2012, the publication list and the teaching archive) or from three official pages found on the web and cited in `design/web-photos/SOURCES.md`: Politecnico di Milano (Professor Emeritus, 2014), Key4biz (AGCOM Commissioner from July 2012) and Invitalia (President of Infratel Italia from October 2016). No copy from the layout PDF was used. End dates of the AGCOM and Infratel mandates and the 2024 honour shown in the PDF could not be verified and are not on the site.
- Photographs: the hero portrait and the lecture-hall photographs come from the original site and from the two course photo albums in the archive (`Foto_corso_2005-06.zip`, `Foto_corso_2006-2007.zip`). The 2022 portrait on the Biography section and the CV pages was found on the 5G Italy speaker page; its rights must be confirmed with Prof. Dècina before publishing (see `design/web-photos/SOURCES.md`). Swap `public/assets/portrait-2022*.jpg/.webp` to replace it.
- The four original documents are rendered from `design/source-content/` and checked on every build: `content-audit.json` must show `text_match: true` and `link_order_match: true` for all four.
- Three original ZIP links returned 404 at the source during extraction and keep their original remote address. See `asset-manifest.json`.

## Design

`design/design-plan.md` records the design brief, tokens and the review against generic defaults. In short: Literata for display and body text, IBM Plex Sans for navigation and metadata, navy and gold on white, hairline-structured lists instead of cards, one gold career timeline as the signature element.

## Regenerating pages

```
python tools/build-website.py
```

Requires Python 3 with `lxml`. The script wraps `tools/home-main.html` (the home page content) in the shared header and footer, rebuilds the four source documents, writes the sitemap and runs the content audit. Edit `tools/home-main.html` for home page content and `public/assets/css/site.css` for styling; never edit the generated HTML by hand.

Image assets in `public/assets/`: `portrait*.jpg/.webp` (hero, from the original site photo), `portrait-2022*` (biography and CV pages, see sources), `lecture-hall-*` (teaching band, original site), `course-2005-*` and `course-2006-*` (rendered from the archive's photo albums), `og-image.jpg` (link preview).

## Other files

- `asset-manifest.json`: inventory of the 483 extracted source files with URLs, sizes and status.
- `tools/extract-assets.py`: repeatable source-asset extraction.
- `design/implementation-review.md`, `design/browser-checks.json`: review notes and browser checks from the first content-preserving version.
