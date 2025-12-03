const form = document.getElementById("creative-form");
const statusText = document.getElementById("status-text");
const results = document.getElementById("results");
const downloadBtn = document.getElementById("download-btn");
const submitBtn = document.getElementById("submit-btn");
const copyBlock = document.getElementById("copy-block");
const copyTitle = document.getElementById("copy-title");
const copyCaption = document.getElementById("copy-caption");

const setStatus = (message) => {
  statusText.textContent = message;
};

const base64ToBlob = (base64, mime = "application/octet-stream") => {
  const byteChars = atob(base64);
  const byteNumbers = new Array(byteChars.length);
  for (let i = 0; i < byteChars.length; i += 1) {
    byteNumbers[i] = byteChars.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mime });
};

const renderOutput = ({ copy, posters }) => {
  if (copy?.title || copy?.caption) {
    copyTitle.textContent = copy.title || "Untitled concept";
    copyCaption.textContent = copy.caption || "";
    copyBlock.hidden = false;
  } else {
    copyBlock.hidden = true;
  }

  results.innerHTML = "";
  if (!posters?.length) {
    results.innerHTML = "<p>No posters returned. Try again.</p>";
    return;
  }

  posters.forEach((poster, index) => {
    const card = document.createElement("article");
    card.className = "card-item";

    if (poster.image_data_url) {
      const img = document.createElement("img");
      img.src = poster.image_data_url;
      img.alt = poster.style || Poster ${index + 1};
      card.appendChild(img);
    }

    const meta = document.createElement("p");
    meta.className = "meta";
    meta.textContent = poster.style || "Poster concept";
    card.appendChild(meta);
    results.appendChild(card);
  });
};

const attachZipDownload = (zipBase64) => {
  if (!zipBase64) {
    downloadBtn.hidden = true;
    return;
  }
  const zipBlob = base64ToBlob(zipBase64, "application/zip");
  const url = URL.createObjectURL(zipBlob);
  downloadBtn.hidden = false;
  downloadBtn.textContent = "Download creative ZIP";
  downloadBtn.onclick = () => {
    const a = document.createElement("a");
    a.href = url;
    a.download = "ai_creatives.zip";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Generating copy + posters with Gemini…");
  submitBtn.disabled = true;
  downloadBtn.hidden = true;
  results.innerHTML = "";

  try {
    const formData = new FormData(form);
    const response = await fetch("/api/generate", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.error || "Gemini call failed");
    }

    const payload = await response.json();
    renderOutput(payload);
    attachZipDownload(payload.zip_base64);
    setStatus("Done! ZIP is ready.");
  } catch (error) {
    console.error(error);
    setStatus(Error: ${error.message});
  } finally {
    submitBtn.disabled = false;
  }
});
