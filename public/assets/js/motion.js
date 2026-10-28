/* Maurizio Dècina — home page motion, built on GSAP and ScrollTrigger.

   The page is readable without this file: site.js carries navigation and a
   CSS-only hero reveal. The `motion` class set in the head hides the elements
   animated below, so the first job here is to guarantee that class comes off
   again — on reduced motion, on a failed CDN, or once the timelines own the
   elements outright. A reader must never be left looking at a blank page. */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Hand the page back to CSS and leave. Used for every path where the
     animations will not run, so the hidden initial states are cleared. */
  function standDown() {
    root.classList.remove('motion');
    root.classList.add('motion-ready');
  }

  if (reduce || !window.gsap || !window.ScrollTrigger) {
    standDown();
    return;
  }

  var gsap = window.gsap;
  var ScrollTrigger = window.ScrollTrigger;
  gsap.registerPlugin(ScrollTrigger);

  /* The head script removes `motion` after a timeout if we never arrive.
     Claim the page before that fires; the elements are ours from here. */
  root.classList.add('motion-ready');

  gsap.defaults({ ease: 'power3.out', duration: .9 });

  var header = document.querySelector('.site-header');

  /* ----------------------------------------------------------------------
     Word splitting

     Wraps every word in a clipping box so the headline can rise into view a
     word at a time. Element wrappers inside the heading (the gold `.accent`
     span) are walked through rather than flattened, so their styling holds.
     ---------------------------------------------------------------------- */
  function splitWords(el) {
    var inners = [];

    function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          if (!child.nodeValue.trim()) return;
          var frag = document.createDocumentFragment();
          child.nodeValue.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (!part.trim()) {
              frag.appendChild(document.createTextNode(part));
              return;
            }
            var box = document.createElement('span');
            box.className = 'w';
            var inner = document.createElement('span');
            inner.className = 'w-i';
            inner.textContent = part;
            box.appendChild(inner);
            frag.appendChild(box);
            inners.push(inner);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          walk(child);
        }
      });
    }

    walk(el);
    return inners;
  }

  /* ----------------------------------------------------------------------
     Hero — one timeline, started once the web fonts have settled so the
     headline never animates at one metric and lands at another.
     ---------------------------------------------------------------------- */
  function hero() {
    var panel = document.querySelector('.hero-panel');
    if (!panel) return;

    var eyebrow = panel.querySelector('.eyebrow');
    var name = panel.querySelector('.hero-name');
    var rule = panel.querySelector('.hero-rule');
    var lede = panel.querySelector('.hero-lede');
    var actions = panel.querySelector('.hero-actions');

    var tl = gsap.timeline();

    if (eyebrow) {
      tl.to(eyebrow, { opacity: 1, duration: .7 }, 0)
        .from(eyebrow, { y: 14, duration: .7 }, 0);
    }

    if (name) {
      /* A word box is sized to its word and cannot break inside, so on narrow
         screens the longest word would outrun the column. There the heading
         stays one block and simply fades up; the per-word rise is a wider
         screen's flourish. */
      var canSplit = window.innerWidth >= 700;

      if (canSplit) {
        /* The heading reads as one string to assistive tech; the per-word
           boxes are a visual device only. */
        name.setAttribute('aria-label', name.textContent.replace(/\s+/g, ' ').trim());
        var words = splitWords(name);
        gsap.set(name, { opacity: 1 });
        if (words.length) {
          tl.from(words, {
            yPercent: 115,
            duration: 1,
            stagger: .055,
            ease: 'power4.out'
          }, .12);
        }
      } else {
        tl.to(name, { opacity: 1, duration: .9 }, .12)
          .from(name, { y: 20, duration: .9 }, .12);
      }
    }

    /* The gold rule draws itself out from the left. */
    if (rule) {
      tl.to(rule, { opacity: 1, duration: .01 }, .42)
        .fromTo(rule, { scaleX: 0 }, { scaleX: 1, duration: .75, ease: 'power3.out' }, .42);
    }

    [[lede, .52], [actions, .62]].forEach(function (pair) {
      if (!pair[0]) return;
      tl.to(pair[0], { opacity: 1, duration: .85 }, pair[1])
        .from(pair[0], { y: 20, duration: .85 }, pair[1]);
    });

    return tl;
  }

  /* ----------------------------------------------------------------------
     Section reveals — everything marked data-reveal, grouped so related
     cards arrive together rather than as one long cascade down the page.
     ---------------------------------------------------------------------- */
  function reveals() {
    var groups = {};

    gsap.utils.toArray('[data-reveal]').forEach(function (el) {
      var key = el.getAttribute('data-reveal') || 'solo';
      var section = el.closest('section, figure') || document.body;
      if (!section.dataset.revealKey) {
        section.dataset.revealKey = 'sec-' + (++reveals.n || (reveals.n = 1));
      }
      var id = key + ':' + section.dataset.revealKey;
      if (!groups[id]) groups[id] = [];
      groups[id].push(el);
    });

    Object.keys(groups).forEach(function (id) {
      var items = groups[id];
      gsap.fromTo(items,
        { opacity: 0, y: 30 },
        {
          opacity: 1,
          y: 0,
          duration: .85,
          stagger: .08,
          clearProps: 'transform',
          scrollTrigger: { trigger: items[0], start: 'top 88%', once: true }
        });
    });
  }

  /* ----------------------------------------------------------------------
     Milestones — the gold rail fills as the row scrolls past, and each
     marker lights up as the fill reaches it.
     ---------------------------------------------------------------------- */
  function milestones() {
    var items = gsap.utils.toArray('.milestones li');
    if (!items.length) return;

    var narrow = window.matchMedia('(max-width: 640px)').matches;
    var axis = narrow ? 'scaleY' : 'scaleX';

    items.forEach(function (li, i) {
      var fill = li.querySelector('.ms-fill');
      if (!fill) return;
      var vars = {
        duration: .55,
        ease: 'none',
        delay: narrow ? 0 : (i % 8) * .05,
        scrollTrigger: { trigger: li, start: narrow ? 'top 80%' : 'top 85%', once: true },
        onStart: function () { li.classList.add('is-lit'); }
      };
      vars[axis] = 1;
      gsap.to(fill, vars);
    });
  }

  /* ----------------------------------------------------------------------
     Photo band — a shallow parallax. The band crops the image, so there is
     room to move without exposing an edge.
     ---------------------------------------------------------------------- */
  function parallax() {
    [['.photo-band', 6], ['.quote-band-art', 5]].forEach(function (pair) {
      var band = document.querySelector(pair[0]);
      var img = band && band.querySelector('img');
      if (!img) return;
      var shift = pair[1];
      gsap.fromTo(img, { yPercent: -shift }, {
        yPercent: shift,
        ease: 'none',
        scrollTrigger: { trigger: band, start: 'top bottom', end: 'bottom top', scrub: true }
      });
    });
  }

  /* ----------------------------------------------------------------------
     Header — condenses once the hero is behind the reader.
     ---------------------------------------------------------------------- */
  function condenseHeader() {
    if (!header) return;
    ScrollTrigger.create({
      start: header.offsetHeight + 40,
      onToggle: function (self) {
        header.classList.toggle('is-condensed', self.isActive);
      }
    });
  }

  function start() {
    /* motion-ready is already set, so the head script's failsafe has stood
       down and nothing else will reveal the page if a step throws here. */
    try {
      hero();
      reveals();
      milestones();
      parallax();
      condenseHeader();
      ScrollTrigger.refresh();
    } catch (error) {
      gsap.globalTimeline.progress(1);
      root.classList.remove('motion');
      if (window.console) console.error('motion.js: ', error);
    }
  }

  /* Wait for fonts so measured positions are final, but never longer than a
     moment — a slow font host must not hold the hero hostage. */
  if (document.fonts && document.fonts.ready) {
    var started = false;
    var once = function () { if (!started) { started = true; start(); } };
    document.fonts.ready.then(once, once);
    setTimeout(once, 1200);
  } else {
    start();
  }

  /* Late-loading images change the page height; recalculate so triggers below
     them do not fire against stale positions. */
  window.addEventListener('load', function () { ScrollTrigger.refresh(); });
})();
