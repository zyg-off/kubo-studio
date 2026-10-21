(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // header shadow + back-to-top
  var bar = $(".site-header"), toTop = $(".to-top");
  function onScroll() {
    var y = window.scrollY;
    if (bar) bar.classList.toggle("scrolled", y > 8);
    if (toTop) toTop.classList.toggle("show", y > 700);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });

  // mobile menu
  var menuBtn = $(".menu-btn"), links = $(".nav-links");
  if (menuBtn && links) {
    menuBtn.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    links.addEventListener("click", function (e) {
      if (e.target.closest("a")) { links.classList.remove("open"); menuBtn.setAttribute("aria-expanded", "false"); }
    });
  }

  // scroll reveal
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.12 });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal").forEach(function (el) { el.classList.add("in"); });
  }

  // rotating words
  var words = $$(".rotator span"), w = 0;
  if (words.length && !reduce) setInterval(function () {
    words[w].classList.remove("on");
    w = (w + 1) % words.length;
    words[w].classList.add("on");
  }, 2600);

  // draggable 3D cube
  var cube = $("#cube");
  if (cube) {
    var stage = cube.parentElement, rx = -26, ry = -42, dragging = false, lastX = 0, lastY = 0;
    var apply = function () { cube.style.transform = "rotateX(" + rx + "deg) rotateY(" + ry + "deg)"; };
    stage.style.touchAction = "pan-y";
    stage.addEventListener("pointerdown", function (e) {
      dragging = true; lastX = e.clientX; lastY = e.clientY;
      cube.classList.remove("idle"); cube.style.cursor = "grabbing";
      stage.setPointerCapture(e.pointerId);
    });
    stage.addEventListener("pointermove", function (e) {
      if (dragging) {
        ry += (e.clientX - lastX) * 0.5; rx -= (e.clientY - lastY) * 0.5;
        rx = Math.max(-80, Math.min(80, rx));
        lastX = e.clientX; lastY = e.clientY; apply();
      } else if (!cube.classList.contains("idle") && e.pointerType === "mouse") {
        var r = stage.getBoundingClientRect();
        ry = -42 + ((e.clientX - r.left) / r.width - 0.5) * 50;
        rx = -26 - ((e.clientY - r.top) / r.height - 0.5) * 30;
        apply();
      }
    });
    var stop = function () { dragging = false; cube.style.cursor = "grab"; };
    stage.addEventListener("pointerup", stop);
    stage.addEventListener("pointercancel", stop);
    if (reduce) cube.classList.remove("idle");
  }

  // guided tour: list of tabs that swap one screenshot, auto-advancing
  $$("[data-tour]").forEach(function (tour) {
    var items = $$(".tour-item", tour), img = $(".tour-view img", tour), url = $(".tour-view .url", tour);
    var idx = 0, timer = null, DUR = 6000, auto = !reduce;
    function show(i, user) {
      idx = i;
      items.forEach(function (it, j) {
        var on = j === i;
        it.setAttribute("aria-selected", on ? "true" : "false");
        it.tabIndex = on ? 0 : -1;
        var b = $(".bar b", it);
        if (b) { b.classList.remove("run"); if (on && auto) { void b.offsetWidth; b.style.setProperty("--dur", DUR + "ms"); b.classList.add("run"); } }
      });
      var src = items[i].getAttribute("data-src"), alt = items[i].getAttribute("data-alt") || "";
      if (img && img.getAttribute("src") !== src) {
        img.classList.add("fade");
        setTimeout(function () { img.src = src; img.alt = alt; img.onload = function () { img.classList.remove("fade"); }; }, 180);
      }
      if (url && items[i].getAttribute("data-url")) url.textContent = items[i].getAttribute("data-url");
      if (user) auto = false;
      clearTimeout(timer);
      if (auto) timer = setTimeout(function () { show((idx + 1) % items.length); }, DUR);
    }
    items.forEach(function (it, i) {
      it.addEventListener("click", function () { show(i, true); });
      it.addEventListener("keydown", function (e) {
        if (e.key === "ArrowDown" || e.key === "ArrowUp") {
          e.preventDefault();
          var n = (i + (e.key === "ArrowDown" ? 1 : items.length - 1)) % items.length;
          show(n, true); items[n].focus();
        }
      });
      var pre = new Image(); pre.src = it.getAttribute("data-src");
    });
    // start when visible
    if ("IntersectionObserver" in window) {
      var started = false;
      new IntersectionObserver(function (en, obs) {
        if (en[0].isIntersecting && !started) { started = true; show(0); obs.disconnect(); }
      }, { threshold: 0.3 }).observe(tour);
    } else show(0);
  });

  // lightbox
  var lb = null;
  function openLightbox(src, alt) {
    if (!lb) {
      lb = document.createElement("div");
      lb.className = "lightbox";
      lb.setAttribute("role", "dialog");
      lb.setAttribute("aria-modal", "true");
      lb.setAttribute("aria-label", "Capture d'écran agrandie");
      lb.innerHTML = '<button type="button" aria-label="Fermer"><svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M5 5l10 10M15 5L5 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button><img alt=""><p></p>';
      document.body.appendChild(lb);
      lb.addEventListener("click", function (e) { if (e.target === lb || e.target.closest("button")) closeLightbox(); });
      document.addEventListener("keydown", function (e) { if (e.key === "Escape" && lb.classList.contains("open")) closeLightbox(); });
    }
    $("img", lb).src = src; $("img", lb).alt = alt; $("p", lb).textContent = alt;
    lb.classList.add("open");
    $("button", lb).focus();
  }
  function closeLightbox() { lb.classList.remove("open"); if (lastTrigger) lastTrigger.focus(); }
  var lastTrigger = null;
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-zoom]");
    if (!t) return;
    lastTrigger = t;
    var img = t.tagName === "IMG" ? t : $("img", t);
    openLightbox(t.getAttribute("data-zoom") || img.src, img ? img.alt : "");
  });

  // FAQ: one open at a time per group
  $$(".faq").forEach(function (faq) {
    var ds = $$("details", faq);
    ds.forEach(function (d) {
      d.addEventListener("toggle", function () { if (d.open) ds.forEach(function (o) { if (o !== d) o.open = false; }); });
    });
  });

  // copy e-mail
  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var txt = b.getAttribute("data-copy"), old = b.textContent;
      var done = function () { b.textContent = "Copié !"; setTimeout(function () { b.textContent = old; }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, function () {});
    });
  });


  // Pages traduites : français par défaut, boutons [data-lang] ou ?lang=en / ?lang=pt
  if (window.I18N) {
    var T = window.I18N, FR = {};
    $$("[data-t]").forEach(function (e) {
      FR[e.getAttribute("data-t")] = e.classList.contains("btn") ? e.lastChild.textContent : e.innerHTML;
    });
    FR.ref = T.fr_ref || "Référence de la commande : ";
    T.fr = FR;
    var params = new URLSearchParams(location.search), current = "fr";
    var checkoutId = params.get("checkout_id"), baseTitle = document.title;
    var setLang = function (lang) {
      current = T[lang] ? lang : "fr";
      var t = T[current];
      document.documentElement.lang = current;
      $$("[data-t]").forEach(function (e) {
        var v = t[e.getAttribute("data-t")];
        if (!v) return;
        if (e.classList.contains("btn")) e.lastChild.textContent = v; else e.innerHTML = v;
      });
      document.title = current === "fr" ? baseTitle : (t.doc_title || baseTitle);
      $$("[data-lang]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-lang") === current ? "true" : "false"); });
      var ref = $("#ref");
      if (ref && checkoutId && checkoutId.indexOf("{") === -1) ref.textContent = t.ref + checkoutId.slice(0, 40);
    };
    $$("[data-lang]").forEach(function (b) { b.addEventListener("click", function () { setLang(b.getAttribute("data-lang")); }); });
    setLang(params.get("lang") || "fr");
  }


  // Calculateur MonKiosk : prix selon le nombre de salariés
  var loc = { fr: "fr-FR", en: "en-GB", pt: "pt-PT" }[document.documentElement.lang] || "fr-FR";
  var fmt = function (x) {
    try { return new Intl.NumberFormat(loc, { style: "currency", currency: "EUR", minimumFractionDigits: x % 1 ? 2 : 0 }).format(x); }
    catch (e) { return x.toFixed(2).replace(".", ",") + " €"; }
  };
  $$("[data-calc]").forEach(function (calc) {
    var input = $("input[type=range]", calc);
    var one = calc.getAttribute("data-emp") || "salarié", many = calc.getAttribute("data-emps") || "salariés";
    var update = function () {
      var n = +input.value, word = n > 1 ? many : one;
      $$(".calc-out", calc).forEach(function (el) { el.innerHTML = "<b>" + n + "</b> " + word; });
      $$("[data-base]", calc).forEach(function (card) {
        var t = Math.round((+card.getAttribute("data-base") + n * +card.getAttribute("data-per")) * 100) / 100;
        var total = $("[data-total]", card), num = $("[data-n]", card);
        if (total) total.textContent = fmt(t);
        if (num) { num.textContent = n; if (num.nextSibling) num.nextSibling.textContent = " " + word + " : "; }
      });
    };
    input.addEventListener("input", update);
    update();
  });

  // Pécule Pro : mensuel ou annuel
  $$("[data-billing]").forEach(function (box) {
    var btns = $$("[data-period]", box);
    var show = function (period) {
      btns.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-period") === period ? "true" : "false"); });
      $$("[data-show]", box).forEach(function (el) { el.hidden = el.getAttribute("data-show") !== period; });
    };
    btns.forEach(function (b) { b.addEventListener("click", function () { show(b.getAttribute("data-period")); }); });
    show("month");
  });


  // Vidéo de démo : lecture quand elle est visible, bouton pause
  $$("[data-video]").forEach(function (wrap) {
    var v = $("video", wrap), btn = $(".video-btn", wrap), userPaused = reduce;
    var labels = { fr: ["Mettre la vidéo en pause", "Lire la vidéo"], en: ["Pause the video", "Play the video"], pt: ["Pausar o vídeo", "Reproduzir o vídeo"] }[document.documentElement.lang] || ["Pause", "Play"];
    var sync = function () {
      var paused = v.paused;
      wrap.classList.toggle("paused", paused);
      btn.setAttribute("aria-label", paused ? labels[1] : labels[0]);
    };
    v.addEventListener("play", sync); v.addEventListener("pause", sync);
    btn.addEventListener("click", function () {
      if (v.paused) { userPaused = false; v.play(); } else { userPaused = true; v.pause(); }
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { if (!userPaused) { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); } }
        else v.pause();
      }, { threshold: 0.1 }).observe(wrap);
    }
    sync();
  });


  // Quiz « Quelle formule pour moi ? »
  $$("[data-quiz]").forEach(function (quiz) {
    var steps = $$(".quiz-step", quiz), results = $$(".quiz-result", quiz), bar = $(".quiz-bar b", quiz);
    var input = $("#quiz-n", quiz), answers = {}, cur = 0;
    var one = quiz.getAttribute("data-emp"), many = quiz.getAttribute("data-emps");
    var show = function (i) {
      cur = i;
      steps.forEach(function (st, j) { st.hidden = j !== i; });
      results.forEach(function (r) { r.hidden = true; });
      bar.style.width = ((i + 1) / (steps.length + 1) * 100) + "%";
      var first = steps[i].querySelector("input, .choice, [data-next]");
      if (first && i > 0) first.focus();
    };
    var finish = function () {
      var n = Math.max(1, Math.min(200, Math.round(+input.value || 1)));
      var key = answers.premium ? "premium" : (answers.staff || answers.manage) ? "pro" : "essentiel";
      steps.forEach(function (st) { st.hidden = true; });
      bar.style.width = "100%";
      results.forEach(function (r) {
        var on = r.getAttribute("data-result") === key;
        r.hidden = !on;
        if (on) {
          var t = Math.round((+r.getAttribute("data-base") + n * +r.getAttribute("data-per")) * 100) / 100;
          $("[data-total]", r).textContent = fmt(t);
          $("[data-n]", r).textContent = n;
          $("[data-word]", r).textContent = n > 1 ? many : one;
          $("h3", r).setAttribute("tabindex", "-1"); $("h3", r).focus();
        }
      });
    };
    $$(".num-btn", quiz).forEach(function (b) {
      b.addEventListener("click", function () { input.value = Math.max(1, Math.min(200, (+input.value || 0) + +b.getAttribute("data-delta"))); });
    });
    $$("[data-next]", quiz).forEach(function (b) { b.addEventListener("click", function () { show(cur + 1); }); });
    $$("[data-back]", quiz).forEach(function (b) { b.addEventListener("click", function () { show(cur - 1); }); });
    $$(".choice", quiz).forEach(function (b) {
      b.addEventListener("click", function () {
        answers[b.getAttribute("data-answer")] = b.getAttribute("data-value") === "1";
        if (cur + 1 < steps.length) show(cur + 1); else finish();
      });
    });
    $$("[data-restart]", quiz).forEach(function (b) { b.addEventListener("click", function () { answers = {}; show(0); input.focus(); }); });
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); show(1); } });
  });

  // FAQ deep link: open the targeted question
  if (location.hash) {
    var target = document.getElementById(location.hash.slice(1));
    if (target && target.tagName === "DETAILS") target.open = true;
  }
})();
