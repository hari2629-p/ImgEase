const unitSelect = document.querySelector('select[name="unit"]');
const widthInput = document.querySelector('input[name="width"]');
const heightInput = document.querySelector('input[name="height"]');
const fileInput = document.getElementById('file-upload');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileDetails = document.getElementById('file-details');
const preview = document.getElementById('preview');
const previewContainer = document.getElementById('preview-container');
const loader = document.getElementById('loader');
const submitBtn = document.getElementById('submit-btn');
const btnText = document.getElementById('btn-text');
const uploadArea = document.querySelector('.upload-area');

let previousUnit = unitSelect.value;
let originalAspectRatio = 1;
let maintainAspectRatio = true;
const DPI = 96;

/**
 * Convert between px, in, and cm units
 */
function convert(value, from, to) {
  if (from === to) return value;

  // Convert to px first
  if (from === "in") value *= DPI;
  else if (from === "cm") value = (value / 2.54) * DPI;

  // Convert from px to target
  if (to === "in") return value / DPI;
  else if (to === "cm") return (value / DPI) * 2.54;

  return value;
}

/**
 * Handle unit change with smooth conversion
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
 * Format file size for display
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Preview the selected image and show file info
 */
function previewImage(file) {
  if (file) {
    fileName.textContent = file.name;
    fileDetails.textContent = `Size: ${formatFileSize(file.size)}`;
    fileInfo.style.display = 'block';

    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      previewContainer.style.display = 'block';

      // Get and display image dimensions
      const tempImg = new Image();
      tempImg.onload = () => {
        fileDetails.textContent += ` • Dimensions: ${tempImg.width} × ${tempImg.height}px`;

        // Auto-fill dimensions and set aspect ratio
        widthInput.value = tempImg.width;
        heightInput.value = tempImg.height;
        originalAspectRatio = tempImg.width / tempImg.height;
      };
      tempImg.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
}

/**
 * Handle drag and drop functionality
 */
uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
  uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('dragover');

  const files = e.dataTransfer.files;
  if (files.length > 0 && files[0].type.startsWith('image/')) {
    fileInput.files = files;
    previewImage(files[0]);
  }
});

/**
 * Show loader and update UI on form submit
 */
function showLoader() {
  submitBtn.disabled = true;
  btnText.textContent = '⏳ Processing...';
  loader.style.display = 'block';
  return true;
}

/**
 * Handle file input change
 */
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    previewImage(file);
  }
});

/**
 * Maintain aspect ratio when width changes
 */
widthInput.addEventListener('input', () => {
  if (maintainAspectRatio && originalAspectRatio && widthInput.value) {
    const newHeight = Math.round(widthInput.value / originalAspectRatio);
    heightInput.value = newHeight;
  }
});

/**
 * Maintain aspect ratio when height changes
 */
heightInput.addEventListener('input', () => {
  if (maintainAspectRatio && originalAspectRatio && heightInput.value) {
    const newWidth = Math.round(heightInput.value * originalAspectRatio);
    widthInput.value = newWidth;
  }
});

/**
 * Prevent form submission if no file selected
 */
document.querySelector('form').addEventListener('submit', (e) => {
  if (!fileInput.files[0]) {
    e.preventDefault();
    alert('Please select an image file first!');
    return false;
  }
});

/**
 * Reset form function (optional utility)
 */
function resetForm() {
  fileInput.value = '';
  fileInfo.style.display = 'none';
  previewContainer.style.display = 'none';
  widthInput.value = '800';
  heightInput.value = '800';
  submitBtn.disabled = false;
  btnText.textContent = '🚀 Process Image';
  loader.style.display = 'none';
}
