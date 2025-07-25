const unitSelect = document.querySelector('select[name="unit"]');
const widthInput = document.querySelector('input[name="width"]');
const heightInput = document.querySelector('input[name="height"]');

let previousUnit = unitSelect.value;
const DPI = 96;

function convert(value, from, to) {
  if (from === to) return value;

  // Convert from `from` to pixels
  if (from === "in") value *= DPI;
  else if (from === "cm") value = (value / 2.54) * DPI;

  // Convert from pixels to `to`
  if (to === "in") return value / DPI;
  else if (to === "cm") return (value / DPI) * 2.54;
  return value;
}

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
