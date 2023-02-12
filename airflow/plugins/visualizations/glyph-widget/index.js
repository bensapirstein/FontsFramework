const slideshow = document.getElementById("slideshow");
const glyphContainer = document.querySelector(".glyph-container");
const glifArray = [
  {
    name: "uni05F4",
    format: 2,
    advance_width: 923,
    unicode: "05F4",
    outline: [
      {
        contour: [
          { x: 207, y: 1015, type: "line" },
          { x: 156, y: 1192, type: "line" },
          { x: 221, y: 1239, type: null },
          { x: 277, y: 1239, type: "qcurve" },
          { x: 339, y: 1239, type: null },
          { x: 410, y: 1173, type: null },
          { x: 412, y: 1076, type: null },
          { x: 393, y: 1022, type: "qcurve" },
          { x: 365, y: 955, type: null },
          { x: 250, y: 753, type: "qcurve" },
          { x: 128, y: 753, type: "line" },
        ],
      },
      {
        contour: [
          { x: 571, y: 1015, type: "line" },
          { x: 520, y: 1192, type: "line" },
          { x: 585, y: 1239, type: null },
          { x: 641, y: 1239, type: "qcurve" },
          { x: 703, y: 1239, type: null },
          { x: 774, y: 1173, type: null },
          { x: 776, y: 1076, type: null },
          { x: 757, y: 1022, type: "qcurve" },
          { x: 729, y: 955, type: null },
          { x: 614, y: 753, type: "qcurve" },
          { x: 492, y: 753, type: "line" },
        ],
      },
    ],
  },
  // Add more .glif files here
];

let currentIndex = 0;

function displayGlyph() {
  const currentGlyph = glifArray[currentIndex];
  let svg = `<svg viewBox="0 0 ${currentGlyph.advance_width} 500">`;

  currentGlyph.outline.forEach((contour) => {
    svg += "<path d='";

    contour.contour.forEach((point, index) => {
        if (point.type === "line") {
            svg += `L ${point.x} ${point.y} `;
          } else if (point.type === "qcurve") {
            const nextPoint = contour.contour[index + 1];
            const controlX = (point.x + nextPoint.x) / 2;
            const controlY = (point.y + nextPoint.y) / 2;
            svg += `Q ${point.x} ${point.y} ${controlX} ${controlY} `;
          } else {
            svg += `M ${point.x} ${point.y} `;
          }
        });
      
        svg += "Z' fill='black' />";
        svg += "</svg>";
      
        glyphContainer.innerHTML = svg;
      });
    }
      
displayGlyph();

setInterval(() => {
currentIndex = (currentIndex + 1) % glifArray.length;
displayGlyph();
}, 2000);
