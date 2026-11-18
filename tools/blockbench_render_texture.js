/**
 * Blockbench 侧贴图渲染器 —— 由 Blockbench MCP 的 execute_script 调用。
 *
 * 用法（在 Blockbench MCP 里执行）：
 *   1) python3 tools/texture_pipeline.py build tools/texture_spec.json /tmp/payload.json
 *   2) 通过 execute_script 调用本文件（内容读入后 eval），传入 payload 路径与仓库贴图目录
 *
 * 流程：
 *   读 payload JSON -> 为每张贴图建 16x16 canvas -> ImageData 灌像素
 *   -> canvas.toDataURL('image/png') -> Blockbench.writeFile 直接写回仓库 PNG
 *
 * 关键点：PNG 的编码与落盘都由 Blockbench 自己完成，不经过 Python 的 PNG 编码器，
 * 因此这条链路与人工在 Blockbench 里画完再导出的产物完全一致。
 */
(function (params) {
  const payloadPath = params.payloadPath;
  const texDir = params.texDir;
  const dryRun = !!params.dryRun;

  return new Promise((resolve) => {
    Blockbench.readFile(payloadPath, { extensions: ['json'] }, (files) => {
      if (!files || !files.length) {
        return resolve({ error: 'payload not readable: ' + payloadPath });
      }
      let payload;
      try {
        payload = JSON.parse(files[0].content);
      } catch (e) {
        return resolve({ error: 'payload is not valid JSON: ' + e });
      }

      const written = [];
      const failed = [];

      for (const name of Object.keys(payload)) {
        const spec = payload[name];
        try {
          const canvas = document.createElement('canvas');
          canvas.width = spec.width;
          canvas.height = spec.height;
          const ctx = canvas.getContext('2d');
          const img = ctx.createImageData(spec.width, spec.height);
          const d = img.data;
          const src = spec.rgba;
          for (let i = 0; i < src.length && i < d.length; i++) {
            d[i] = src[i];
          }
          ctx.putImageData(img, 0, 0);
          const url = canvas.toDataURL('image/png');
          if (!dryRun) {
            Blockbench.writeFile(texDir + '/' + name + '.png', {
              content: url,
              savetype: 'image',
            });
          }
          written.push(name);
        } catch (e) {
          failed.push(name + ': ' + e);
        }
      }

      resolve({
        written: written.length,
        failed: failed,
        names: written,
        dryRun: dryRun,
      });
    });
  });
});
