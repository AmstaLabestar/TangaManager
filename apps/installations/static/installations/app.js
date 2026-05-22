(function () {
  const form = document.getElementById("installation-form");
  if (!form) return;

  const checklists = JSON.parse(document.getElementById("checklists-data").textContent);
  const screens = Array.from(document.querySelectorAll(".screen"));
  const tabs = Array.from(document.querySelectorAll(".step-tab"));
  const progress = document.getElementById("progress-bar");
  const backButton = document.getElementById("back-button");
  const nextButton = document.getElementById("next-button");
  const submitButton = document.getElementById("submit-button");
  const checklistEl = document.getElementById("checklist");
  const solutionField = document.getElementById("id_solution");
  const checklistField = document.getElementById("id_checklist_statuses");
  const ratingField = document.getElementById("id_note_formation");
  const clientSigField = document.getElementById("id_signature_client_data");
  const techSigField = document.getElementById("id_signature_technicien_data");
  const declaration = document.getElementById("declaration");
  const state = {
    step: 0,
    checklist: [],
    signatures: {
      "client-signature": false,
      "tech-signature": false,
    },
  };

  const labels = {
    1: "Pas du tout compris",
    2: "Peu compris",
    3: "Partiellement maitrise",
    4: "Bien compris",
    5: "Parfaitement autonome",
  };

  function checklistKey(solution) {
    if (solution === "feelback") return "feelback";
    if (solution === "smartcard") return "smartcard";
    return "default";
  }

  function setStep(step) {
    state.step = Math.max(0, Math.min(step, screens.length - 1));
    screens.forEach((screen, index) => {
      screen.classList.toggle("is-active", index === state.step);
    });
    tabs.forEach((tab, index) => {
      tab.classList.toggle("is-active", index === state.step);
    });
    progress.style.width = `${((state.step + 1) / screens.length) * 100}%`;
    backButton.style.visibility = state.step === 0 ? "hidden" : "visible";
    nextButton.classList.toggle("is-hidden", state.step === screens.length - 1);
    submitButton.classList.toggle("is-hidden", state.step !== screens.length - 1);
    updateDeclaration();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function requireValue(id, message) {
    const field = document.getElementById(id);
    if (!field || field.value.trim()) return true;
    field.focus();
    alert(message);
    return false;
  }

  function canLeaveStep() {
    if (state.step === 0) {
      return (
        requireValue("id_client_nom", "Le nom du client est requis.") &&
        requireValue("id_client_contact", "Le contact principal est requis.") &&
        requireValue("id_technicien_nom", "Le nom du technicien est requis.") &&
        requireValue("id_date_installation", "La date est requise.")
      );
    }
    if (state.step === 1) {
      if (!solutionField.value) {
        alert("Selectionnez une solution installee.");
        return false;
      }
      return requireValue("id_numero_serie", "Le numero de serie est requis.");
    }
    if (state.step === 2) {
      if (!ratingField.value) {
        alert("Selectionnez la note de formation client.");
        return false;
      }
    }
    return true;
  }

  function buildChecklist(solution) {
    const items = checklists[checklistKey(solution)] || checklists.default;
    state.checklist = items.map(() => "a_verifier");
    checklistEl.innerHTML = "";
    items.forEach((label, index) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "check-item";
      item.innerHTML = `<span>${label}</span><strong>A verifier</strong>`;
      item.addEventListener("click", () => toggleChecklistItem(item, index));
      checklistEl.appendChild(item);
    });
    syncChecklist();
  }

  function toggleChecklistItem(element, index) {
    const next = {
      a_verifier: "ok",
      ok: "probleme",
      probleme: "a_verifier",
    };
    state.checklist[index] = next[state.checklist[index]];
    element.classList.remove("ok", "probleme");
    element.classList.add(state.checklist[index]);
    element.querySelector("strong").textContent = {
      a_verifier: "A verifier",
      ok: "OK",
      probleme: "Probleme",
    }[state.checklist[index]];
    if (state.checklist[index] === "a_verifier") {
      element.classList.remove("a_verifier");
    }
    syncChecklist();
  }

  function syncChecklist() {
    checklistField.value = JSON.stringify(state.checklist);
  }

  function updateDeclaration() {
    const client = document.getElementById("id_client_nom").value || "le client";
    const contact = document.getElementById("id_client_contact").value || "son representant";
    const tech = document.getElementById("id_technicien_nom").value || "le technicien TANGA";
    const selected = solutionField.options[solutionField.selectedIndex];
    const solution = selected && selected.value ? selected.textContent : "la solution installee";
    declaration.textContent = `${contact} confirme la reception de ${solution} pour ${client}. L'installation a ete testee et presentee par ${tech}.`;
  }

  document.querySelectorAll("[data-solution]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-solution]").forEach((node) => {
        node.classList.remove("is-selected");
      });
      button.classList.add("is-selected");
      solutionField.value = button.dataset.solution;
      buildChecklist(button.dataset.solution);
    });
  });

  document.querySelectorAll("[data-rating]").forEach((button) => {
    button.addEventListener("click", () => {
      const value = button.dataset.rating;
      ratingField.value = value;
      document.querySelectorAll("[data-rating]").forEach((node) => {
        node.classList.toggle("is-selected", Number(node.dataset.rating) <= Number(value));
      });
      document.getElementById("rating-label").textContent = `${value}/5 - ${labels[value]}`;
    });
  });

  function setupSignature(canvasId, field) {
    const canvas = document.getElementById(canvasId);
    const wrapper = canvas.closest(".signature-pad");
    const context = canvas.getContext("2d");
    let drawing = false;
    let last = null;

    context.strokeStyle = "#1f2328";
    context.lineWidth = 3;
    context.lineCap = "round";
    context.lineJoin = "round";

    function position(event) {
      const rect = canvas.getBoundingClientRect();
      const point = event.touches ? event.touches[0] : event;
      return {
        x: (point.clientX - rect.left) * (canvas.width / rect.width),
        y: (point.clientY - rect.top) * (canvas.height / rect.height),
      };
    }

    function start(event) {
      event.preventDefault();
      drawing = true;
      last = position(event);
      wrapper.classList.add("has-ink");
      state.signatures[canvasId] = true;
    }

    function move(event) {
      if (!drawing) return;
      event.preventDefault();
      const current = position(event);
      context.beginPath();
      context.moveTo(last.x, last.y);
      context.lineTo(current.x, current.y);
      context.stroke();
      last = current;
    }

    function stop() {
      if (!drawing) return;
      drawing = false;
      field.value = canvas.toDataURL("image/png");
    }

    canvas.addEventListener("mousedown", start);
    canvas.addEventListener("mousemove", move);
    canvas.addEventListener("mouseup", stop);
    canvas.addEventListener("mouseleave", stop);
    canvas.addEventListener("touchstart", start, { passive: false });
    canvas.addEventListener("touchmove", move, { passive: false });
    canvas.addEventListener("touchend", stop);
  }

  setupSignature("client-signature", clientSigField);
  setupSignature("tech-signature", techSigField);

  document.querySelectorAll("[data-clear]").forEach((button) => {
    button.addEventListener("click", () => {
      const canvas = document.getElementById(button.dataset.clear);
      canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
      canvas.closest(".signature-pad").classList.remove("has-ink");
      state.signatures[button.dataset.clear] = false;
      if (button.dataset.clear === "client-signature") clientSigField.value = "";
      if (button.dataset.clear === "tech-signature") techSigField.value = "";
    });
  });

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = Number(tab.dataset.jump);
      if (target <= state.step || canLeaveStep()) setStep(target);
    });
  });

  backButton.addEventListener("click", () => setStep(state.step - 1));
  nextButton.addEventListener("click", () => {
    if (canLeaveStep()) setStep(state.step + 1);
  });

  form.addEventListener("submit", (event) => {
    syncChecklist();
    if (!state.signatures["client-signature"]) {
      event.preventDefault();
      alert("La signature client est requise.");
      return;
    }
    if (!state.signatures["tech-signature"]) {
      event.preventDefault();
      alert("La signature technicien est requise.");
    }
  });

  buildChecklist(solutionField.value || "presencerh_rfid");
  setStep(0);
})();

