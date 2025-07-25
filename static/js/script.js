const unitSelect = document.querySelector('select[name="unit"]');
const widthInput = document.querySelector('input[name="width"]');
const heightInput = document.querySelector('input[name="height"]');
const fileInput = document.querySelector('input[name="image"]');
const fileNameText = document.getElementById("file-name");
const preview = document.getElementById("preview");
const loader = document.getElementById("loader");
const submitBtn = document.getElementById("submit-btn");

let previousUnit = unitSelect.value;
const DPI = 96;

/**
 * Convert between px, in, and cm units
 */
function convert(value, from, to) {
  if (from === to) return value;

  // Convert to px
  if (from === "in") value *= DPI;
  else if (from === "cm") value = (value / 2.54) * DPI;

  // Convert from px to target
  if (to === "in") return value / DPI;
  else if (to === "cm") return (value / DPI) * 2.54;

  return value;
}

/**
 * Handle unit change — auto convert values
 */
unitSelect.addEventListener("change", () => {
  const newUnit = unitSelect.value;
  const width = parseFloat(widthInput.value);
  const height = parseFloat(heightInput.value);

  if (!isNaN(width) && !isNaN(height)) {
    widthInput.value = convert(width, previousUnit, newUnit).toFixed(2);
    heightInput.value = convert(height, previousUnit, newUnit).toFixed(2);
  }

  previousUnit = newUnit;
});

/**
 * Preview the selected image and show file name
 */
function previewImage(event) {
  const file = event.target.files[0];
  if (file) {
    fileNameText.textContent = `Selected: ${file.name}`;

    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      preview.style.display = "block";

      // Show uploaded image dimensions
      const tempImg = new Image();
      tempImg.onload = () => {
        fileNameText.textContent += ` (${tempImg.width} x ${tempImg.height}px)`;
      };
      tempImg.src = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    preview.style.display = "none";
    fileNameText.textContent = "";
  }
}

/**
 * Show loader and disable button on submit
 */
function showLoader() {
  submitBtn.disabled = true;
  submitBtn.innerText = "Processing...";
  loader.style.display = "block";
}

// Register event listeners
fileInput.addEventListener("change", previewImage);
