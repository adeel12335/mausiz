# Professional minimal revamp

Active base: claude-design. User requested a more professional, minimal design with a city background in the hero. Milan Piazza del Duomo connects the design to Politecnico di Milano.

## Implementation spec

- Native desktop reference: 01-desktop-concept.png, 1536x1024. Header approximately76px; hero approximately572px; centered content begins near165px, using existing1360px outer wrap and responsive gutters.
- Preserve all Claude branch text, complete Italian teaching archive, English/Italian curricula, publication metadata, links, images, navigation and routes. Only hero title and role change visual order: name first, role below.
- Hero: full-bleed evening Milan city image, deliberate navy readability scrim on left, separate transparent original-person portrait at right. No portrait tint, card, network lines or diagonal rule. Natural face and both hands remain visible. Copy and controls stay native HTML.
- Colours: true white #ffffff; ink #12253a; deepnavy #0d2036; muted #637184; rules #e3e7ec; bronze #b18a43; readable bronze links #8a6429.
- Typography: existing Literata for titles and citation, existing IBM Plex Sans for body, controls and metadata. Desktop hero72px, section44px, body18px/1.7, nav/buttons15px. Mobile titleapproximately44px, body17px. Preserve original typography fallback stacks.
- Components: thin-outline header CTA, bronze primary hero CTA, white-outline secondary hero CTA; open affiliation rows; editorial biography; horizontal dated career rows; open research lists; original publication table; teaching archive rail; existingcontactcolumns and navyfooter.
- Editorial reference:02-editorial-concept.png. Remove oversized dropcap; retain all biography paragraphs, original square city portrait and CV links. Dates and career content remain unchanged.
- Publication reference:03-publications-concept.png. Use its visual hierarchy, rules and spacing. Its generated example dates/venues are not source content and must be replaced by the exact existing real metadata. Retain all actual introductory text and all original teaching/contact sections. Section merging/omissions shown by the concept are not adopted.
- Mobile reference:04-mobile-concept.png. Exact readable original copy,44px minimum controls, city image behindcopy andportrait. Put portrait belowcopy on narrow screens to prevent overlapping controls/emails; this accessibility adaptation is intentional.
- Shared theme extends to all existing pages through minimal.css. Preserve responsive archive scroll-spy, category anchors, mobile navigation, focus states and reduced-motion behaviour.
- No new marketing copy, statistics, labels, fake claims, sections or UI widgets.

## Allowed hero copy

Maurizio Dècina; Professor Emeritus of Telecommunications, Politecnico di Milano; For contributions to digital communications and to voice/data packet switching.; IEEE Fellow citation, 1986; Read the biography; Selected publications; Biografia in italiano; maurizio@mauriziodecina.it; m.decina@ieee.org.

## Asset inventory

milan-duomo-evening-v2.png: standalone city background generated from desktop concept.
maurizio-cutout-v2.png: transparent background edit of existing portrait.jpg.
Existing biography portrait, classroom images, downloaded documents and source snapshots remain unchanged.


## Production image encoding

Optimized WebP sources total667,240 bytes versus4,536,654 bytes for the retainedPNG originals (approximately85% reduction). PNG fallbacks remain available. Both assets retain their composition and the portrait retains alpha transparency. No source document or archival binary was changed.

## User-requested refinement: Teaching feature and distinct hero backdrop

The active hero reference is now06-hero-v3-concept.png; the Duomo hero concept is superseded. The new modern Milan skyline is a standalone generated backdrop, using the existing native hero copy, portrait and header. Use a32% vertical background crop to keep the skyline spire in frame and the deliberate left readability scrim. Use optimizedWebP withPNG fallback.

Teaching reference:05-teaching-v3-concept.png at1536x1024. Replace the600px full-bleed classroom photo with an editorial feature inside the Teaching section: widened1480px outerwrap,66px responsivegutters (imageleftx94 at1536px), three-to-two columnratio,42pxgap, original classroom imageleft, introandarchiveCTA right. Photo420px high on desktop, naturalcolours,nooverlay. Captionoutsidephoto. Heading60px, intro20px/1.6,46pxminimumCTAwithsubtlearrow. Fine horizontalrule leads to original course/year lists beneath the feature. Keep every existingcourse/year/download/gallery/contactword and link. Move the original archive link to the feature without duplicating it.

The concept's added labelCourses is omitted to honour the user's original content lock. Keep the existing globalheader alignment. On narrow screens, moveTeaching introabovephoto, thenstacktheoriginal lists. All photos areoriginal historicalsources; onlydisplayframingchanges. Navigation to#teaching lands onthisnewfeature.

Final skyline framing: desktop image overscans180px horizontally and uses a27% vertical crop, keeping the tower beside the portrait rather than touching the head. Mobile keeps its own natural crop. Teaching description uses navy text, wide-screenCTA17px and archive heading34px.
