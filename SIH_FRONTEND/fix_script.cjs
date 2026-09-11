const fs = require('fs');

function removeScriptTags(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  content = content.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  fs.writeFileSync(filePath, content);
}

removeScriptTags('src/pages/officer/ManufacturerRepeat.tsx');
removeScriptTags('src/pages/officer/Map.tsx');
