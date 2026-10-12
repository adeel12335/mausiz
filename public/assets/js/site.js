/* Maurizio Dècina — site behaviour: navigation, header state, scroll-spy. */
(function () {
  'use strict';

  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.site-nav');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------- Mobile navigation ---------- */
  if (toggle && nav) {
    var open = function () {
      nav.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
      document.documentElement.classList.add('nav-open');
    };
    var close = function () {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      document.documentElement.classList.remove('nav-open');
    };
    toggle.addEventListener('click', function () {
      nav.classList.contains('is-open') ? close() : open();
    });
    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) close();
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        close();
        toggle.focus();
      }
    });
    document.addEventListener('click', function (event) {
      if (!event.target.closest('.site-header')) close();
    });
    var wide = window.matchMedia('(min-width: 1024px)');
    var onWide = function () { if (wide.matches) close(); };
    if (wide.addEventListener) wide.addEventListener('change', onWide); else wide.addListener(onWide);

    /* Mark the current page in the navigation. */
    var here = location.pathname.replace(/\/index\.html$/, '/');
    nav.querySelectorAll('a[href]').forEach(function (link) {
      var url = new URL(link.getAttribute('href'), location.href);
      var path = url.pathname.replace(/\/index\.html$/, '/');
      if (path === here && !url.hash) link.setAttribute('aria-current', 'page');
    });
  }

  /* ---------- Header shadow once the page has scrolled ---------- */
  if (header) {
    var setScrolled = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    setScrolled();
    window.addEventListener('scroll', setScrolled, { passive: true });
  }

  /* ---------- Scroll-spy for sticky rails (archive years, publication categories) ---------- */
  document.querySelectorAll('[data-spy]').forEach(function (rail) {
    var links = Array.prototype.slice.call(rail.querySelectorAll('a[href^="#"]'));
    var targets = links.map(function (link) {
      return document.getElementById(decodeURIComponent(link.hash.slice(1)));
    }).filter(Boolean);
    if (!targets.length) return;

    var setActive = function (id) {
      links.forEach(function (link) {
        var active = decodeURIComponent(link.hash.slice(1)) === id;
        link.classList.toggle('is-active', active);
        if (active) {
          link.setAttribute('aria-current', 'location');
          /* Keep the active item visible inside a scrolling rail. */
          if (rail.scrollHeight > rail.clientHeight || rail.scrollWidth > rail.clientWidth) {
            link.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: reduceMotion.matches ? 'auto' : 'smooth' });
          }
        } else {
          link.removeAttribute('aria-current');
        }
      });
    };

    /* On narrow screens the rail sits under the header, so it counts towards the offset. */
    var railBox = rail.closest('.archive-aside, .article-aside') || rail;
    var offset = function () {
      var railHeight = window.innerWidth < 1024 ? railBox.offsetHeight : 0;
      return (header ? header.offsetHeight : 0) + railHeight + 28;
    };
    var ticking = false;
    var update = function () {
      ticking = false;
      var limit = offset();
      var current = targets[0];
      for (var i = 0; i < targets.length; i++) {
        if (targets[i].getBoundingClientRect().top - limit <= 1) current = targets[i];
        else break;
      }
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
        current = targets[targets.length - 1];
      }
      setActive(current.id);
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update);
    update();

    /* Rail links jump instantly: these pages are tens of thousands of pixels long,
       and a smooth scroll across the whole archive is slow rather than helpful. */
    links.forEach(function (link) {
      link.addEventListener('click', function (event) {
        var target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
        if (!target) return;
        event.preventDefault();
        var root = document.documentElement;
        var previous = root.style.scrollBehavior;
        root.style.scrollBehavior = 'auto';
        target.scrollIntoView({ behavior: 'auto', block: 'start' });
        root.style.scrollBehavior = previous;
        history.pushState(null, '', link.hash);
        setActive(target.id);
      });
    });
  });

  /* ---------- Keep a deep link anchored once web fonts have swapped in ---------- */
  if (location.hash && document.fonts && document.fonts.ready) {
    var startY = window.scrollY;
    document.fonts.ready.then(function () {
      var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (target && Math.abs(window.scrollY - startY) < 4) {
        target.scrollIntoView({ behavior: 'auto', block: 'start' });
      }
    });
  }

  /* ---------- Hero reveal: add the class once fonts are ready so text never flashes mid-animation ---------- */
  var hero = document.querySelector('.hero');
  if (hero && !reduceMotion.matches) {
    var reveal = function () { hero.classList.add('is-ready'); };
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(reveal, reveal);
      setTimeout(reveal, 900);
    } else {
      reveal();
    }
  } else if (hero) {
    hero.classList.add('is-ready');
  }
})();
