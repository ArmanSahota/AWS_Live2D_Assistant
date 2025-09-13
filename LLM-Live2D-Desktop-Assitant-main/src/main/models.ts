import fs from 'fs';
import path from 'path';
import { app } from 'electron';

export type ModelEntry = { 
  name: string; 
  dir: string; 
  conf?: string; 
  model3?: string 
};

/**
 * Resolves the root directory for Live2D models
 * @returns The path to the models root directory
 */
export function resolveModelsRoot(): string {
  // in dev we keep models in static/desktop/models
  const devRoot = path.join(app.getAppPath(), 'static', 'desktop', 'models');

  // in prod you must copy models into resources/models (see package.json build config)
  const prodRoot = path.join(process.resourcesPath, 'models');

  return fs.existsSync(prodRoot) ? prodRoot : devRoot;
}

/**
 * Lists all available Live2D models
 * @returns Array of model entries
 */
export function listModels(): ModelEntry[] {
  const root = resolveModelsRoot();
  if (!fs.existsSync(root)) return [];

  try {
    const dirs = fs.readdirSync(root, { withFileTypes: true })
      .filter(d => d.isDirectory());
    
    const models: ModelEntry[] = [];

    for (const dir of dirs) {
      const dirPath = path.join(root, dir.name);
      const confPath = path.join(dirPath, 'conf.yml');
      const hasConf = fs.existsSync(confPath);

      // fallback: scan for first *.model3.json
      let model3: string | undefined = undefined;
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
  } catch (error) {
    console.error('Error listing models:', error);
    return [];
  }
}

/**
 * Finds the default model to use
 * @returns The default model entry or undefined if none found
 */
export function findDefaultModel(): ModelEntry | undefined {
  const all = listModels();
  // prefer folder named "default" else first
  return all.find(m => m.name.toLowerCase() === 'default') || all[0];
}

/**
 * Resolves the model3.json path from a model entry
 * This can either be directly from the model3 property or by parsing the conf.yml
 * @param model The model entry to resolve
 * @returns Promise resolving to the model3.json path or undefined if not found
 */
export async function resolveModel3Path(model: ModelEntry): Promise<string | undefined> {
  // If we already have the model3 path, return it
  if (model.model3) {
    return model.model3;
  }
  
  // If we have a conf.yml, try to parse it
  if (model.conf) {
    try {
      const yaml = require('yaml');
      const confContent = fs.readFileSync(model.conf, 'utf8');
      const config = yaml.parse(confContent);
      
      if (config && config.model3) {
        return path.join(path.dirname(model.conf), config.model3);
      }
    } catch (error) {
      console.error(`Error parsing conf.yml for model ${model.name}:`, error);
    }
  }
  
  return undefined;
}
