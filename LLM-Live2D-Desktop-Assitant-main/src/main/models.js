const fs = require('fs');
const path = require('path');
const { app } = require('electron');

/**
 * @typedef {Object} ModelEntry
 * @property {string} name - The name of the model
 * @property {string} dir - The directory path of the model
 * @property {string} [conf] - Optional path to conf.yml file
 * @property {string} [model3] - Optional path to model3.json file
 */

/**
 * Resolves the root directory for Live2D models
 * @returns {string} The path to the models root directory
 */
function resolveModelsRoot() {
  // in dev we keep models in static/desktop/models
  const devRoot = path.join(app.getAppPath(), 'static', 'desktop', 'models');

  // in prod you must copy models into resources/models (see package.json build config)
  const prodRoot = path.join(process.resourcesPath, 'models');

  return fs.existsSync(prodRoot) ? prodRoot : devRoot;
}

/**
 * Lists all available Live2D models
 * @returns {ModelEntry[]} Array of model entries
 */
function listModels() {
  const root = resolveModelsRoot();
  if (!fs.existsSync(root)) return [];

  const dirs = fs.readdirSync(root, { withFileTypes: true }).filter(d => d.isDirectory());
  const models = [];

  for (const dir of dirs) {
    const dirPath = path.join(root, dir.name);
    const confPath = path.join(dirPath, 'conf.yml');
    const hasConf = fs.existsSync(confPath);

    // fallback: scan for first *.model3.json
    let model3 = undefined;
    if (!hasConf) {
      const files = fs.readdirSync(dirPath);
      const json = files.find(f => f.toLowerCase().endsWith('.model3.json'));
      if (json) model3 = path.join(dirPath, json);
    }

    if (hasConf || model3) {
      models.push({ 
        name: dir.name, 
        dir: dirPath, 
        conf: hasConf ? confPath : undefined, 
        model3 
      });
    }
  }
  return models;
}

/**
 * Finds the default model to use
 * @returns {ModelEntry|undefined} The default model entry or undefined if none found
 */
function findDefaultModel() {
  const all = listModels();
  // prefer folder named "default" else first
  return all.find(m => m.name.toLowerCase() === 'default') || all[0];
}

module.exports = {
  resolveModelsRoot,
  listModels,
  findDefaultModel
};
