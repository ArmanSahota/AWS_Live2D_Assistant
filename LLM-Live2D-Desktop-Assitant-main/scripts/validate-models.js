const fs = require('fs');
const path = require('path');

// Find the models root directory
const rootA = path.join(process.cwd(), 'static', 'desktop', 'models');
const root = fs.existsSync(rootA) ? rootA : path.join(process.cwd(), 'models');

if (!fs.existsSync(root)) {
  console.error('No models root found at:', root);
  process.exit(1);
}

const dirs = fs.readdirSync(root, { withFileTypes: true }).filter(d => d.isDirectory());
console.log('Models root:', root);
if (!dirs.length) console.error('No model folders found.');

for (const d of dirs) {
  const dir = path.join(root, d.name);
  const conf = path.join(dir, 'conf.yml');
  const hasConf = fs.existsSync(conf);
  const files = fs.readdirSync(dir);
  const model3 = files.find(f => f.toLowerCase().endsWith('.model3.json'));
  console.log(`- ${d.name}: conf.yml=${hasConf ? 'yes' : 'no'}, model3=${model3 ? model3 : 'none'}`);
}
