/* =========================================================================
   user_vcard_create.js
   - Refactor del JS embebido para trabajar como archivo estático.
   - Usa data-preview-url del HTML en lugar de {% url %}.
   - No requiere jQuery. Compatibilidad con HTMX si está presente.
   ========================================================================= */

// Util: obtiene la URL de preview desde el DOM
function getPreviewURL() {
  // Prioriza el form; fallback a <body data-preview-url="...">
  const form = document.getElementById("editorForm");
  return (
    form?.dataset?.previewUrl ||
    document.body?.dataset?.previewUrl ||
    null
  );
}

// Util: dispara render del preview si hay HTMX y URL
function triggerPreviewWithForm(form) {
  const PREVIEW_URL = getPreviewURL();
  if (!window.htmx || !form || !PREVIEW_URL) return;
  const fd = new FormData(form);
  window.htmx.ajax("POST", PREVIEW_URL, { target: "#preview", values: fd });
}

/* ===========================
   1) Slugify + validación
   =========================== */
(function () {
  const $slug = document.getElementById("slug");
  if (!$slug) return;

  const toSlug = (v) => {
    v = (v || "").toString().toLowerCase();
    v = v.replace(/\s+/g, "-");       // espacios → guiones
    v = v.replace(/[^a-z0-9-]/g, ""); // solo [a-z0-9-]
    v = v.replace(/-+/g, "-");        // guiones repetidos
    v = v.replace(/^-+|-+$/g, "");    // guiones extremos
    return v;
  };

  const applyValidity = () => {
    const ok = $slug.value.length >= 5 && /^[a-z0-9-]+$/.test($slug.value);
    $slug.setCustomValidity(
      ok ? "" : "El slug debe tener al menos 5 caracteres y solo minúsculas, números y guiones."
    );
    // Mensaje local por si no usas endpoint
    const st = document.getElementById("slugStatus");
    if (st && !st.querySelector("[data-local]") && !st.innerHTML.trim()) {
      st.innerHTML = '<span data-local class="badgeStatus">*mínimo 5 caracteres requeridos</span>';
    }
  };

  $slug.addEventListener("input", () => {
    const pos = $slug.selectionStart;
    const before = $slug.value;
    const after = toSlug(before);
    if (before !== after) {
      $slug.value = after;
      $slug.setSelectionRange(Math.min(pos, after.length), Math.min(pos, after.length));
    }
    applyValidity();
  });

  $slug.addEventListener("blur", () => {
    $slug.value = toSlug($slug.value);
    applyValidity();
  });

  $slug.value = toSlug($slug.value);
  applyValidity();
})();

/* =====================================
   2) Menú “+Agregar” de Contactos (clonar templates)
   ===================================== */
(function () {
  const btn  = document.getElementById("contactMenuBtn");
  const list = document.getElementById("contactMenuList");
  const host = document.getElementById("contactList");

  if (!btn || !list || !host) return;

  // Toggle del menú
  btn.addEventListener("click", () => {
    list.hidden = !list.hidden;
  });
  document.addEventListener("click", (e) => {
    if (!list.hidden && !e.target.closest("#contactMenu")) list.hidden = true;
  });

  const getTpl = (type) => {
    const id =
      type === "email"   ? "tpl-contact-email"   :
      type === "address" ? "tpl-contact-address" :
                           "tpl-contact-number";
    const tpl = document.getElementById(id);
    return tpl ? tpl.content.cloneNode(true) : null;
  };

  // Agregar item
  list.addEventListener("click", (e) => {
    const add = e.target.closest("[data-new]");
    if (!add) return;
    const type = add.getAttribute("data-new");
    const frag = getTpl(type);
    if (!frag) return;

    host.appendChild(frag);
    list.hidden = true;

    // Recolecta inputs clonados + repinta preview
    const form = document.getElementById("editorForm");
    if (form && window.htmx) {
      const fd = new FormData(form);
      document.querySelectorAll('#contactList input[name="contact_label[]"]').forEach(i => fd.append("contact_label[]", i.value));
      document.querySelectorAll('#contactList input[name="contact_value[]"]').forEach(i => fd.append("contact_value[]", i.value));
      document.querySelectorAll('#contactList input[name="contact_type[]"]').forEach(i => fd.append("contact_type[]", i.value));
      const PREVIEW_URL = getPreviewURL();
      if (PREVIEW_URL) window.htmx.ajax("POST", PREVIEW_URL, { target: "#preview", values: fd });
    }
  });

  // Eliminar item
  document.addEventListener("click", (e) => {
    const del = e.target.closest("[data-del]");
    if (!del) return;
    const item = del.closest(".contact-item");
    if (!item) return;
    item.remove();

    const form = document.getElementById("editorForm");
    if (form && window.htmx) {
      const fd = new FormData(form);
      document.querySelectorAll('#contactList input[name="contact_label[]"]').forEach(i => fd.append("contact_label[]", i.value));
      document.querySelectorAll('#contactList input[name="contact_value[]"]').forEach(i => fd.append("contact_value[]", i.value));
      document.querySelectorAll('#contactList input[name="contact_type[]"]').forEach(i => fd.append("contact_type[]", i.value));
      const PREVIEW_URL = getPreviewURL();
      if (PREVIEW_URL) window.htmx.ajax("POST", PREVIEW_URL, { target: "#preview", values: fd });
    }
  });
})();

/* =====================================
   3) Carrusel de plantillas + aria-selected
   ===================================== */
(function () {
  const rail = document.getElementById("templateRadios");
  if (!rail) return;
  const step = 320;

  document.querySelectorAll(".tplBtn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const dir = Number(btn.dataset.dir || 1);
      rail.scrollBy({ left: dir * step, behavior: "smooth" });
    });
  });

  rail.addEventListener("change", (e) => {
    if (e.target && e.target.name === "template") {
      rail.querySelectorAll(".tplItem").forEach((l) => {
        const checked = l.querySelector("input")?.checked;
        l.setAttribute("aria-selected", checked ? "true" : "false");
      });
    }
  });
})();

/* ==============================
   4) Accordions (abrir/cerrar)
   ============================== */
function accSetState(head, open) {
  const body = head.parentElement.querySelector(".acc-body");
  const icon = head.querySelector(".acc-icon");
  head.setAttribute("aria-expanded", open ? "true" : "false");
  if (body) body.style.display = open ? "block" : "none";
  if (icon) icon.textContent = open ? "−" : "+";
}
function accInit(root = document) {
  root.querySelectorAll(".acc-head").forEach((head) => {
    if (head.dataset.accInited === "1") return;
    head.dataset.accInited = "1";
    const startOpen = head.getAttribute("aria-expanded") === "true";
    accSetState(head, startOpen);
  });
}
document.addEventListener("DOMContentLoaded", () => accInit(document));
document.addEventListener("click", (e) => {
  const head = e.target.closest(".acc-head");
  if (!head) return;
  e.preventDefault();
  const open = head.getAttribute("aria-expanded") !== "true";
  accSetState(head, open);
});
document.addEventListener("htmx:afterSwap", (evt) => accInit(evt.target || document));

/* ======================================================
   5) Sincronizar template seleccionado → preview HTMX
   ====================================================== */
(function () {
  const hidden = document.getElementById("templateField");
  const form = document.getElementById("editorForm");
  document.querySelectorAll('#templateRadios input[name="template"]').forEach((r) => {
    r.addEventListener("change", () => {
      if (hidden) hidden.value = r.value;
      triggerPreviewWithForm(form);
    });
  });
})();

/* ======================================================
   6) Upload tiles: previsualización inmediata
   ====================================================== */
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-upload-btn]");
  if (!btn) return;
  const form = btn.closest("form.asset-uploader");
  const file = form?.querySelector('input[type="file"].hidden-file');
  if (file) file.click();
});

document.addEventListener("change", (e) => {
  const input = e.target;
  if (!input.matches('form.asset-uploader input[type="file"].hidden-file')) return;

  const form = input.closest("form.asset-uploader");
  const targetSel = form?.getAttribute("hx-target");
  const targetEl = targetSel ? document.querySelector(targetSel) : null;

  if (targetEl && input.files && input.files[0]) {
    const file = input.files[0];
    const url = URL.createObjectURL(file);
    if (file.type.startsWith("image/")) {
      targetEl.innerHTML = `<img class="tile-preview" src="${url}" alt="">`;
    } else if (file.type.startsWith("video/")) {
      targetEl.innerHTML = `<video class="tile-preview" src="${url}" muted loop playsinline></video>`;
    }
  }

  // envía el form para server-side processing (si aplica)
  form?.requestSubmit();
  // limpia el input (permite re-subir el mismo archivo)
  setTimeout(() => { input.value = ""; }, 0);
});

/* ==========================
   7) Colores helpers
   ========================== */
(function () {
  const form = document.getElementById("colorsForm");
  if (!form) return;

  let activeField = form.querySelector(".color-field");
  if (activeField) activeField.classList.add("is-target");

  form.addEventListener("focusin", (e) => {
    const cf = e.target.closest(".color-field");
    if (!cf) return;
    activeField?.classList.remove("is-target");
    activeField = cf;
    activeField.classList.add("is-target");
  });

  const toHex = (v) => {
    if (!v) return "";
    v = v.trim();
    if (/^#[0-9a-fA-F]{6}$/.test(v)) return v.toUpperCase();
    if (/^#[0-9a-fA-F]{3}$/.test(v)) {
      const r = v[1], g = v[2], b = v[3];
      return ("#" + r + r + g + g + b + b).toUpperCase();
    }
    if (/^[0-9a-fA-F]{6}$/.test(v)) return ("#" + v).toUpperCase();
    return v.toUpperCase();
  };

  const applyToField = (cf, hex) => {
    if (!cf) return;
    const hexInp = cf.querySelector(".hex");
    const pick = cf.querySelector(".color-picker");
    const clean = toHex(hex);
    if (hexInp) hexInp.value = clean;
    if (pick) pick.value = clean;
    if (window.htmx) window.htmx.trigger(hexInp || pick, "change");
  };

  form.querySelector("#swatchRow")?.addEventListener("click", (e) => {
    const sw = e.target.closest(".swatch");
    if (!sw) return;
    applyToField(activeField, sw.dataset.color);
  });

  form.addEventListener("input", (e) => {
    const pick = e.target.closest(".color-picker");
    if (!pick) return;
    const cf = pick.closest(".color-field");
    const hexInp = cf.querySelector(".hex");
    if (hexInp) hexInp.value = toHex(pick.value);
  });

  form.addEventListener("change", (e) => {
    const hexInp = e.target.closest(".hex");
    if (!hexInp) return;
    const cf = hexInp.closest(".color-field");
    const pick = cf.querySelector(".color-picker");
    const hv = toHex(hexInp.value);
    hexInp.value = hv;
    if (/^#[0-9A-F]{6}$/.test(hv) && pick) pick.value = hv;
  });
})();

/* ==========================
   8) Copiar URL
   ========================== */
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-copy]");
  if (!btn) return;
  const url = btn.getAttribute("data-copy");
  if (!url) return;
  navigator.clipboard.writeText(url).then(() => {
    btn.classList.add("copied");
    setTimeout(() => btn.classList.remove("copied"), 800);
  });
});

/* =====================================
   9) Guardar (Ctrl/Cmd + S) + botón espejo
   ===================================== */
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
    e.preventDefault();
    document.getElementById("saveBtn")?.click();
  }
});
document.getElementById("saveBtnRight")?.addEventListener("click", () => {
  document.getElementById("saveBtn")?.click();
});

/* ======================================================
   10) Tabs de la izquierda: scroll suave + resaltar activo
   ====================================================== */
(function () {
  const getOffset = () => {
    const v = getComputedStyle(document.documentElement)
      .getPropertyValue("--affix-offset")
      .trim();
    return parseInt(v || "80", 10);
  };

  const tabs = document.querySelectorAll("#editorTabs .tab");
  const sections = [];

  tabs.forEach((tab) => {
    const sel = tab.getAttribute("data-target");
    const el = sel ? document.querySelector(sel) : null;
    if (!el) return;

    sections.push({ tab, el });
    tab.addEventListener("click", () => {
      const head = el.querySelector(".acc-head");
      if (head && head.getAttribute("aria-expanded") !== "true") head.click();

      const top = el.getBoundingClientRect().top + window.scrollY - getOffset();
      window.scrollTo({ top, behavior: "smooth" });
    });
  });

  const observer = new IntersectionObserver(
    (entries) => {
      let best = null;
      entries.forEach((en) => {
        if (!best || en.intersectionRatio > best.intersectionRatio) best = en;
      });
      if (!best) return;
      const idx = sections.findIndex((s) => s.el === best.target);
      if (idx < 0) return;

      tabs.forEach((t) => t.classList.remove("is-active"));
      sections[idx].tab.classList.add("is-active");

      const nav = document.getElementById("editorTabs");
      const active = sections[idx].tab;
      const aRect = active.getBoundingClientRect();
      const nRect = nav.getBoundingClientRect();
      if (aRect.right > nRect.right) nav.scrollBy({ left: aRect.right - nRect.right + 16, behavior: "smooth" });
      if (aRect.left  < nRect.left ) nav.scrollBy({ left: aRect.left  - nRect.left  - 16, behavior: "smooth" });
    },
    { root: null, rootMargin: `-${getOffset() + 8}px 0px -55% 0px`, threshold: [0.25, 0.5, 0.75] }
  );

  sections.forEach(({ el }) => observer.observe(el));
})();

/* ======================================================
   11) Calcular offsets sticky (header + barra de la derecha)
   ====================================================== */
(function () {
  function setOffsets() {
    const globalHeader = document.querySelector(
      'header.sticky, header[style*="position: sticky"], header[style*="position:fixed"]'
    );
    const headerH = globalHeader ? globalHeader.offsetHeight : 0;
    document.documentElement.style.setProperty("--affix-offset", headerH + 8 + "px");

    const dock = document.querySelector(".previewDock");
    const dockH = dock ? dock.offsetHeight : 0;
    document.documentElement.style.setProperty("--previewDock-h", dockH + "px");
  }
  window.addEventListener("load", setOffsets);
  window.addEventListener("resize", setOffsets);
  document.addEventListener("htmx:afterSwap", setOffsets);
})();

/* ======================================================
   12) Enlaces: clonar template y eliminar
   ====================================================== */
(function () {
  const addBtn    = document.getElementById("addLinkBtn");
  const linksList = document.getElementById("linksList");
  const tpl       = document.getElementById("linkItemTemplate");

  function triggerPreview() {
    const form = document.getElementById("editorForm");
    triggerPreviewWithForm(form);
  }

  function createLinkItem() {
    if (!tpl || !linksList) return;
    const frag = tpl.content.cloneNode(true);
    linksList.appendChild(frag);
    const last = linksList.lastElementChild;
    const firstInput = last?.querySelector('input[name="link_url[]"]');
    if (firstInput) firstInput.focus();
    triggerPreview();
  }

  addBtn?.addEventListener("click", createLinkItem);

  document.addEventListener("click", (ev) => {
    const delBtn = ev.target.closest(".link-del, .link-del--inline");
    if (!delBtn) return;
    const item = delBtn.closest(".link-item");
    if (item) {
      item.remove();
      triggerPreview();
    }
  });
})();

/* ======================================================
   13) Redes sociales: clonar template y eliminar
   ====================================================== */
(function () {
  const addBtn = document.getElementById("addSocialBtn");
  const list   = document.getElementById("socialList");
  const tpl    = document.getElementById("socialItemTemplate");

  function triggerPreview() {
    const form = document.getElementById("editorForm");
    triggerPreviewWithForm(form);
  }

  function addItem() {
    if (!tpl || !list) return;
    const frag = tpl.content.cloneNode(true);
    list.appendChild(frag);

    const last = list.lastElementChild;
    const sel  = last?.querySelector('select[name="social_network[]"]');
    if (sel) sel.focus();

    triggerPreview();
  }

  addBtn?.addEventListener("click", addItem);

  document.addEventListener("click", (ev) => {
    const del = ev.target.closest(".badge-del, .badge-del--inline");
    if (!del) return;
    const item = del.closest(".social-item");
    if (item && item.parentElement === list) {
      item.remove();
      triggerPreview();
    }
  });
})();
