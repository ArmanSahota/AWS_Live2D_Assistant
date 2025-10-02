/**
 * Test script for Electron configuration loading
 * 
 * This script tests the loading of configuration files in the Electron app.
 * It simulates the process of loading configuration files and updating the context menu.
 */

const fs = require('fs');
const path = require('path');

// Simulate the config_alts directory path
const configAltsDir = path.join(__dirname, 'config_alts');

// Function to scan the config_alts directory for YAML files
function scanConfigAltsDirectory() {
  console.log(`Scanning directory: ${configAltsDir}`);
  
  // Check if the directory exists
  if (!fs.existsSync(configAltsDir)) {
    console.error(`Directory does not exist: ${configAltsDir}`);
    return [];
  }
  
  try {
    // Get all files in the directory
    const files = fs.readdirSync(configAltsDir);
    
    // Filter for YAML files
    const yamlFiles = files.filter(file => 
      file.endsWith('.yaml') || file.endsWith('.yml')
    );
    
    console.log(`Found ${yamlFiles.length} YAML files:`);
    yamlFiles.forEach(file => console.log(`- ${file}`));
    
    return yamlFiles;
  } catch (error) {
    console.error(`Error scanning directory: ${error.message}`);
    return [];
  }
}

// Function to read a YAML file
function readYamlFile(filename) {
  const filePath = path.join(configAltsDir, filename);
  console.log(`Reading file: ${filePath}`);
  
  try {
    // Read the file
    const content = fs.readFileSync(filePath, 'utf8');
    console.log(`Successfully read file: ${filename}`);
    console.log(`Content length: ${content.length} characters`);
    console.log(`First 100 characters: ${content.substring(0, 100)}...`);
    
    return content;
  } catch (error) {
    console.error(`Error reading file ${filename}: ${error.message}`);
    return null;
  }
}

// Simulate the context menu update process
function simulateContextMenuUpdate(configFiles) {
  console.log('\nSimulating context menu update with config files:');
  
  if (configFiles.length === 0) {
    console.log('No configuration files found. Context menu would be empty.');
    return;
  }
  
  console.log('Context menu would contain:');
  configFiles.forEach((file, index) => {
    console.log(`${index + 1}. ${file}`);
  });
}

// Main function
function main() {
  console.log('=== Testing Electron Configuration Loading ===\n');
  
  // Scan for configuration files
  const configFiles = scanConfigAltsDirectory();
  
  // Read each configuration file
  console.log('\nReading configuration files:');
  configFiles.forEach(file => {
    const content = readYamlFile(file);
    if (content) {
      console.log(`File ${file} read successfully.`);
    }
  });
  
  // Simulate context menu update
  simulateContextMenuUpdate(configFiles);
}

// Run the main function
main();
