const fs = require('fs');

function fixProps(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Fix onclick -> onClick={() => {}}
  content = content.replace(/onclick="[^"]*"/g, 'onClick={() => {}}');
  
  // Fix inline styles
  content = content.replace(/style="([^"]*)"/g, (match, styleString) => {
    let styles = {};
    styleString.split(';').forEach(s => {
      let parts = s.split(':');
      if (parts.length === 2) {
        let key = parts[0].trim().replace(/-([a-z])/g, g => g[1].toUpperCase());
        let val = parts[1].trim();
        styles[key] = val;
      }
    });
    return 'style={' + JSON.stringify(styles) + '}';
  });

  fs.writeFileSync(filePath, content);
}

fixProps('src/pages/officer/ManufacturerRepeat.tsx');
fixProps('src/pages/officer/Map.tsx');
