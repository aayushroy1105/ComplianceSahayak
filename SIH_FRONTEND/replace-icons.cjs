const fs = require('fs');
const path = require('path');

function getRelativePathToUi(filePath) {
  const dir = path.dirname(filePath);
  const uiDir = path.resolve(__dirname, 'src/components/ui');
  let rel = path.relative(dir, uiDir);
  if (!rel.startsWith('.')) {
    rel = './' + rel;
  }
  return rel + '/Icon';
}

function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      processDirectory(fullPath);
    } else if (fullPath.endsWith('.tsx') && fullPath !== path.resolve(__dirname, 'src/components/ui/Icon.tsx')) {
      let content = fs.readFileSync(fullPath, 'utf-8');
      
      const iconRegex = /<span className="material-symbols-outlined([^"]*)">([^<]+)<\/span>/g;
      const iconRegex2 = /<span className={'material-symbols-outlined([^']*)'}>([^<]+)<\/span>/g;
      
      let modified = false;
      
      if (content.match(iconRegex) || content.match(iconRegex2)) {
        content = content.replace(iconRegex, (match, classes, name) => {
          return `<Icon name="${name.trim()}" className="${classes.trim()}" />`;
        });
        
        // Also handle the case where the class is first, wait, it's just 'material-symbols-outlined text-[16px]...'
        // Let's do a more robust regex that catches it anywhere in className
        
        const genericRegex = /<span[^>]*className=["']([^"']*)material-symbols-outlined([^"']*)["'][^>]*>([^<]+)<\/span>/g;
        content = content.replace(genericRegex, (match, before, after, name) => {
          const combinedClasses = `${before} ${after}`.replace(/\s+/g, ' ').trim();
          return `<Icon name="${name.trim()}" className="${combinedClasses}" />`;
        });
        
        // Ensure import is present
        if (!content.includes('import Icon from')) {
          const relPath = getRelativePathToUi(fullPath);
          const importStmt = `import Icon from '${relPath}';\n`;
          
          // insert after the last import
          const lastImportIndex = content.lastIndexOf('import ');
          if (lastImportIndex !== -1) {
            const endOfLine = content.indexOf('\n', lastImportIndex);
            content = content.slice(0, endOfLine + 1) + importStmt + content.slice(endOfLine + 1);
          } else {
            content = importStmt + content;
          }
        }
        modified = true;
      }
      
      if (modified) {
        fs.writeFileSync(fullPath, content);
        console.log(`Updated ${fullPath}`);
      }
    }
  }
}

processDirectory(path.resolve(__dirname, 'src'));
