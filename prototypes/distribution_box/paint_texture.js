// Run inside Blockbench. One atlas texel is approximately one model unit.
// This 32px atlas holds a 16px door face, the casing, and shared hardware swatches.
(function () {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 32;
  const ctx = canvas.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  const rect = (x, y, w, h, color) => {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
  };
  rect(0, 0, 32, 32, '#bcc3c5');
  rect(0, 0, 16, 16, '#d5dbdc');
  rect(16, 0, 16, 16, '#abb5b9');
  for (let y = 1; y < 15; y++) {
    for (let x = 1; x < 15; x++) {
      const n = (Math.imul(x + 13, 374761393) ^ Math.imul(y + 71, 668265263)) >>> 0;
      if (n % 7 === 0) rect(x, y, 1, 1, '#d7ddde');
      if (n % 7 === 1) rect(x, y, 1, 1, '#d3d9da');
      if (n % 9 === 0) rect(x + 16, y, 1, 1, '#aeb8bc');
      if (n % 9 === 1) rect(x + 16, y, 1, 1, '#a8b2b6');
    }
  }
  // Folded door edge and a restrained engraved identification strip.
  rect(0, 0, 16, 1, '#e5e9e9');
  rect(0, 1, 1, 14, '#dee3e4');
  rect(15, 1, 1, 15, '#b8c1c4');
  rect(1, 15, 14, 1, '#c0c9cc');
  rect(3, 2, 10, 2, '#aebbbf');
  rect(4, 2, 5, 1, '#60747d');
  rect(10, 2, 2, 1, '#e2e8e9');
  // A rectangular electrical warning sticker reads better than a tiny triangle.
  rect(5, 5, 7, 7, '#ae892b');
  rect(6, 6, 5, 5, '#e4b738');
  const bolt = ['...##', '..##.', '.###.', '..##.', '.##..'];
  bolt.forEach((row, y) => [...row].forEach((pixel, x) => {
    if (pixel === '#') rect(x + 6, y + 6, 1, 1, '#34434a');
  }));
  // Shared 4px hardware regions. Keep the micro-grain low amplitude.
  const colors = ['#39464c', '#586b73', '#73878f', '#ced9dc',
                  '#bdc8cc', '#70a68b', '#ddb33e', '#27353b'];
  colors.forEach((color, i) => rect(i * 4, 16, 4, 4, color));
  rect(0, 20, 32, 12, '#a5afb3');
  rect(0, 24, 16, 1, '#b5bfc3');
  rect(0, 31, 16, 1, '#929fa5');
  const url = canvas.toDataURL('image/png');
  const existing = Texture.all.find(t => t.name === 'distribution_box.png');
  const texture = existing || new Texture({name: 'distribution_box.png', folder: 'block', namespace: 'sheepnpp'});
  texture.fromDataURL(url);
  if (!existing) texture.add();
  Blockbench.writeFile('/www/wwwroot/mcmoddevlop/004/prototypes/distribution_box/distribution_box.png', {
    content: url, savetype: 'image'
  });
  return {uuid: texture.uuid, width: 32, height: 32};
})
