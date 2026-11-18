// Run in Blockbench with distribution_box.bbmodel open.
(function () {
  const compiled = Codecs.java_block.compile();
  const model = typeof compiled === 'string' ? JSON.parse(compiled) : compiled;
  // Current Blockbench may emit a newer editor format marker; 1.20.1 uses elements.
  delete model.format_version;
  model.parent = 'minecraft:block/block';
  model.textures.particle = 'minecraft:block/light_gray_concrete';
  Blockbench.writeFile('/www/wwwroot/mcmoddevlop/004/prototypes/distribution_box/distribution_box.json', {
    content: JSON.stringify(model, null, 2), savetype: 'text'
  });
  return {elements: model.elements.length, textures: model.textures, parent: model.parent};
})
