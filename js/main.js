(() => {
  "use strict";

  const header = document.querySelector(".site-header");
  const menuToggle = document.querySelector("[data-menu-toggle]");
  const nav = document.querySelector("[data-site-nav]");
  const backToTop = document.querySelector("[data-back-to-top]");

  const syncScrollState = () => {
    const scrolled = window.scrollY > 18;
    header?.classList.toggle("is-scrolled", scrolled);
    backToTop?.classList.toggle("is-visible", window.scrollY > 500);
  };

  syncScrollState();
  window.addEventListener("scroll", syncScrollState, { passive: true });

  if (menuToggle && nav) {
    menuToggle.addEventListener("click", () => {
      const open = menuToggle.getAttribute("aria-expanded") === "true";
      menuToggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
      document.body.classList.toggle("menu-open", !open);
    });

    nav.addEventListener("click", (event) => {
      if (event.target.closest("a")) {
        menuToggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
        document.body.classList.remove("menu-open");
      }
    });
  }

  document.querySelectorAll("img").forEach((image) => {
    const markMissing = () => image.closest(".image-panel, .insight-image, .hero-frame, .article-cover")?.classList.add("image-missing");
    image.addEventListener("error", markMissing, { once: true });
    if (image.complete && image.naturalWidth === 0) markMissing();
  });

  document.querySelectorAll("[data-faq-button]").forEach((button) => {
    button.addEventListener("click", () => {
      const panelId = button.getAttribute("aria-controls");
      const panel = document.getElementById(panelId);
      if (!panel) return;
      const willOpen = button.getAttribute("aria-expanded") !== "true";
      button.setAttribute("aria-expanded", String(willOpen));
      panel.classList.toggle("is-open", willOpen);
      panel.hidden = !willOpen;
    });
  });

  const insightSearch = document.querySelector("[data-insight-search]");
  const insightCards = [...document.querySelectorAll("[data-insight-card]")];
  const filterButtons = [...document.querySelectorAll("[data-insight-filter]")];
  const emptyState = document.querySelector("[data-insight-empty]");
  let activeCategory = "all";

  const filterInsights = () => {
    const term = (insightSearch?.value || "").trim().toLocaleLowerCase("zh-Hant");
    let visibleCount = 0;
    insightCards.forEach((card) => {
      const matchesTerm = !term || card.textContent.toLocaleLowerCase("zh-Hant").includes(term);
      const matchesCategory = activeCategory === "all" || card.dataset.category === activeCategory;
      const visible = matchesTerm && matchesCategory;
      card.hidden = !visible;
      if (visible) visibleCount += 1;
    });
    emptyState?.classList.toggle("is-visible", visibleCount === 0);
  };

  insightSearch?.addEventListener("input", filterInsights);
  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeCategory = button.dataset.insightFilter || "all";
      filterButtons.forEach((item) => {
        const active = item === button;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-pressed", String(active));
      });
      filterInsights();
    });
  });

  const contactForm = document.querySelector("[data-contact-form]");
  if (contactForm) {
    contactForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const status = contactForm.querySelector("[data-form-status]");
      const required = [...contactForm.querySelectorAll("[required]")];
      const invalid = required.find((field) => !field.value.trim());
      if (invalid) {
        invalid.focus();
        if (status) {
          status.textContent = "請完成所有必填欄位後再整理諮詢內容。";
          status.className = "form-status is-error";
        }
        return;
      }
      if (status) {
        status.textContent = "內容已在瀏覽器端完成檢查。此靜態網站不會上傳資料，請將內容透過研究院公布的官方聯絡管道送出。";
        status.className = "form-status is-success";
      }
      contactForm.reset();
    });
  }

  const progress = document.querySelector("[data-reading-progress]");
  if (progress) {
    const updateProgress = () => {
      const article = document.querySelector(".article-body");
      if (!article) return;
      const start = article.offsetTop - window.innerHeight * 0.2;
      const distance = article.offsetHeight - window.innerHeight * 0.55;
      const percent = Math.min(100, Math.max(0, ((window.scrollY - start) / Math.max(distance, 1)) * 100));
      progress.style.width = `${percent}%`;
    };
    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);
  }

  backToTop?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  const revealItems = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add("is-visible"));
  }
})();
